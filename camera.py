import cv2
import logging

class Camera:
    def __init__(self, index=0, width=1280, height=720):
        self.index = index
        self.cap = cv2.VideoCapture(index)
        self.cap.set(3, width)
        self.cap.set(4, height)

    def get_frame(self):
        success, img = self.cap.read()
        return img if success else None

    def switch(self):
        self.cap.release()
        self.index = (self.index + 1) % 3
        self.cap = cv2.VideoCapture(self.index)
        return self.cap.isOpened()
