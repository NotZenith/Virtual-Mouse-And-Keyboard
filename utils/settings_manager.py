import json
import os
from utils.logger import logger

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "WIDTH": 1280,
    "HEIGHT": 720,
    "DETECTION_CONFIDENCE": 0.8,
    "SMOOTHING": 5,
    "MOUSE_SPEED": 1.5,
    "MOUSE_DEADZONE": 5,
    "GESTURE_COOLDOWN": 0.5,
    "CLICK_THRESHOLD": 30,
    "DRAG_THRESHOLD": 30,
    "SCROLL_THRESHOLD": 40,
    "SCROLL_SPEED": 20,
    "KEYBOARD_SCALE": 1.0,
    "KEYBOARD_VISIBLE": True,
    "CAM_RECT_MARGIN": 150
}

class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
                logger.info("Settings loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
        else:
            self.save_settings()

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Settings saved successfully.")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

settings_manager = SettingsManager()
