import time
import config
import math

class ClapDetector:
    def __init__(self):
        self.last_clap_time = 0
        self.clap_count = 0
        self.cooldown_until = 0

    def detect_double_clap(self, hands):
        # We need exactly two hands for a clap
        if len(hands) != 2:
            return False

        curr_time = time.time()
        if curr_time < self.cooldown_until:
            return False

        # Get centers of both hands
        h1_center = hands[0]['center']
        h2_center = hands[1]['center']

        # Calculate Euclidean distance between hand centers
        dist = math.sqrt((h1_center[0] - h2_center[0])**2 + (h1_center[1] - h2_center[1])**2)

        if dist < config.CLAP_THRESHOLD:
            # Clap detected
            if self.clap_count == 0:
                self.clap_count = 1
                self.last_clap_time = curr_time
                # Small delay to prevent detecting the same clap multiple times
                self.cooldown_until = curr_time + 0.2 
            elif self.clap_count == 1:
                if curr_time - self.last_clap_time < config.DOUBLE_CLAP_TIME:
                    # Double clap success!
                    self.clap_count = 0
                    self.cooldown_until = curr_time + config.CLAP_COOLDOWN
                    return True
                else:
                    # Too slow, reset
                    self.clap_count = 1
                    self.last_clap_time = curr_time
                    self.cooldown_until = curr_time + 0.2
        else:
            # Reset if too much time passes since first clap
            if self.clap_count == 1 and curr_time - self.last_clap_time > config.DOUBLE_CLAP_TIME:
                self.clap_count = 0

        return False
