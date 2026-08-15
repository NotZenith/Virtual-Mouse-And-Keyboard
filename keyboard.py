import cv2
from pynput.keyboard import Controller, Key

class KeyboardManager:
    def __init__(self, draw_rounded_rect, draw_overlay):
        self.ctrl = Controller()
        self.final_text = ""
        self.hover_btn, self.last_btn, self.anim = None, None, 0
        self.draw_rounded_rect = draw_rounded_rect
        self.draw_overlay = draw_overlay
        self.keys = [["Q","W","E","R","T","Y","U","I","O","P"],
                     ["A","S","D","F","G","H","J","K","L",";"],
                     ["Z","X","C","V","B","N","M",",",".","/"],
                     ["SPACE", "BACK"]]
        self.btns = []
        for i, row in enumerate(self.keys):
            for j, k in enumerate(row):
                w, h = 85, 85
                if k == "SPACE": w = 300
                if k == "BACK": w = 150
                x = 100*j+50
                if i == 3 and k == "BACK": x = 400
                self.btns.append({'pos': [x, 100*i+50], 'text': k, 'size': [w, h]})

    def draw(self, img):
        self.draw_overlay(img, (30, 30), (1050, 420), (20,20,20), 0.3)
        for b in self.btns:
            color = (40,40,40)
            if b == self.hover_btn: color = (0,120,215)
            if b == self.last_btn and self.anim > 0: color = (0,153,0); self.anim -= 1
            self.draw_rounded_rect(img, b['pos'], b['size'], 15, color)
            tx, ty = b['pos'][0]+20, b['pos'][1]+55
            if b['text'] == "SPACE": tx += 80
            cv2.putText(img, b['text'], (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.8 if len(b['text']) > 1 else 1, (255,255,255), 2)
        self.draw_overlay(img, (50, 450), (700, 100), (30,30,30), 0.6)
        cv2.putText(img, self.final_text, (60, 530), cv2.FONT_HERSHEY_PLAIN, 4, (255,255,255), 3)

    def update(self, lm):
        self.hover_btn = None
        if not lm: return
        for b in self.btns:
            x, y = b['pos']
            w, h = b['size']
            if x < lm[8][0] < x + w and y < lm[8][1] < y + h:
                self.hover_btn = b; break

    def on_type(self, state):
        if state == 'start' and self.hover_btn:
            try:
                char = self.hover_btn['text']
                if char == "SPACE":
                    self.ctrl.tap(Key.space)
                    self.final_text += " "
                elif char == "BACK":
                    self.ctrl.tap(Key.backspace)
                    self.final_text = self.final_text[:-1]
                else:
                    self.ctrl.tap(char)
                    self.final_text += char
                self.last_btn, self.anim = self.hover_btn, 5
            except Exception:
                pass
