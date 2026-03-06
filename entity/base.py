import json

from dataclasses import dataclass, fields, is_dataclass, MISSING
from typing import Any, Type, TypeVar, Dict, Union, get_origin, get_args

T = TypeVar('T', bound='BaseEntity')

@dataclass
class BaseEntity:
    @classmethod
    def from_any(cls: Type[T], data: Any) -> T:
        if data is None:
            init_data = {}
            for f in fields(cls):
                if f.default is not MISSING:
                    init_data[f.name] = f.default
                elif f.default_factory is not MISSING:
                    init_data[f.name] = f.default_factory()
                else:
                    init_data[f.name] = 0 if f.type is int else None
            return cls(**init_data)

        if not isinstance(data, dict):
            try:
                config_dict = vars(data)
            except TypeError:
                config_dict = {f.name: getattr(data, f.name, None) for f in fields(cls)}
        else:
            config_dict = data

        def _convert(target_type: Any, value: Any) -> Any:
            if value is None:
                return None
            
            origin = get_origin(target_type) or target_type
            args = get_args(target_type)
            
            if isinstance(origin, type) and issubclass(origin, BaseEntity):
                return origin.from_any(value)
            
            if origin is list and isinstance(value, list):
                item_type = args[0] if args else Any
                return [_convert(item_type, i) for i in value]
            
            if origin is dict and isinstance(value, dict):
                item_type = args[1] if len(args) > 1 else Any
                return {k: _convert(item_type, v) for k, v in value.items()}
            
            try:
                if origin is int: return int(value)
                if origin is str: return str(value)
                if origin is float: return float(value)
                if origin is bool:
                    if isinstance(value, str):
                        return value.lower() in ('true', '1', 'yes')
                    return bool(value)
            except (ValueError, TypeError):
                pass
            return value

        init_data = {}
        for field in fields(cls):
            val = config_dict.get(field.name)
            
            origin_type = get_origin(field.type)
            actual_types = get_args(field.type) if origin_type is Union else (field.type,)
            
            base_type = next((t for t in actual_types if t is not type(None)), field.type)
            base_origin = get_origin(base_type) or base_type

            if val is None:
                if field.default is not MISSING:
                    val = field.default
                elif field.default_factory is not MISSING:
                    val = field.default_factory()
                elif base_origin is int:
                    val = 0
                elif base_origin is str:
                    val = ""
                elif base_origin is list:
                    val = []
                elif base_origin is dict:
                    val = {}
                else:
                    val = None
            else:
                if not isinstance(val, (dict, list, str, int, float, bool)) and hasattr(val, "__dict__"):
                    def to_dict(o):
                        if hasattr(o, "__dict__"):
                            return {k: to_dict(v) for k, v in vars(o).items()}
                        elif isinstance(o, list):
                            return [to_dict(i) for i in o]
                        return o
                    val = to_dict(val)

                val = _convert(base_type, val)
            
            init_data[field.name] = val

        return cls(**init_data)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            result[field.name] = self._serialize_value(value)
        return result

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, BaseEntity):
            return value.to_dict()
        elif is_dataclass(value):
            from dataclasses import asdict
            return asdict(value)
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(',', ':'), ensure_ascii=False)
