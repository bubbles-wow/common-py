from pathlib import Path
from logging.handlers import RotatingFileHandler
from logging import Logger, StreamHandler, root

from .precision_formatter import PrecisionFormatter

class CustomLogger(Logger):
    def __init__(self, name: str, level: int = None) -> None:
        if level is None:
            level = root.level
        super().__init__(name, level)
        self.init_handlers()
        
    def init_handlers(self) -> None:
        if self.handlers:
            return

        console_handler = StreamHandler()
        console_handler.setLevel(self.level)

        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            filename=str(log_dir / f"{self.name}.log"),
            maxBytes=1024 * 1024,
            backupCount=30,
            encoding="utf-8"
        )
        file_handler.setLevel(self.level)

        simple_fmt = PrecisionFormatter("[%(asctime)s][%(levelname)s] (%(code)s): %(message)s")
        console_handler.setFormatter(simple_fmt)
        file_handler.setFormatter(simple_fmt)
        
        self.addHandler(console_handler)
        self.addHandler(file_handler)

    def info(self, code: int, message: str) -> None:
        super().info(message, extra={"code": code})
        
    def error(self, code: int, message: str) -> None:
        super().error(message, extra={"code": code})
        
    def warning(self, code: int, message: str) -> None:
        super().warning(message, extra={"code": code})
        
    def debug(self, code: int, message: str) -> None:
        super().debug(message, extra={"code": code})

    def set_name(self, name: str) -> None:
        self.name = name
        for handler in self.handlers[:]:
            self.removeHandler(handler)
        self.init_handlers()
        
logger = CustomLogger("main")