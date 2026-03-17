"""
Randevu Sistemi - Sound Manager
Audio feedback system using PyQt6 QSoundEffect
"""

from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from pathlib import Path
from config import Sounds


class SoundManager:
    """Manages sound effects for the application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._sounds = {}
        self._enabled = True
        self._volume = 0.7
        
        self._load_sounds()
    
    def _load_sounds(self):
        """Preload all sound effects"""
        sound_mapping = {
            "button": Sounds.BUTTON,
            "caution": Sounds.CAUTION,
            "celebration": Sounds.CELEBRATION,
            "disabled": Sounds.DISABLED,
            "notification": Sounds.NOTIFICATION,
            "progress": Sounds.PROGRESS_LOOP,
            "ringtone": Sounds.RINGTONE_LOOP,
            "select": Sounds.SELECT,
            "swipe": Sounds.SWIPE,
            "tap": Sounds.TAP_01,
            "toggle_on": Sounds.TOGGLE_ON,
            "toggle_off": Sounds.TOGGLE_OFF,
            "transition_down": Sounds.TRANSITION_DOWN,
            "transition_up": Sounds.TRANSITION_UP,
            "type": Sounds.TYPE_01,
        }
        
        for name, path in sound_mapping.items():
            if path.exists():
                sound = QSoundEffect()
                sound.setSource(QUrl.fromLocalFile(str(path)))
                sound.setVolume(self._volume)
                sound.setLoopCount(1)
                self._sounds[name] = sound
    
    def play(self, sound_name: str):
        """Play a sound by name"""
        if not self._enabled:
            return
        
        sound = self._sounds.get(sound_name)
        if sound:
            sound.play()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sounds"""
        self._enabled = enabled
    
    def set_volume(self, volume: float):
        """Set volume (0.0 - 1.0)"""
        self._volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            sound.setVolume(self._volume)
    
    # Convenience methods
    def play_button(self):
        self.play("button")
    
    def play_caution(self):
        self.play("caution")
    
    def play_celebration(self):
        self.play("celebration")
    
    def play_disabled(self):
        self.play("disabled")
    
    def play_notification(self):
        self.play("notification")
    
    def play_select(self):
        self.play("select")
    
    def play_swipe(self):
        self.play("swipe")
    
    def play_tap(self):
        self.play("tap")
    
    def play_toggle_on(self):
        self.play("toggle_on")
    
    def play_toggle_off(self):
        self.play("toggle_off")
    
    def play_transition_down(self):
        self.play("transition_down")
    
    def play_transition_up(self):
        self.play("transition_up")
    
    def play_type(self):
        self.play("type")
    
    def play_ringtone(self):
        """Play ringtone for new appointments - loops 3 times"""
        if not self._enabled:
            return
        sound = self._sounds.get("ringtone")
        if sound:
            sound.setLoopCount(3)  # Loop 3 times for attention
            sound.play()


# Global instance
_sound_manager = None


def get_sound_manager() -> SoundManager:
    """Get the global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager
