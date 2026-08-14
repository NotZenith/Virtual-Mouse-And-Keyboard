import cv2
import numpy as np
import pyautogui
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
import json
import os
import time
import math
import logging

# --- Settings & Configuration ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "WIDTH": 1280, "HEIGHT": 720, "DETECTION_CONFIDENCE": 0.8,
    "SMOOTHING": 5, "MOUSE_DEADZONE": 5, "GESTURE_COOLDOWN": 0.5,
    "CLICK_THRESHOLD": 30, "DRAG_THRESHOLD": 30, "SCROLL_THRESHOLD": 40,
    "SCROLL_SPEED": 20, "CAM_RECT_MARGIN": 150, "IS_CALIBRATED": False
}

class Settings:
    def __init__(self):
        self.data = DEFAULT_SETTINGS.copy()
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                self.data.update(json.load(f))
    
    def get(self, key): return self.data.get(key)
    def set(self, key, value):
        self.data[key] = value
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

cfg = Settings()

# --- UI Utilities ---
def draw_rounded_rect(img, pos, size, radius, color, thickness=-1):
    x, y = pos
    w, h = size
    cv2.circle(img, (x + radius, y + radius), radius, color, thickness)
    cv2.circle(img, (x + w - radius, y + radius), radius, color, thickness)
    cv2.circle(img, (x + radius, y + h - radius), radius, color, thickness)
    cv2.circle(img, (x + w - radius, y + h - radius), radius, color, thickness)
    cv2.rectangle(img, (x + radius, y), (x + w - radius, y + h), color, thickness)
    cv2.rectangle(img, (x, y + radius), (x + w, y + h - radius), color, thickness)

def draw_overlay(img, pos, size, color, alpha=0.4, radius=15):
    x, y = pos
    w, h = size
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(img.shape[1], x + w), min(img.shape[0], y + h)
    if x1 < x2 and y1 < y2:
        roi = img[y1:y2, x1:x2]
        overlay = roi.copy()
        draw_rounded_rect(overlay, (x - x1, y - y1), (w, h), radius, color, -1)
        cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)

def draw_text(img, text, pos, font=cv2.FONT_HERSHEY_PLAIN, scale=1.2, color=(255,255,255), thickness=1):
    cv2.putText(img, text, (pos[0]+1, pos[1]+1), font, scale, (0,0,0), thickness)
    cv2.putText(img, text, pos, font, scale, color, thickness)

# --- Core Components ---
class Camera:
    def __init__(self, index=0):
        self.index = index
        self.cap = cv2.VideoCapture(index)
        self.cap.set(3, cfg.get("WIDTH"))
        self.cap.set(4, cfg.get("HEIGHT"))

    def get_frame(self):
        success, img = self.cap.read()
        return img if success else None

    def switch(self):
        self.cap.release()
        self.index = (self.index + 1) % 3
        self.__init__(self.index)

class Gesture:
    def __init__(self, name, cooldown=0.5, callback=None):
        self.name, self.cooldown, self.callback = name, cooldown, callback
        self.last_time, self.is_active = 0, False

    def trigger(self, *args, **kwargs):
        if time.time() - self.last_time > self.cooldown:
            self.last_time = time.time()
            if self.callback: self.callback(*args, **kwargs)
            return True
        return False

class PinchGesture(Gesture):
    def __init__(self, name, f_idx, threshold, h_type='Right', callback=None):
        super().__init__(name, cfg.get("GESTURE_COOLDOWN"), callback)
        self.f_idx, self.threshold, self.h_type = f_idx, threshold, h_type

    def detect(self, hand, detector):
        if hand['type'] != self.h_type: return False
        dist, _, _ = detector.findDistance(4, self.f_idx, draw=False)
        detected = dist < self.threshold
        if detected and not self.is_active:
            if self.trigger(state='start'): self.is_active = True
        elif not detected and self.is_active:
            self.trigger(state='end')
            self.is_active = False
        return detected

