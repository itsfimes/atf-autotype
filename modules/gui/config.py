import os
from dataclasses import dataclass
from dotenv import load_dotenv, set_key
from typing import Optional

load_dotenv()


@dataclass
class AppConfig:
    monitor_id: int = 1
    typing_speed: int = 260
    switch_kb_layout: bool = False
    fix_qwerty: bool = True
    api_key: str = ""
    screen_w: int = 1920
    screen_h: int = 1080


@dataclass
class AppConstants:
    WINDOW_WIDTH: int = 700
    WINDOW_HEIGHT: int = 680
    SPEED_MIN: int = 50
    SPEED_MAX: int = 500
    SPEED_DEFAULT: int = 260
    START_DELAY: int = 2
    SLIDE_DELAY: float = 0.2
    PRE_SLIDE_DELAY: float = 0.1
    POST_SLIDE_DELAY: float = 0.1
    WPM_DIVISOR: int = 5


_config_instance: Optional[AppConfig] = None


class ConfigManager:
    
    @classmethod
    def load(cls) -> AppConfig:
        global _config_instance
        if _config_instance is None:
            _config_instance = AppConfig(
                monitor_id=int(os.getenv("MONITOR_ID", 1)),
                typing_speed=int(os.getenv("TYPING_SPEED", 260)),
                switch_kb_layout=os.getenv("SWITCH_KB_LAYOUT_ON_START", "false").lower() == "true",
                fix_qwerty=os.getenv("FIX_QWERTY", "true").lower() == "true",
                api_key=os.getenv("MISTRAL_API_KEY", ""),
                screen_w=int(os.getenv("SCREEN_W", 1920)),
                screen_h=int(os.getenv("SCREEN_H", 1080))
            )
        return _config_instance
    
    @classmethod
    def save(cls, config: AppConfig):
        global _config_instance
        set_key(".env", "MONITOR_ID", str(config.monitor_id))
        set_key(".env", "TYPING_SPEED", str(config.typing_speed))
        set_key(".env", "SWITCH_KB_LAYOUT_ON_START", str(config.switch_kb_layout).lower())
        set_key(".env", "FIX_QWERTY", str(config.fix_qwerty).lower())
        if config.api_key:
            set_key(".env", "MISTRAL_API_KEY", config.api_key)
        _config_instance = config
    
    @classmethod
    def reset(cls):
        global _config_instance
        _config_instance = None
