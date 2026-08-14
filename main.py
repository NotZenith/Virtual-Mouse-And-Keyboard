import cv2
import numpy as np
import os
import json
import time
import logging
from camera import Camera
from cvzone.HandTrackingModule import HandDetector
from engine import DoubleClapGesture, PinchGesture
from mouse import MouseManager
from keyboard import KeyboardManager

# --- Settings ---
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

# --- UI Utils ---
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

# --- App ---
class App:
    def __init__(self):
        self.cam = Camera(width=cfg.get("WIDTH"), height=cfg.get("HEIGHT"))
        self.tracker = HandDetector(detectionCon=cfg.get("DETECTION_CONFIDENCE"), maxHands=2)
        self.mouse = MouseManager(cfg)
        self.kb = KeyboardManager(draw_rounded_rect, draw_overlay)
        self.kb_active, self.last_g, self.calib_start = False, "None", 0
        self.ry = 0
        self.gestures = [
            DoubleClapGesture(self.toggle_mode),
            PinchGesture("Left Click", 12, cfg.get("CLICK_THRESHOLD"), callback=lambda s: self.handle_g("Left Click", self.mouse.on_left, s)),
            PinchGesture("Right Click", 8, cfg.get("CLICK_THRESHOLD"), callback=lambda s: self.handle_g("Right Click", self.mouse.on_right, s)),
            PinchGesture("Scroll", 20, cfg.get("SCROLL_THRESHOLD"), callback=lambda s: self.handle_g("Scroll", lambda st: self.mouse.on_scroll(st, self.ry), s)),
            PinchGesture("Type", 12, cfg.get("CLICK_THRESHOLD"), 'Left', lambda s: self.handle_g("Type", self.kb.on_type, s))
        ]
        self.prev_t = time.time()

    def toggle_mode(self): self.kb_active = not self.kb_active; self.last_g = "Mode Toggle"
    def handle_g(self, n, f, s): 
        if s == 'start': self.last_g = n
        f(s)

    def run(self):
        while True:
            img = self.cam.get_frame()
            if img is None: break
            
            # Let cvzone handle the mirroring and flip logic automatically
            hands, img = self.tracker.findHands(img, draw=True, flipType=True) 
            
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
                        size = (self.tracker.findDistance(hands[0]['lmList'][0][:2], hands[0]['lmList'][9][:2])[0] + 
                                self.tracker.findDistance(hands[1]['lmList'][0][:2], hands[1]['lmList'][9][:2])[0]) / 2
                        th = int(30 * (size/110.0))
                        cfg.set("CLICK_THRESHOLD", th); cfg.set("DRAG_THRESHOLD", th)
                        cfg.set("SCROLL_THRESHOLD", int(40*(size/110.0))); cfg.set("IS_CALIBRATED", True)
                else: self.calib_start = 0
            else:
                for g in self.gestures:
                    if "Clap" in g.name: g.detect(hands)
                    else: [g.detect(h, self.tracker) for h in hands]
                if self.kb_active: self.kb.draw(img)
                for h in hands:
                    # Debug: Show EVERY detected hand's type and distance
                    d_8_12 = int(self.tracker.findDistance(h['lmList'][8][:2], h['lmList'][12][:2])[0])
                    label = f"{h['type']} (D:{d_8_12})"
                    cv2.putText(img, label, (h['lmList'][0][0], h['lmList'][0][1]-20),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                    # Allow any hand to control the mouse for now to fix the "not working" issue
                    # We can restrict it back to 'Right' once we see what the labels are doing
                    self.ry = h['lmList'][8][1]
                    self.mouse.update(h, self.tracker)
                    
                    if self.kb_active and h['type'] == 'Left':
                        self.kb.update(h['lmList'])

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
