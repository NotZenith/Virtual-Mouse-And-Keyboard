import cv2
import numpy as np

def draw_rounded_rect(img, pos, size, radius, color, thickness=-1):
    x, y = pos
    w, h = size
    
    # Draw corners
    cv2.circle(img, (x + radius, y + radius), radius, color, thickness)
    cv2.circle(img, (x + w - radius, y + radius), radius, color, thickness)
    cv2.circle(img, (x + radius, y + h - radius), radius, color, thickness)
    cv2.circle(img, (x + w - radius, y + h - radius), radius, color, thickness)
    
    # Draw rectangles to fill
    cv2.rectangle(img, (x + radius, y), (x + w - radius, y + h), color, thickness)
    cv2.rectangle(img, (x, y + radius), (x + w, y + h - radius), color, thickness)

def draw_transparent_overlay(img, pos, size, color, alpha=0.5, radius=15):
    """Optimized overlay using ROI."""
    x, y = pos
    w, h = size
    
    # Ensure coordinates are within image bounds
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(img.shape[1], x + w), min(img.shape[0], y + h)
    
    if x1 >= x2 or y1 >= y2:
        return

    roi = img[y1:y2, x1:x2]
    overlay = roi.copy()
    
    # Adjust position for ROI
    draw_rounded_rect(overlay, (x - x1, y - y1), (w, h), radius, color, -1)
    cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)

def draw_text_with_shadow(img, text, pos, font, scale, color, thickness, shadow_color=(0,0,0)):
    x, y = pos
    cv2.putText(img, text, (x+1, y+1), font, scale, shadow_color, thickness)
    cv2.putText(img, text, pos, font, scale, color, thickness)
