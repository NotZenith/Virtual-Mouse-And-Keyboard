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

        # Acceleration logic (optional but recommended for large screens)
        # We can amplify the movement if it's fast, but smoothing already helps.
        # For simplicity, we stick to smooth mapping first.

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

        # Always update cursor position unless scrolling
        if not self.is_scrolling:
            self.move_cursor(hand)
        
        # Get distances for gestures
        # 4: Thumb tip, 8: Index tip, 12: Middle tip, 20: Pinky tip
        dist_ti, _, _ = detector.findDistance(4, 8, draw=False)  # Thumb-Index
        dist_tm, _, _ = detector.findDistance(4, 12, draw=False) # Thumb-Middle
        dist_tp, _, _ = detector.findDistance(4, 20, draw=False) # Thumb-Pinky

        curr_time = time.time()

        # 1. Scroll Mode (Thumb + Pinky) - Priority
        if dist_tp < config.SCROLL_THRESHOLD:
            if not self.is_scrolling:
                self.is_scrolling = True
                self.scroll_start_y = hand['lmList'][8][1]
            else:
                diff = hand['lmList'][8][1] - self.scroll_start_y
                if abs(diff) > 20:
                    scroll_dir = -1 if diff > 0 else 1
                    pyautogui.scroll(scroll_dir * config.SCROLL_SPEED)
            return # Exit early in scroll mode
        else:
            self.is_scrolling = False

        # 2. Left Click / Drag (Thumb + Middle)
        if dist_tm < config.CLICK_THRESHOLD:
            if not self.is_dragging:
                # One-shot click if released quickly, but here we handle hold for drag
                if curr_time - self.last_gesture_time > config.GESTURE_COOLDOWN:
                    pyautogui.mouseDown()
                    self.is_dragging = True
                    self.last_gesture_time = curr_time
        else:
            if self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False
                self.last_gesture_time = curr_time

        # 3. Right Click (Thumb + Index)
        if dist_ti < config.CLICK_THRESHOLD:
            if curr_time - self.last_gesture_time > config.GESTURE_COOLDOWN:
                pyautogui.rightClick()
                self.last_gesture_time = curr_time
