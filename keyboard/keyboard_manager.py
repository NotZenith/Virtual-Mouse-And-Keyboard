import cv2
import numpy as np
import config
from .button import Button
from pynput.keyboard import Controller
from utils.ui_utils import draw_rounded_rect, draw_transparent_overlay

class KeyboardManager:
    def __init__(self):
        self.keyboard_controller = Controller()
        self.buttons = []
        self.final_text = ""
        self.current_hover_btn = None
        self.last_pressed_btn = None
        self.press_animation_timer = 0
        self._create_buttons()

    def _create_buttons(self):
        for i, row in enumerate(config.KEYS):
            for j, key in enumerate(row):
                pos = [config.BUTTON_SPACING * j + config.START_X, 
                       config.BUTTON_SPACING * i + config.START_Y]
                self.buttons.append(Button(pos, key, config.BUTTON_SIZE))

    def draw_all(self, img):
        # 1. Draw main translucent panel
        draw_transparent_overlay(img, (config.START_X - 20, config.START_Y - 20), 
                                (1020, 320), (20, 20, 20), alpha=0.3, radius=20)

        # 2. Draw buttons
        for btn in self.buttons:
            color = config.COLOR_KEYBOARD_BG
            if btn == self.current_hover_btn:
                color = config.COLOR_HOVER
            if btn == self.last_pressed_btn and self.press_animation_timer > 0:
                color = config.COLOR_CLICK
                self.press_animation_timer -= 1
            
            draw_rounded_rect(img, btn.pos, btn.size, 15, color, -1)
            cv2.putText(img, btn.text, (btn.pos[0] + 30, btn.pos[1] + 55),
                        cv2.FONT_HERSHEY_DUPLEX, 1, config.COLOR_TEXT, 2)

        # 3. Draw text output box
        tx, ty = config.TEXT_BOX_POS
        tw, th = config.TEXT_BOX_SIZE
        draw_transparent_overlay(img, (tx, ty), (tw, th), (30, 30, 30), alpha=0.6, radius=15)
        cv2.putText(img, self.final_text, config.TEXT_BOX_TEXT_POS,
                    cv2.FONT_HERSHEY_PLAIN, 4, config.COLOR_TEXT, 3)
        
        return img

    def update_hover(self, img, lm_list):
        self.current_hover_btn = None
        if not lm_list:
            return img

        for btn in self.buttons:
            x, y = btn.pos
            w, h = btn.size
            if x < lm_list[8][0] < x + w and y < lm_list[8][1] < y + h:
                self.current_hover_btn = btn
                break # Optimization: stop once found
        return img

    def handle_type(self, state):
        if state == 'start' and self.current_hover_btn:
            self.keyboard_controller.press(self.current_hover_btn.text)
            self.final_text += self.current_hover_btn.text
            self.last_pressed_btn = self.current_hover_btn
            self.press_animation_timer = 5
