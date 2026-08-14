import pyautogui
from utils.settings_manager import settings_manager

# Dynamic values from settings_manager
WIDTH = settings_manager.get("WIDTH")
HEIGHT = settings_manager.get("HEIGHT")
DETECTION_CONFIDENCE = settings_manager.get("DETECTION_CONFIDENCE")

# Keyboard Layout
KEYS = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
]

# Button configuration
BUTTON_SIZE = (85, 85)
BUTTON_SPACING = 100
START_X = 50
START_Y = 50

# Colors (BGR)
COLOR_KEYBOARD_BG = (40, 40, 40) # Darker, more modern
COLOR_TEXT = (255, 255, 255)
COLOR_HOVER = (0, 120, 215) # Windows blue
COLOR_CLICK = (0, 153, 0)
COLOR_CORNER = (0, 120, 215)
COLOR_MODE_TEXT = (0, 255, 255)

# UI Settings
TEXT_BOX_POS = (50, 350)
TEXT_BOX_SIZE = (650, 100)
TEXT_BOX_TEXT_POS = (60, 430)
MODE_INDICATOR_POS = (30, 50) # Moved to top left

# Mouse configuration
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SMOOTHING = settings_manager.get("SMOOTHING")
MOUSE_DEADZONE = settings_manager.get("MOUSE_DEADZONE")
GESTURE_COOLDOWN = settings_manager.get("GESTURE_COOLDOWN")
CLICK_THRESHOLD = settings_manager.get("CLICK_THRESHOLD")
DRAG_THRESHOLD = settings_manager.get("DRAG_THRESHOLD")
SCROLL_THRESHOLD = settings_manager.get("SCROLL_THRESHOLD")
SCROLL_SPEED = settings_manager.get("SCROLL_SPEED")

# Region of interest
CAM_RECT_MARGIN = settings_manager.get("CAM_RECT_MARGIN")
CAM_RECT_X = (CAM_RECT_MARGIN, WIDTH - CAM_RECT_MARGIN)
CAM_RECT_Y = (CAM_RECT_MARGIN, HEIGHT - CAM_RECT_MARGIN)

# Clap detection
CLAP_THRESHOLD = 60
DOUBLE_CLAP_TIME = 0.5
CLAP_COOLDOWN = 0.8
