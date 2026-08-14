import cv2
import config
from camera import Camera
from hand_tracker import HandTracker
from keyboard.keyboard_manager import KeyboardManager
from keyboard.ui_overlay import UIOverlay
from mouse.mouse_manager import MouseManager
from gestures.engine import GestureEngine
from gestures.pinch_gesture import PinchGesture
from gestures.clap_gesture import DoubleClapGesture
from utils.calibration_manager import CalibrationManager
from utils.logger import logger

class App:
    def __init__(self):
        try:
            self.cam = Camera()
            self.tracker = HandTracker()
            self.kb_manager = KeyboardManager()
            self.mouse_manager = MouseManager()
            self.engine = GestureEngine()
            self.overlay = UIOverlay()
            self.calibration = CalibrationManager()
            
            self.keyboard_mode_active = False
            self.last_gesture = "None"
            self._setup_gestures()
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise

    def _setup_gestures(self):
        # Mode Toggle
        self.engine.add_gesture(DoubleClapGesture(callback=self.toggle_mode))
        
        # Mouse Gestures (Right Hand)
        self.engine.add_gesture(PinchGesture("Left Click", 12, config.CLICK_THRESHOLD, 
                                             callback=lambda s: self.handle_gesture("Left Click", self.mouse_manager.handle_left_click, s)))
        self.engine.add_gesture(PinchGesture("Right Click", 8, config.CLICK_THRESHOLD, 
                                             callback=lambda s: self.handle_gesture("Right Click", self.mouse_manager.handle_right_click, s)))
        self.engine.add_gesture(PinchGesture("Scroll", 20, config.SCROLL_THRESHOLD, 
                                             callback=lambda s: self.handle_gesture("Scroll", lambda st: self.mouse_manager.handle_scroll(st, self.last_right_hand_y), s)))

        # Keyboard Gesture (Left Hand)
        self.engine.add_gesture(PinchGesture("Type", 12, config.CLICK_THRESHOLD, hand_type='Left', 
                                             callback=lambda s: self.handle_gesture("Type", self.kb_manager.handle_type, s)))

    def handle_gesture(self, name, func, state):
        if state == 'start':
            self.last_gesture = name
        func(state)

    def toggle_mode(self):
        self.keyboard_mode_active = not self.keyboard_mode_active
        self.last_gesture = "Mode Toggle"
        logger.info(f"Keyboard Mode: {self.keyboard_mode_active}")

    def run(self):
        logger.info("Application starting. Press 'R' to recalibrate, 'Tab' to switch camera, 'Q' to quit.")
        self.last_right_hand_y = 0

        while True:
            try:
                img = self.cam.get_frame()
                if img is None:
                    logger.warning("Camera stream interrupted. Attempting to reconnect...")
                    if not self.cam._initialize_camera():
                        cv2.waitKey(1000)
                    continue

                hands, img = self.tracker.find_hands(img)
                
                if not self.calibration.is_calibrated:
                    progress = self.calibration.get_progress()
                    self.overlay.draw_calibration_progress(img, progress)
                    self.calibration.update(hands, self.tracker.detector)
                else:
                    self.engine.update_gestures(hands, self.tracker.detector)

                    if self.keyboard_mode_active:
                        img = self.kb_manager.draw_all(img)

                    for hand in hands:
                        if hand['type'] == 'Right':
                            self.last_right_hand_y = hand['lmList'][8][1]
                            self.mouse_manager.update(hand)
                        elif self.keyboard_mode_active:
                            img = self.kb_manager.update_hover(img, hand['lmList'])

                # UI Dashboard
                mode = "KEYBOARD" if self.keyboard_mode_active else "MOUSE"
                status = "CALIBRATED" if self.calibration.is_calibrated else "CALIBRATING"
                self.overlay.draw(img, mode, status, self.last_gesture)

                cv2.imshow("Virtual Control Center", img)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.calibration.start_calibration()
                elif key == ord('\t'): # Tab key
                    self.cam.switch_camera()

            except Exception as e:
                logger.error(f"Runtime error: {e}")
                break

        self.cam.release()
        cv2.destroyAllWindows()
        logger.info("Application closed.")

if __name__ == "__main__":
    try:
        App().run()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
