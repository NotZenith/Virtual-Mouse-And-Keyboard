import pyautogui
import numpy as np

class MouseManager:
    def __init__(self, config):
        self.cfg = config
        pyautogui.FAILSAFE = False
        self.px, self.py = 0, 0
        self.dragging, self.scrolling, self.s_start_y = False, False, 0
        self.sw, self.sh = pyautogui.size()

    def update(self, hand):
        if not self.scrolling:
            lx, ly = hand['lmList'][8][0], hand['lmList'][8][1]
            margin = self.cfg.get("CAM_RECT_MARGIN")
            sx = np.interp(lx, (margin, self.cfg.get("WIDTH")-margin), (0, self.sw))
            sy = np.interp(ly, (margin, self.cfg.get("HEIGHT")-margin), (0, self.sh))
            cx = self.px + (sx - self.px) / self.cfg.get("SMOOTHING")
            cy = self.py + (sy - self.py) / self.cfg.get("SMOOTHING")
            if abs(cx-self.px) > self.cfg.get("MOUSE_DEADZONE") or abs(cy-self.py) > self.cfg.get("MOUSE_DEADZONE"):
                pyautogui.moveTo(self.sw - cx, cy, _pause=False)
                self.px, self.py = cx, cy
        else:
            diff = hand['lmList'][8][1] - self.s_start_y
            if abs(diff) > 20:
                pyautogui.scroll((-1 if diff > 0 else 1) * self.cfg.get("SCROLL_SPEED"))

    def on_left(self, state):
        if state == 'start': pyautogui.mouseDown(); self.dragging = True
        else: pyautogui.mouseUp(); self.dragging = False
    
    def on_right(self, state):
        if state == 'start': pyautogui.rightClick()
    
    def on_scroll(self, state, y=0):
        if state == 'start': self.scrolling, self.s_start_y = True, y
        else: self.scrolling = False
