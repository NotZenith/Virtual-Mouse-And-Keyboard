from cvzone.HandTrackingModule import HandDetector
import config

class HandTracker:
    def __init__(self, detection_con=config.DETECTION_CONFIDENCE):
        self.detector = HandDetector(detectionCon=detection_con)

    def find_hands(self, img):
        return self.detector.findHands(img)

    def get_position(self, img):
        return self.detector.findPosition(img)

    def get_distance(self, p1, p2, img):
        return self.detector.findDistance(p1, p2, img)
