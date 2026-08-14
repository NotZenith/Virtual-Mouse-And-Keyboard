import cv2
from camera import Camera
from hand_tracker import HandTracker
from keyboard.keyboard_manager import KeyboardManager
from utils.logger import logger

def main():
    logger.info("Starting Virtual Keyboard application...")
    
    cam = Camera()
    tracker = HandTracker()
    kb_manager = KeyboardManager()

    while True:
        img = cam.get_frame()
        if img is None:
            break

        # Hand detection
        img = tracker.find_hands(img)
        lm_list, _ = tracker.get_position(img)

        # Keyboard logic and rendering
        img = kb_manager.draw_all(img)
        img = kb_manager.update(img, lm_list, tracker.detector)

        cv2.imshow("Virtual Keyboard", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    logger.info("Application closed.")

if __name__ == "__main__":
    main()
