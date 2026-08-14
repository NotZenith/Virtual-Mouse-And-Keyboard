import time
import math
from cvzone.HandTrackingModule import HandDetector

class Gesture:
    def __init__(self, name, cooldown=0.5, callback=None):
        self.name, self.cooldown, self.callback = name, cooldown, callback
        self.last_time, self.is_active = 0, False

    def trigger(self, *args, **kwargs):
        if time.time() - self.last_time > self.cooldown:
            self.last_time = time.time()
            if self.callback: self.callback(*args, **kwargs)
            return True
        return False

class PinchGesture(Gesture):
    def __init__(self, name, f_idx, threshold, h_type='Right', callback=None, cooldown=0.5):
        super().__init__(name, cooldown, callback)
        self.f_idx, self.threshold, self.h_type = f_idx, threshold, h_type

    def detect(self, hand, detector):
        if hand['type'] != self.h_type: return False
        # Ensure we use 2D points for distance calculation to avoid unpacking errors
        p1 = hand['lmList'][4][:2]
        p2 = hand['lmList'][self.f_idx][:2]
        dist, _, _ = detector.findDistance(p1, p2, draw=False)
        detected = dist < self.threshold
        if detected and not self.is_active:
            if self.trigger(state='start'): self.is_active = True
        elif not detected and self.is_active:
            self.trigger(state='end')
            self.is_active = False
        return detected

class DoubleClapGesture(Gesture):
    def __init__(self, callback=None):
        super().__init__("Double Clap", 0.8, callback)
        self.count, self.last_clap = 0, 0

    def detect(self, hands):
        if len(hands) != 2: return False
        h1, h2 = hands[0]['center'], hands[1]['center']
        dist = math.sqrt((h1[0]-h2[0])**2 + (h1[1]-h2[1])**2)
        curr = time.time()
        if dist < 60:
            if self.count == 0:
                self.count, self.last_clap = 1, curr
                time.sleep(0.1)
            elif self.count == 1:
                if curr - self.last_clap < 0.5:
                    self.count = 0
                    return self.trigger()
                self.count, self.last_clap = 1, curr
        elif self.count == 1 and curr - self.last_clap > 0.5:
            self.count = 0
        return False
