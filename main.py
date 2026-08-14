import cv2
import config
from camera import Camera
from hand_tracker import HandTracker
from keyboard.keyboard_manager import KeyboardManager
from mouse.mouse_manager import MouseManager
from gestures.clap_detector import ClapDetector
from utils.logger import logger

def main():
    logger.info("Starting Virtual Keyboard and Mouse application...")
    
    cam = Camera()
    tracker = HandTracker()
    kb_manager = KeyboardManager()
    mouse_manager = MouseManager()
    clap_detector = ClapDetector()

    keyboard_mode_active = False

    while True:
        img = cam.get_frame()
        if img is None:
            break

        # Hand detection
        hands, img = tracker.find_hands(img)
        
        # Check for mode toggle (Double Clap)
        if clap_detector.detect_double_clap(hands):
            keyboard_mode_active = not keyboard_mode_active
            logger.info(f"Keyboard Mode toggled: {keyboard_mode_active}")

        # Keyboard rendering and interaction (if active)
        if keyboard_mode_active:
            img = kb_manager.draw_all(img)

        # Process each hand
        for hand in hands:
            if hand['type'] == 'Right':
                # Right hand always controls the mouse
                mouse_manager.update(hand, tracker.detector)
            else:
                # Left hand (or any other) controls the keyboard IF active
                if keyboard_mode_active:
                    img = kb_manager.update(img, hand['lmList'], tracker.detector)

        # UI Indicators
        mode_text = "MODE: KEYBOARD" if keyboard_mode_active else "MODE: MOUSE"
        cv2.putText(img, mode_text, config.MODE_INDICATOR_POS,
                    cv2.FONT_HERSHEY_PLAIN, 2, config.COLOR_MODE_TEXT, 2)

        cv2.imshow("Virtual Keyboard & Mouse", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    logger.info("Application closed.")

if __name__ == "__main__":
    main()
