import time
import math
import config
from utils.settings_manager import settings_manager
from utils.logger import logger

class CalibrationManager:
    def __init__(self):
        self.is_calibrated = settings_manager.get("IS_CALIBRATED") or False
        self.calibration_start_time = 0
        self.calibration_duration = 3.0 # Seconds to hold pose
        self.samples = []

    def start_calibration(self):
        self.is_calibrated = False
        self.calibration_start_time = time.time()
        self.samples = []
        logger.info("Calibration started.")

    def update(self, hands, detector):
        if self.is_calibrated:
            return True

        if len(hands) != 2:
            self.calibration_start_time = time.time() # Reset if hands lost
            return False

        curr_time = time.time()
        
        # Collect hand sizes (distance between thumb base and pinky base or palm size)
        for hand in hands:
            lm_list = hand['lmList']
            # Distance between wrist (0) and middle finger mcp (9) as a proxy for hand scale
            dist, _, _ = detector.findDistance(0, 9, draw=False)
            self.samples.append(dist)

        if curr_time - self.calibration_start_time >= self.calibration_duration:
            self.finish_calibration()
            return True
        
        return False

    def finish_calibration(self):
        if not self.samples:
            return
        
        avg_hand_size = sum(self.samples) / len(self.samples)
        logger.info(f"Calibration finished. Avg hand size: {avg_hand_size}")
        
        # Adjust thresholds based on hand size
        # Base size was around 100-120 in testing for default 30 threshold
        scale_factor = avg_hand_size / 110.0
        
        new_click_threshold = int(30 * scale_factor)
        new_scroll_threshold = int(40 * scale_factor)
        
        settings_manager.set("CLICK_THRESHOLD", new_click_threshold)
        settings_manager.set("DRAG_THRESHOLD", new_click_threshold)
        settings_manager.set("SCROLL_THRESHOLD", new_scroll_threshold)
        settings_manager.set("IS_CALIBRATED", True)
        
        self.is_calibrated = True
        logger.info(f"Thresholds updated: Click={new_click_threshold}, Scroll={new_scroll_threshold}")

    def get_progress(self):
        if self.is_calibrated: return 1.0
        elapsed = time.time() - self.calibration_start_time
        return min(elapsed / self.calibration_duration, 1.0)