class DoubleClapGesture(Gesture):
    def __init__(self, callback=None):
        super().__init__("Double Clap", 0.8, callback)
        self.count, self.last_clap = 0, 0

    def detect(self, hands):
        if len(hands) != 2: return False
        h1, h2 = hands[0]['center'], hands[1]['center']
        dist = math.sqrt((h1[0]-h2[0])**2 + (h1[1]-h2[1])**2)
        curr = time.time()
        if dist < 60:
            if self.count == 0:
                self.count, self.last_clap = 1, curr
                time.sleep(0.1)
            elif self.count == 1:
                if curr - self.last_clap < 0.5:
                    self.count = 0
                    return self.trigger()
                self.count, self.last_clap = 1, curr
        elif self.count == 1 and curr - self.last_clap > 0.5:
            self.count = 0
        return False

# --- Managers ---
class MouseManager:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.px, self.py = 0, 0
        self.dragging, self.scrolling, self.s_start_y = False, False, 0
        self.sw, self.sh = pyautogui.size()

    def update(self, hand):
        if not self.scrolling:
            lx, ly = hand['lmList'][8][0], hand['lmList'][8][1]
            margin = cfg.get("CAM_RECT_MARGIN")
            sx = np.interp(lx, (margin, cfg.get("WIDTH")-margin), (0, self.sw))
            sy = np.interp(ly, (margin, cfg.get("HEIGHT")-margin), (0, self.sh))
            cx = self.px + (sx - self.px) / cfg.get("SMOOTHING")
            cy = self.py + (sy - self.py) / cfg.get("SMOOTHING")
            if abs(cx-self.px) > cfg.get("MOUSE_DEADZONE") or abs(cy-self.py) > cfg.get("MOUSE_DEADZONE"):
                pyautogui.moveTo(self.sw - cx, cy, _pause=False)
                self.px, self.py = cx, cy
        else:
            diff = hand['lmList'][8][1] - self.s_start_y
            if abs(diff) > 20:
                pyautogui.scroll((-1 if diff > 0 else 1) * cfg.get("SCROLL_SPEED"))

    def on_left(self, state):
        if state == 'start': pyautogui.mouseDown(); self.dragging = True
        else: pyautogui.mouseUp(); self.dragging = False
    
    def on_right(self, state):
        if state == 'start': pyautogui.rightClick()
    
    def on_scroll(self, state, y=0):
        if state == 'start': self.scrolling, self.s_start_y = True, y
        else: self.scrolling = False

class KeyboardManager:
    def __init__(self):
        self.ctrl = Controller()
        self.final_text = ""
        self.hover_btn, self.last_btn, self.anim = None, None, 0
        self.keys = [["Q","W","E","R","T","Y","U","I","O","P"],
                     ["A","S","D","F","G","H","J","K","L",";"],
                     ["Z","X","C","V","B","N","M",",",".","/"]]
        self.btns = []
        for i, row in enumerate(self.keys):
            for j, k in enumerate(row):
                self.btns.append({'pos': [100*j+50, 100*i+50], 'text': k, 'size': [85,85]})

    def draw(self, img):
        draw_overlay(img, (30, 30), (1020, 320), (20,20,20), 0.3)
        for b in self.btns:
            color = (40,40,40)
            if b == self.hover_btn: color = (0,120,215)
            if b == self.last_btn and self.anim > 0: color = (0,153,0); self.anim -= 1
            draw_rounded_rect(img, b['pos'], b['size'], 15, color)
            cv2.putText(img, b['text'], (b['pos'][0]+30, b['pos'][1]+55), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2)
        draw_overlay(img, (50, 350), (650, 100), (30,30,30), 0.6)
        cv2.putText(img, self.final_text, (60, 430), cv2.FONT_HERSHEY_PLAIN, 4, (255,255,255), 3)

    def update(self, lm):
        self.hover_btn = None
        if not lm: return
        for b in self.btns:
            if b['pos'][0] < lm[8][0] < b['pos'][0]+b['size'][0] and b['pos'][1] < lm[8][1] < b['pos'][1]+b['size'][1]:
                self.hover_btn = b; break

    def on_type(self, state):
        if state == 'start' and self.hover_btn:
            self.ctrl.press(self.hover_btn['text'])
            self.final_text += self.hover_btn['text']
            self.last_btn, self.anim = self.hover_btn, 5

