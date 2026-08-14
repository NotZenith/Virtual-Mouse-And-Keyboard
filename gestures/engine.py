class GestureEngine:
    def __init__(self):
        self.gestures = []

    def add_gesture(self, gesture):
        self.gestures.append(gesture)

    def process(self, hands, detector):
        """
        Processes hands and triggers detected gestures.
        """
        results = {}
        
        # Check multi-hand gestures first (like Clap)
        for gesture in self.gestures:
            if hasattr(gesture, 'detect_multi'):
                detected = gesture.detect_multi(hands, detector)
                results[gesture.name] = detected
            elif hasattr(gesture, 'detect'):
                # For single hand gestures, we check each hand
                for hand in hands:
                    detected = gesture.detect(hand, detector)
                    if detected:
                        results[gesture.name] = True
                        break # One detection per frame for now
        
        return results

    def update_gestures(self, hands, detector):
        # Specific wrapper for the current hand detection structure
        # Some gestures take all hands (Clap), some take one (Pinch)
        for gesture in self.gestures:
            # We'll adapt PinchGesture and DoubleClapGesture to a common interface
            # DoubleClap needs all hands
            if "Clap" in gesture.name:
                gesture.detect(hands, detector)
            else:
                # Pinch needs specific hand type
                for hand in hands:
                    gesture.detect(hand, detector)
