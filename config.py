"""
Randevu Sistemi - Configuration
Central configuration for the appointment system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def get_base_dir() -> Path:
    """Get base directory (works with PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent


BASE_DIR = get_base_dir()
SOUND_PACK_DIR = BASE_DIR / "SND01-sine-sound-pack"

# Load .env file from base directory
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    # Try loading from current working directory
    load_dotenv()


class Sounds:
    """Sound file paths"""
    BUTTON = SOUND_PACK_DIR / "button.wav"
    CAUTION = SOUND_PACK_DIR / "caution.wav"
    CELEBRATION = SOUND_PACK_DIR / "celebration.wav"
    DISABLED = SOUND_PACK_DIR / "disabled.wav"
    NOTIFICATION = SOUND_PACK_DIR / "notification.wav"
    PROGRESS_LOOP = SOUND_PACK_DIR / "progress_loop.wav"
    RINGTONE_LOOP = SOUND_PACK_DIR / "ringtone_loop.wav"
    SELECT = SOUND_PACK_DIR / "select.wav"
    SWIPE = SOUND_PACK_DIR / "swipe.wav"
    TAP_01 = SOUND_PACK_DIR / "tap_01.wav"
    TAP_02 = SOUND_PACK_DIR / "tap_02.wav"
    TAP_03 = SOUND_PACK_DIR / "tap_03.wav"
    TOGGLE_ON = SOUND_PACK_DIR / "toggle_on.wav"
    TOGGLE_OFF = SOUND_PACK_DIR / "toggle_off.wav"
    TRANSITION_DOWN = SOUND_PACK_DIR / "transition_down.wav"
    TRANSITION_UP = SOUND_PACK_DIR / "transition_up.wav"
    TYPE_01 = SOUND_PACK_DIR / "type_01.wav"


class AppConfig:
    """Application configuration"""
    APP_NAME = "Randevu Sistemi Pro"
    APP_VERSION = "1.0.0"
    
    # Supabase Configuration from .env
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-key-here")
    
    # Colors (Modern Dark Theme)
    PRIMARY_COLOR = "#6366F1"  # Indigo
    SECONDARY_COLOR = "#8B5CF6"  # Purple
    SUCCESS_COLOR = "#10B981"  # Emerald
    WARNING_COLOR = "#F59E0B"  # Amber
    DANGER_COLOR = "#EF4444"  # Red
    INFO_COLOR = "#3B82F6"  # Blue
    
    # Background colors
    BG_DARK = "#0F172A"  # Slate 900
    BG_CARD = "#1E293B"  # Slate 800
    BG_INPUT = "#334155"  # Slate 700
    
    # Text colors
    TEXT_PRIMARY = "#F8FAFC"  # Slate 50
    TEXT_SECONDARY = "#94A3B8"  # Slate 400
    TEXT_MUTED = "#64748B"  # Slate 500
    
    # Border radius
    BORDER_RADIUS = "12px"
    BORDER_RADIUS_SM = "8px"
    BORDER_RADIUS_LG = "16px"
    
    # Shadow
    SHADOW = "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)"
    
    @classmethod
    def get_env_path(cls) -> Path:
        """Get .env file path"""
        return get_base_dir() / ".env"
    
    @classmethod
    def save_env(cls, url: str, key: str):
        """Save Supabase configuration to .env file"""
        env_path = cls.get_env_path()
        
        content = f"""# Randevu Sistemi Pro - Supabase Configuration
# BU DOSYAYI GÜVENLİ BİR YERDE SAKLAYIN!

SUPABASE_URL={url}
SUPABASE_KEY={key}
"""
        env_path.write_text(content, encoding="utf-8")
        
        # Reload environment variables
        load_dotenv(env_path, override=True)
        
        # Update class attributes
        cls.SUPABASE_URL = url
        cls.SUPABASE_KEY = key
