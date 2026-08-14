import cv2
import numpy as np
import cvzone
import config
from .button import Button
from pynput.keyboard import Controller

class KeyboardManager:
    def __init__(self):
        self.keyboard_controller = Controller()
        self.buttons = []
        self.final_text = ""
        self.current_hover_btn = None
        self._create_buttons()

    def _create_buttons(self):
        for i, row in enumerate(config.KEYS):
            for j, key in enumerate(row):
                pos = [config.BUTTON_SPACING * j + config.START_X, 
                       config.BUTTON_SPACING * i + config.START_Y]
                self.buttons.append(Button(pos, key, config.BUTTON_SIZE))

    def draw_all(self, img):
        overlay = np.zeros_like(img, np.uint8)
        for btn in self.buttons:
            x, y = btn.pos
            w, h = btn.size
            cvzone.cornerRect(overlay, (x, y, w, h), 20, rt=0, colorC=config.COLOR_CORNER)
            cv2.rectangle(overlay, btn.pos, (x + w, y + h), config.COLOR_KEYBOARD_BG, cv2.FILLED)
            cv2.putText(overlay, btn.text, (x + 40, y + 60),
                        cv2.FONT_HERSHEY_PLAIN, 2, config.COLOR_TEXT, 3)

        out = img.copy()
        mask = overlay.astype(bool)
        out[mask] = cv2.addWeighted(img, 0.5, overlay, 0.5, 0)[mask]
        
        tx, ty = config.TEXT_BOX_POS
        tw, th = config.TEXT_BOX_SIZE
        cv2.rectangle(out, (tx, ty), (tx + tw, ty + th), config.COLOR_HOVER, cv2.FILLED)
        cv2.putText(out, self.final_text, config.TEXT_BOX_TEXT_POS,
                    cv2.FONT_HERSHEY_PLAIN, 5, config.COLOR_TEXT, 5)
        
        return out

    def update_hover(self, img, lm_list):
        self.current_hover_btn = None
        if not lm_list:
            return img

        for btn in self.buttons:
            x, y = btn.pos
            w, h = btn.size

            if x < lm_list[8][0] < x + w and y < lm_list[8][1] < y + h:
                self.current_hover_btn = btn
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), config.COLOR_HOVER, cv2.FILLED)
                cv2.putText(img, btn.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, 4, config.COLOR_TEXT, 4)
        return img

    def handle_type(self, state):
        if state == 'start' and self.current_hover_btn:
            self.keyboard_controller.press(self.current_hover_btn.text)
            self.final_text += self.current_hover_btn.text
