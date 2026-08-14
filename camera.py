import cv2
import config

class Camera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(3, config.WIDTH)
        self.cap.set(4, config.HEIGHT)

    def get_frame(self):
        success, img = self.cap.read()
        if not success:
            return None
        return img

    def release(self):
        self.cap.release()
