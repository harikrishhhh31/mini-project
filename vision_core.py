import cv2
import mediapipe as mp
import time
import math
import numpy as np
from .utils import PointFilter
from .config import *

class VisionCore:
    def __init__(self):
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6
        )
        self.mp_face = mp.solutions.face_mesh
        self.face = self.mp_face.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6
        )
        
        # filters
        self.cursor_filter = PointFilter(min_cutoff=0.01, beta=SMOOTHING_BETA)
        
        # State
        self.prev_time = time.time()
        self.prev_hand_pos = None

    def get_eye_aspect_ratio(self, eye_landmarks, w, h):
        # Simply calculate height/width ratio of eye
        # Landmarks: [Top, Bottom, Left, Right]
        # Approximation for 'Squint' detection
        top = np.array([eye_landmarks[1].x*w, eye_landmarks[1].y*h])
        bottom = np.array([eye_landmarks[3].x*w, eye_landmarks[3].y*h])
        left = np.array([eye_landmarks[0].x*w, eye_landmarks[0].y*h])
        right = np.array([eye_landmarks[2].x*w, eye_landmarks[2].y*h])
        
        height = np.linalg.norm(top - bottom)
        width = np.linalg.norm(left - right)
        return height / (width + 1e-6)

    def process_frame(self, frame, sensitivity=1.0):
        """
        Main pipeline. Returns a dictionary of 'High Level' features for the Arbiter.
        Sensitivity: 1.0 = Normal (1:1 mapping). >1.0 = Faster (Smaller hand movement covers screen).
        """
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 1. Run Inference
        hand_results = self.hands.process(rgb_frame)
        face_results = self.face.process(rgb_frame)
        
        data = {
            "hand_present": False,
            "face_present": False,
            "velocity": 0,
            "is_fist": False,
            "gesture": "NONE",
            "cursor": (0, 0),
            "is_squinting": False,
            "lean_forward": False,
            "raw_frame": frame
        }

        current_time = time.time()
        dt = current_time - self.prev_time
        self.prev_time = current_time

        # 2. Process BIO-ADAPTIVE (Face)
        if face_results.multi_face_landmarks:
            data["face_present"] = True
            face = face_results.multi_face_landmarks[0]
            
            # Squint Detection (Left Eye: 33, 160, 158, 133... approx indices)
            # Using simple indices for speed (Left Eye)
            left_eye_indices = [33, 159, 133, 145] # Left, Top, Right, Bottom
            left_eye_points = [face.landmark[i] for i in left_eye_indices]
            ear = self.get_eye_aspect_ratio(left_eye_points, w, h)
            
            if ear < 0.15: # Threshold for squint
                data["is_squinting"] = True
            
            # Lean Detection (Z-depth of nose tip #1)
            # MediaPipe Z is relative to face center. Closer = smaller/negative?
            # Actually easier: Check Bounding Box size or Inter-ocular distance
            nose_tip = face.landmark[1]
            if nose_tip.z < -0.1: # Very close to cam
                data["lean_forward"] = True

        # 3. Process GESTURES (Hand)
        data["hands"] = {"Left": {}, "Right": {}}
        
        if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
            data["hand_present"] = True
            
            for idx, hand_handedness in enumerate(hand_results.multi_handedness):
                hand = hand_results.multi_hand_landmarks[idx]
                label = hand_handedness.classification[0].label # "Left" or "Right"
                
                # Landmarks
                wrist = hand.landmark[0]
                thumb_tip = hand.landmark[4]
                index_tip = hand.landmark[8]
                middle_tip = hand.landmark[12]
                
                # Metrics dictionary for this hand
                hand_data = {
                    "is_fist": False,
                    "pinch_index": 1000,
                    "pinch_middle": 1000,
                    "cursor": (0,0),
                    "velocity": 0,
                    "gesture": "NONE"
                }

                # Coordinates (Index Tip)
                raw_cx, raw_cy = int(index_tip.x * w), int(index_tip.y * h)
                
                # Apply Sensitivity (Scale input relative to center)
                # "Faster" = Sensitivity > 1.0
                if sensitivity != 1.0:
                    center_x, center_y = w // 2, h // 2
                    # Scale delta from center
                    # If sens = 2.0, a delta of 10 become 20.
                    dx = (raw_cx - center_x) * sensitivity
                    dy = (raw_cy - center_y) * sensitivity
                    
                    cx = int(center_x + dx)
                    cy = int(center_y + dy)
                    
                    # Clamp to screen
                    cx = max(0, min(w, cx))
                    cy = max(0, min(h, cy))
                else:
                    cx, cy = raw_cx, raw_cy
                
                
                # Velocity & Smoothing (Only tracked for Right/Dominant hand for cursor usually)
                if label == "Right": # Assuming Right is dominant pointer
                    smooth_x, smooth_y = self.cursor_filter.process(cx, cy)
                    data["cursor"] = (smooth_x, smooth_y)
                    
                    if self.prev_hand_pos:
                        dist = math.hypot(cx - self.prev_hand_pos[0], cy - self.prev_hand_pos[1])
                        velocity = dist / (dt + 1e-6)
                        data["velocity"] = velocity
                    self.prev_hand_pos = (cx, cy)

                # Fist Detection
                if index_tip.y > hand.landmark[6].y and middle_tip.y > hand.landmark[10].y:
                    hand_data["is_fist"] = True
                
                # PINCH DETECTION
                # Index Pinch
                hand_data["pinch_index"] = math.hypot((index_tip.x - thumb_tip.x)*w, (index_tip.y - thumb_tip.y)*h)
                # Middle Pinch
                hand_data["pinch_middle"] = math.hypot((middle_tip.x - thumb_tip.x)*w, (middle_tip.y - thumb_tip.y)*h)
                
                # Gestures
                if index_tip.y < hand.landmark[6].y and middle_tip.y < hand.landmark[10].y:
                    finger_gap = math.hypot(index_tip.x - middle_tip.x, index_tip.y - middle_tip.y)
                    if finger_gap > 0.15:
                        hand_data["gesture"] = "PEACE_SPLIT"
                
                # Neural Network Input (Raw Landmarks relative to Wrist)
                # 21 points * 2 coords (x, y) = 42 floats
                raw_landmarks = []
                for lm in hand.landmark:
                    # Normalize relative to wrist to be position-invariant
                    rx = lm.x - wrist.x
                    ry = lm.y - wrist.y
                    raw_landmarks.extend([rx, ry])
                
                hand_data["raw_landmarks"] = raw_landmarks
                        
                data["hands"][label] = hand_data

        return data
