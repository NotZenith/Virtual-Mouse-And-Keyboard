import pyautogui
import numpy as np
import time

class MouseManager:
    def __init__(self, config):
        self.cfg = config
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        self.px, self.py = 0, 0
        self.dragging, self.scrolling, self.s_start_y = False, False, 0
        self.sw, self.sh = pyautogui.size()
        self.last_click_time = 0
        self.click_cooldown = 0.3

    def update(self, hand, detector):
        lm = hand['lmList']

        move_th = self.cfg.get("CLICK_THRESHOLD") + 40
        click_th = self.cfg.get("CLICK_THRESHOLD")
        
        d_8_12, _, _ = detector.findDistance(lm[8][:2], lm[12][:2], draw=False)
        d_4_8, _, _ = detector.findDistance(lm[4][:2], lm[8][:2], draw=False)
        d_4_12, _, _ = detector.findDistance(lm[4][:2], lm[12][:2], draw=False)
        d_12_16, _, _ = detector.findDistance(lm[12][:2], lm[16][:2], draw=False)

        curr_time = time.time()

        if d_8_12 < click_th and d_12_16 < click_th:
            if not self.scrolling:
                self.scrolling = True
                self.s_start_y = lm[8][1]
            else:
                diff = lm[8][1] - self.s_start_y
                if abs(diff) > 20:
                    scroll_dir = 1 if diff > 0 else -1
                    pyautogui.scroll(scroll_dir * self.cfg.get("SCROLL_SPEED"))
            return
        else:
            self.scrolling = False

        # 2. Click Logic (Thumb + finger)
        if curr_time - self.last_click_time > self.click_cooldown:
            if d_4_8 < click_th: # Left Click
                pyautogui.click(button='left')
                self.last_click_time = curr_time
            elif d_4_12 < click_th: # Right Click
                pyautogui.click(button='right')
                self.last_click_time = curr_time

        # 3. Movement Logic: Index + Middle connected
        if d_8_12 < move_th:
            lx, ly = lm[8][0], lm[8][1]
            margin = self.cfg.get("CAM_RECT_MARGIN")
            
            # Map coordinates to screen resolution
            sx = np.interp(lx, (margin, self.cfg.get("WIDTH")-margin), (0, self.sw))
            sy = np.interp(ly, (margin, self.cfg.get("HEIGHT")-margin), (0, self.sh))
            
            # Linear Interpolation (Smoothing)
            self.px = self.px + (sx - self.px) / self.cfg.get("SMOOTHING")
            self.py = self.py + (sy - self.py) / self.cfg.get("SMOOTHING")
            
            # Final Safety bounds check
            self.px = np.clip(self.px, 0, self.sw)
            self.py = np.clip(self.py, 0, self.sh)
            
            try:
                # Direct cast to int for coordinates
                pyautogui.moveTo(int(self.px), int(self.py))
            except Exception:
                pass
