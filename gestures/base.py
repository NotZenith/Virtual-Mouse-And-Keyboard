import time

class Gesture:
    def __init__(self, name, cooldown=0.5, callback=None):
        self.name = name
        self.cooldown = cooldown
        self.callback = callback
        self.last_trigger_time = 0
        self.is_active = False

    def can_trigger(self):
        return time.time() - self.last_trigger_time > self.cooldown

    def trigger(self, *args, **kwargs):
        if self.can_trigger():
            self.last_trigger_time = time.time()
            if self.callback:
                self.callback(*args, **kwargs)
            return True
        return False

    def detect(self, hands, detector):
        """Should be implemented by subclasses. Returns True if gesture is detected."""
        raise NotImplementedError
