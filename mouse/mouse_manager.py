import pyautogui
import config
import numpy as np

class MouseManager:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        self.is_dragging = False
        self.is_scrolling = False
        self.scroll_start_y = 0

    def move_cursor(self, hand):
        lm_list = hand['lmList']
        x_raw, y_raw = lm_list[8][0], lm_list[8][1]

        x_screen = np.interp(x_raw, config.CAM_RECT_X, (0, config.SCREEN_WIDTH))
        y_screen = np.interp(y_raw, config.CAM_RECT_Y, (0, config.SCREEN_HEIGHT))

        self.curr_x = self.prev_x + (x_screen - self.prev_x) / config.SMOOTHING
        self.curr_y = self.prev_y + (y_screen - self.prev_y) / config.SMOOTHING

        if abs(self.curr_x - self.prev_x) > config.MOUSE_DEADZONE or \
           abs(self.curr_y - self.prev_y) > config.MOUSE_DEADZONE:
            pyautogui.moveTo(config.SCREEN_WIDTH - self.curr_x, self.curr_y, _pause=False)
            self.prev_x, self.prev_y = self.curr_x, self.curr_y

    def update(self, hand):
        if not self.is_scrolling:
            self.move_cursor(hand)
        
        if self.is_scrolling:
            diff = hand['lmList'][8][1] - self.scroll_start_y
            if abs(diff) > 20:
                scroll_dir = -1 if diff > 0 else 1
                pyautogui.scroll(scroll_dir * config.SCROLL_SPEED)

    # Callbacks for the Gesture Engine
    def handle_left_click(self, state):
        if state == 'start':
            pyautogui.mouseDown()
            self.is_dragging = True
        elif state == 'end':
            pyautogui.mouseUp()
            self.is_dragging = False

    def handle_right_click(self, state):
        if state == 'start':
            pyautogui.rightClick()

    def handle_scroll(self, state, hand_y=None):
        if state == 'start':
            self.is_scrolling = True
            self.scroll_start_y = hand_y
        elif state == 'end':
            self.is_scrolling = False
