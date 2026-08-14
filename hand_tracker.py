from cvzone.HandTrackingModule import HandDetector
import config

class HandTracker:
    def __init__(self, detection_con=config.DETECTION_CONFIDENCE):
        # Increased detection confidence for stability
        self.detector = HandDetector(detectionCon=detection_con, maxHands=2)

    def find_hands(self, img, draw=False):
        """Find hands in the image. Default draw=False for performance."""
        hands, img = self.detector.findHands(img, draw=draw)
        return hands, img

    def get_distance(self, p1, p2, img=None):
        """Calculate distance between two points."""
        dist, info, img = self.detector.findDistance(p1, p2, img)
        return dist, info, img