class App:
    def __init__(self):
        self.cam, self.tracker = Camera(), HandDetector(detectionCon=0.8, maxHands=2)
        self.mouse, self.kb = MouseManager(), KeyboardManager()
        self.kb_active, self.last_g, self.calib_start = False, "None", 0
        self.gestures = [
            DoubleClapGesture(self.toggle_mode),
            PinchGesture("Left Click", 12, cfg.get("CLICK_THRESHOLD"), callback=lambda s: self.handle_g("Left Click", self.mouse.on_left, s)),
            PinchGesture("Right Click", 8, cfg.get("CLICK_THRESHOLD"), callback=lambda s: self.handle_g("Right Click", self.mouse.on_right, s)),
            PinchGesture("Scroll", 20, cfg.get("SCROLL_THRESHOLD"), callback=lambda s: self.handle_g("Scroll", lambda st: self.mouse.on_scroll(st, self.ry), s)),
            PinchGesture("Type", 12, cfg.get("CLICK_THRESHOLD"), 'Left', lambda s: self.handle_g("Type", self.kb.on_type, s))
        ]
        self.prev_t, self.ry = time.time(), 0

    def toggle_mode(self): self.kb_active = not self.kb_active; self.last_g = "Mode Toggle"
    def handle_g(self, n, f, s): 
        if s == 'start': self.last_g = n
        f(s)

    def run(self):
        while True:
            img = self.cam.get_frame()
            if img is None: break
            hands, img = self.tracker.findHands(img, draw=False)
            
            if not cfg.get("IS_CALIBRATED"):
                if len(hands) == 2:
                    if self.calib_start == 0: self.calib_start = time.time()
                    prog = min((time.time()-self.calib_start)/3.0, 1.0)
                    h, w = img.shape[:2]
                    draw_overlay(img, (w//2-210, h//2-40), (420, 100), (30,30,30), 0.7)
                    draw_text(img, "CALIBRATING... HOLD POSE", (w//2-200, h//2-10), scale=1.5, thickness=2)
                    cv2.rectangle(img, (w//2-200, h//2+20), (w//2+200, h//2+50), (100,100,100), -1)
                    cv2.rectangle(img, (w//2-200, h//2+20), (w//2-200+int(400*prog), h//2+50), (0,255,0), -1)
                    if prog >= 1.0:
                        size = (self.tracker.findDistance(hands[0]['lmList'][0], hands[0]['lmList'][9])[0] + 
                                self.tracker.findDistance(hands[1]['lmList'][0], hands[1]['lmList'][9])[0]) / 2
                        th = int(30 * (size/110.0))
                        cfg.set("CLICK_THRESHOLD", th); cfg.set("DRAG_THRESHOLD", th)
                        cfg.set("SCROLL_THRESHOLD", int(40*(size/110.0))); cfg.set("IS_CALIBRATED", True)
                else: self.calib_start = 0
            else:
                for g in self.gestures:
                    if "Clap" in g.name: g.detect(hands, self.tracker)
                    else: [g.detect(h, self.tracker) for h in hands]
                if self.kb_active: self.kb.draw(img)
                for h in hands:
                    if h['type'] == 'Right': self.ry = h['lmList'][8][1]; self.mouse.update(h)
                    elif self.kb_active: self.kb.update(h['lmList'])

            curr = time.time(); fps = int(1/(curr-self.prev_t)); self.prev_t = curr
            draw_overlay(img, (20,20), (300, 250), (50,50,50))
            draw_text(img, "VIRTUAL CONTROL", (40, 60), cv2.FONT_HERSHEY_DUPLEX, 0.8)
            y = 110
            for t, c in [(f"FPS: {fps}", (0,255,0)), (f"MODE: {'KB' if self.kb_active else 'MOUSE'}", (0,255,255)), 
                         (f"CALIB: {'DONE' if cfg.get('IS_CALIBRATED') else '...'}", (255,255,0)), (f"G: {self.last_g}", (255,0,255))]:
                draw_text(img, t, (40, y), color=c); y += 35

            cv2.imshow("Virtual Control", img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            if key == ord('r'): cfg.set("IS_CALIBRATED", False)
            if key == ord('\t'): self.cam.switch()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    App().run()
