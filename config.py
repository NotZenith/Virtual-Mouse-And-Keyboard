import pyautogui

# Window configuration
WIDTH = 1280
HEIGHT = 720

# Hand Tracking configuration
DETECTION_CONFIDENCE = 0.8

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

# Interaction configuration
CLICK_DISTANCE = 30
CLICK_SLEEP = 0.15

# Colors (BGR)
COLOR_KEYBOARD_BG = (255, 0, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_HOVER = (175, 0, 175)
COLOR_CLICK = (0, 255, 0)
COLOR_CORNER = (255, 0, 255)

# Text Box configuration
TEXT_BOX_POS = (50, 350)
TEXT_BOX_SIZE = (650, 100)
TEXT_BOX_TEXT_POS = (60, 430)

# Mouse configuration
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SMOOTHING = 5
MOUSE_SPEED = 1.5
MOUSE_DEADZONE = 5
GESTURE_COOLDOWN = 0.5
CLICK_THRESHOLD = 30
DRAG_THRESHOLD = 30
SCROLL_THRESHOLD = 40
SCROLL_SPEED = 20

# Region of interest for mouse movement (to allow edge-to-edge coverage)
# We map a smaller rectangle in the camera feed to the full screen
CAM_RECT_MARGIN = 150 
CAM_RECT_X = (CAM_RECT_MARGIN, WIDTH - CAM_RECT_MARGIN)
CAM_RECT_Y = (CAM_RECT_MARGIN, HEIGHT - CAM_RECT_MARGIN)

# Clap detection configuration
CLAP_THRESHOLD = 60
DOUBLE_CLAP_TIME = 0.5 # Seconds
CLAP_COOLDOWN = 0.8

# Mode UI configuration
MODE_INDICATOR_POS = (1000, 50)
COLOR_MODE_TEXT = (0, 255, 255) # Cyan
