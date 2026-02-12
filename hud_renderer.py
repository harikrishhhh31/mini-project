import cv2
import numpy as np
from .config import *

class HudRenderer:
    def __init__(self):
        self.click_timer = 0
        self.click_pos = (0, 0)
        self.reject_timer = 0

    def draw_text(self, img, text, pos, color=COLOR_CYAN_CORE, scale=0.6, thickness=1):
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)

    def draw_skeleton(self, img, landmarks, is_active=False):
        """Draws a sci-fi skeleton over the hand"""
        h, w, c = img.shape
        color = COLOR_GOLD if is_active else COLOR_CYAN_CORE
        
        # Connections (MediaPipe indices)
        connections = [
            (0,1), (1,2), (2,3), (3,4),         # Thumb
            (0,5), (5,6), (6,7), (7,8),         # Index
            (9,10), (10,11), (11,12),           # Middle
            (13,14), (14,15), (15,16),          # Ring
            (0,17), (17,18), (18,19), (19,20),  # Pinky
            (5,9), (9,13), (13,17)              # Palm
        ]
        
        points = {}
        for i, lm in enumerate(landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            points[i] = (cx, cy)
            # Draw Joint Nodes
            cv2.circle(img, (cx, cy), 3, color, -1)
            
        for s, e in connections:
            if s in points and e in points:
                cv2.line(img, points[s], points[e], color, 1)

    def draw_arc_reactor(self, img, center, radius):
        """Draws a circular target reticle"""
        cv2.circle(img, center, radius, COLOR_CYAN_GLOW, 1)
        cv2.circle(img, center, int(radius*0.7), COLOR_CYAN_CORE, 1)
        cv2.line(img, (center[0]-radius, center[1]), (center[0]+radius, center[1]), COLOR_CYAN_GLOW, 1)
        cv2.line(img, (center[0], center[1]-radius), (center[0], center[1]+radius), COLOR_CYAN_GLOW, 1)

    def render(self, frame, vision_data, decision, events=[]):
        """
        Main render loop. Draws all UI elements on top of the frame.
        """
        # Create a "Glassy" dark overlay for contrast
        overlay = frame.copy()
        cv2.rectangle(overlay, (0,0), (frame.shape[1], frame.shape[0]), (0,0,0), -1)
        cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
        
        h, w, c = frame.shape
        current_time = time.time()
        
        # Handle Events
        if "CLICKED" in events:
            self.click_timer = current_time + 0.3
            self.click_pos = vision_data.get('cursor', (w//2, h//2))
            
        # 1. STATUS WIDGET (Top Left)
        self.draw_text(frame, "HEISENBERG CORE: ONLINE", (20, 30), COLOR_CYAN_CORE, scale=0.7)
        
        # Mode Display logic with color coding
        mode_color = COLOR_CYAN_GLOW
        if "ACTION" in decision: mode_color = COLOR_GOLD
        if "REJECTED" in decision or "BLOCKED" in decision: mode_color = COLOR_RED_ALERT
        
        self.draw_text(frame, f"MODE: {decision}", (20, 70), mode_color, scale=1.0, thickness=2)
        
        # Voice Status (Top Right)
        if vision_data.get("voice_active"):
            self.draw_text(frame, "MIC: LISTENING", (w - 200, 30), (0, 255, 0), scale=0.7) # Green

        
        # Data widgets
        if vision_data.get('velocity'):
            vel = int(vision_data['velocity'])
            self.draw_text(frame, f"VEL: {vel} px/s", (20, 90), COLOR_RED_ALERT if vel > THROW_VELOCITY_THRESH else COLOR_CYAN_GLOW)
        
        # 2. HAND TRACKING
        if vision_data.get('hand_present'):
            # Check raw landmarks from VisionCore (Need to expose them in vision_core if not present)
            # For now, simplistic cursor draw
            cursor = vision_data.get('cursor')
            self.draw_arc_reactor(frame, cursor, 20)
            
            # Draw Line to destination
            if vision_data.get('is_fist'):
                self.draw_text(frame, "GRIP ACTIVE", (cursor[0]+30, cursor[1]), COLOR_GOLD)

            # Fix 4: Click Feedback Animation
            current_time = time.time()
            if current_time < self.click_timer:
                # Growing circle
                progress = 1.0 - (self.click_timer - current_time) / 0.3
                radius = int(20 + 30 * progress)
                cv2.circle(frame, self.click_pos, radius, COLOR_GOLD, 2)

        # 3. FACE TRACKING (Nose Target)
        if vision_data.get('face_present'):
             # Draw simple brackets around face area?
             # For bio-adaptive feedback
             if vision_data.get('is_squinting'):
                 self.draw_text(frame, "WARNING: EYE FATIGUE", (w//2 - 100, h - 50), COLOR_RED_ALERT)
                 
        return frame
