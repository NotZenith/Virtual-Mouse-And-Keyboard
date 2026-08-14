import cv2
from camera import Camera
from hand_tracker import HandTracker
from keyboard.keyboard_manager import KeyboardManager
from mouse.mouse_manager import MouseManager
from utils.logger import logger

def main():
    logger.info("Starting Virtual Keyboard and Mouse application...")
    
    cam = Camera()
    tracker = HandTracker()
    kb_manager = KeyboardManager()
    mouse_manager = MouseManager()

    while True:
        img = cam.get_frame()
        if img is None:
            break

        # Hand detection
        hands, img = tracker.find_hands(img)
        
        # Keyboard rendering (always show)
        img = kb_manager.draw_all(img)

        # Process each hand
        for hand in hands:
            if hand['type'] == 'Right':
                # Right hand controls the mouse
                mouse_manager.update(hand, tracker.detector)
            else:
                # Left hand (or any other) controls the keyboard
                img = kb_manager.update(img, hand['lmList'], tracker.detector)

        cv2.imshow("Virtual Keyboard & Mouse", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    logger.info("Application closed.")

if __name__ == "__main__":
    main()
