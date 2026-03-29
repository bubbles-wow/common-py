import yaml
import os
import re

from typing import Any

def load_config_as_obj(file_path: str) -> Any:
    def replace_env_vars(data):
        if isinstance(data, dict):
            return {k: replace_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [replace_env_vars(i) for i in data]
        elif isinstance(data, str):
            # Match ${VAR_NAME} or ${VAR_NAME:default_value}
            pattern = re.compile(r'\$\{(?P<var>[^:]+)(?::(?P<default>.*))?\}')
            def replace(match):
                var = match.group('var')
                default = match.group('default')
                return os.environ.get(var, default if default is not None else match.group(0))
            return pattern.sub(replace, data)
        return data

    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        if data is None:
            return {}
        
        data = replace_env_vars(data)
        del data[".template"]
        return data
