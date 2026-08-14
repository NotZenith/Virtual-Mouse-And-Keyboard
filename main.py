import cv2
import config
from camera import Camera
from hand_tracker import HandTracker
from keyboard.keyboard_manager import KeyboardManager
from mouse.mouse_manager import MouseManager
from gestures.engine import GestureEngine
from gestures.pinch_gesture import PinchGesture
from gestures.clap_gesture import DoubleClapGesture
from utils.logger import logger

class App:
    def __init__(self):
        self.cam = Camera()
        self.tracker = HandTracker()
        self.kb_manager = KeyboardManager()
        self.mouse_manager = MouseManager()
        self.engine = GestureEngine()
        self.keyboard_mode_active = False
        self._setup_gestures()

    def _setup_gestures(self):
        # Mode Toggle
        self.engine.add_gesture(DoubleClapGesture(callback=self.toggle_mode))
        
        # Mouse Gestures (Right Hand)
        self.engine.add_gesture(PinchGesture("Left Click", 12, config.CLICK_THRESHOLD, 
                                             callback=self.mouse_manager.handle_left_click))
        self.engine.add_gesture(PinchGesture("Right Click", 8, config.CLICK_THRESHOLD, 
                                             callback=self.mouse_manager.handle_right_click))
        self.engine.add_gesture(PinchGesture("Scroll", 20, config.SCROLL_THRESHOLD, 
                                             callback=lambda state: self.mouse_manager.handle_scroll(state, self.last_right_hand_y)))

        # Keyboard Gesture (Left Hand)
        self.engine.add_gesture(PinchGesture("Type", 12, config.CLICK_THRESHOLD, hand_type='Left', 
                                             callback=self.kb_manager.handle_type))

    def toggle_mode(self):
        self.keyboard_mode_active = not self.keyboard_mode_active
        logger.info(f"Keyboard Mode: {self.keyboard_mode_active}")

    def run(self):
        logger.info("Starting Application...")
        self.last_right_hand_y = 0

        while True:
            img = self.cam.get_frame()
            if img is None: break

            hands, img = self.tracker.find_hands(img)
            
            # Update gestures for all hands
            self.engine.update_gestures(hands, self.tracker.detector)

            if self.keyboard_mode_active:
                img = self.kb_manager.draw_all(img)

            for hand in hands:
                if hand['type'] == 'Right':
                    self.last_right_hand_y = hand['lmList'][8][1]
                    self.mouse_manager.update(hand)
                elif self.keyboard_mode_active:
                    img = self.kb_manager.update_hover(img, hand['lmList'])

            mode_text = f"MODE: {'KEYBOARD' if self.keyboard_mode_active else 'MOUSE'}"
            cv2.putText(img, mode_text, config.MODE_INDICATOR_POS, 
                        cv2.FONT_HERSHEY_PLAIN, 2, config.COLOR_MODE_TEXT, 2)

            cv2.imshow("Virtual Keyboard & Mouse", img)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        self.cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    App().run()
