import cv2
import config
from utils.logger import logger

class Camera:
    def __init__(self, index=0):
        self.index = index
        self.cap = None
        self._initialize_camera()

    def _initialize_camera(self):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera index {self.index}")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.HEIGHT)
        logger.info(f"Camera {self.index} initialized at {config.WIDTH}x{config.HEIGHT}")
        return True

    def get_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None
        success, img = self.cap.read()
        if not success:
            logger.warning("Failed to read frame from camera.")
            return None
        return img

    def switch_camera(self):
        self.index = (self.index + 1) % 3 # Try up to 3 cameras
        logger.info(f"Switching to camera index {self.index}")
        return self._initialize_camera()

    def release(self):
        if self.cap:
            self.cap.release()
            logger.info("Camera released.")
