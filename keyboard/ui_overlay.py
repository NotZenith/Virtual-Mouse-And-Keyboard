import cv2
import time
import config
from utils.ui_utils import draw_transparent_overlay, draw_text_with_shadow

class UIOverlay:
    def __init__(self):
        self.prev_time = time.time()
        self.fps = 0

    def draw(self, img, mode, calibration_status, last_gesture):
        curr_time = time.time()
        self.fps = 1 / (curr_time - self.prev_time)
        self.prev_time = curr_time

        # Draw Side Dashboard (Glassmorphism style)
        panel_pos = (20, 20)
        panel_size = (300, 250)
        draw_transparent_overlay(img, panel_pos, panel_size, (50, 50, 50), alpha=0.4)

        # Draw Title
        draw_text_with_shadow(img, "VIRTUAL CONTROL", (40, 60), 
                              cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        
        # Info list
        y_offset = 110
        info = [
            (f"FPS: {int(self.fps)}", (0, 255, 0)),
            (f"MODE: {mode}", config.COLOR_MODE_TEXT),
            (f"CALIB: {calibration_status}", (255, 255, 0)),
            (f"LAST GESTURE: {last_gesture}", (255, 0, 255))
        ]

        for text, color in info:
            draw_text_with_shadow(img, text, (40, y_offset), 
                                  cv2.FONT_HERSHEY_PLAIN, 1.2, color, 1)
            y_offset += 35

    def draw_calibration_progress(self, img, progress):
        h, w = img.shape[:2]
        bar_w = 400
        bar_h = 30
        x = (w - bar_w) // 2
        y = (h - bar_h) // 2
        
        draw_transparent_overlay(img, (x-10, y-40), (bar_w+20, 100), (30, 30, 30), alpha=0.7)
        draw_text_with_shadow(img, "CALIBRATING... HOLD POSE", (x, y-10), 
                              cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
        
        # Progress bar background
        cv2.rectangle(img, (x, y+20), (x+bar_w, y+bar_h+20), (100, 100, 100), cv2.FILLED)
        # Progress bar fill
        cv2.rectangle(img, (x, y+20), (x+int(bar_w*progress), y+bar_h+20), (0, 255, 0), cv2.FILLED)
