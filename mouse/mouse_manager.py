import pyautogui
import config
import numpy as np
import time

class MouseManager:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        self.last_gesture_time = 0
        self.is_dragging = False
        self.is_scrolling = False
        self.scroll_start_y = 0

    def move_cursor(self, hand):
        lm_list = hand['lmList']
        # Use index fingertip (landmark 8)
        x_raw, y_raw = lm_list[8][0], lm_list[8][1]

        # Map camera coordinates to screen coordinates with margins
        x_screen = np.interp(x_raw, config.CAM_RECT_X, (0, config.SCREEN_WIDTH))
        y_screen = np.interp(y_raw, config.CAM_RECT_Y, (0, config.SCREEN_HEIGHT))

        # Exponential smoothing
        self.curr_x = self.prev_x + (x_screen - self.prev_x) / config.SMOOTHING
        self.curr_y = self.prev_y + (y_screen - self.prev_y) / config.SMOOTHING

        # Deadzone to prevent shaking
        if abs(self.curr_x - self.prev_x) > config.MOUSE_DEADZONE or \
           abs(self.curr_y - self.prev_y) > config.MOUSE_DEADZONE:
            pyautogui.moveTo(config.SCREEN_WIDTH - self.curr_x, self.curr_y, _pause=False)
            self.prev_x, self.prev_y = self.curr_x, self.curr_y

    def update(self, hand, detector):
        if hand['type'] != 'Right':
            return

        # Always update cursor position unless scrolling (optional, but requested smooth movement)
        if not self.is_scrolling:
            self.move_cursor(hand)
        
        # Gestures will be added in next steps
