from cvzone.HandTrackingModule import HandDetector
import config

class HandTracker:
    def __init__(self, detection_con=config.DETECTION_CONFIDENCE):
        self.detector = HandDetector(detectionCon=detection_con, maxHands=2)

    def find_hands(self, img, draw=True):
        # findHands returns img and a list of hands
        # Each hand is a dict: {'lmList', 'bbox', 'center', 'type'}
        hands, img = self.detector.findHands(img, draw=draw)
        return hands, img

    def get_distance(self, p1, p2, img=None):
        # findDistance can take raw coordinates or indices
        # We wrapper it for convenience
        dist, info, img = self.detector.findDistance(p1, p2, img)
        return dist, info, img
