from .base import Gesture
import config
import math
import time

class DoubleClapGesture(Gesture):
    def __init__(self, name="Double Clap", cooldown=config.CLAP_COOLDOWN, callback=None):
        super().__init__(name, cooldown, callback)
        self.clap_count = 0
        self.last_clap_time = 0
        self.threshold = config.CLAP_THRESHOLD
        self.double_time = config.DOUBLE_CLAP_TIME

    def detect(self, hands, detector):
        if len(hands) != 2:
            return False

        curr_time = time.time()
        # Single point centers
        h1_center = hands[0]['center']
        h2_center = hands[1]['center']

        dist = math.sqrt((h1_center[0] - h2_center[0])**2 + (h1_center[1] - h2_center[1])**2)

        if dist < self.threshold:
            if self.clap_count == 0:
                self.clap_count = 1
                self.last_clap_time = curr_time
                time.sleep(0.1) # Debounce
            elif self.clap_count == 1:
                if curr_time - self.last_clap_time < self.double_time:
                    self.clap_count = 0
                    return self.trigger()
                else:
                    self.clap_count = 1
                    self.last_clap_time = curr_time
        else:
            if self.clap_count == 1 and curr_time - self.last_clap_time > self.double_time:
                self.clap_count = 0
        
        return False
