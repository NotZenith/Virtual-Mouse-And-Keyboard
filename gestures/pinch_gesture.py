from .base import Gesture
import config

class PinchGesture(Gesture):
    def __init__(self, name, finger_index, threshold, hand_type='Right', cooldown=0.5, callback=None):
        super().__init__(name, cooldown, callback)
        self.finger_index = finger_index # 8 for Index, 12 for Middle, 20 for Pinky
        self.threshold = threshold
        self.hand_type = hand_type
        self.thumb_index = 4

    def detect(self, hand, detector):
        if hand['type'] != self.hand_type:
            return False

        # Get distance between thumb and target finger
        # detector is the cvzone HandDetector
        dist, _, _ = detector.findDistance(self.thumb_index, self.finger_index, draw=False)
        
        detected = dist < self.threshold
        
        # Handle state changes for one-shot vs continuous triggers
        if detected and not self.is_active:
            if self.trigger(state='start'):
                self.is_active = True
        elif not detected and self.is_active:
            self.trigger(state='end')
            self.is_active = False
            
        return detected
