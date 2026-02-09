from .config import *
import time
import math

class GestureArbiter:
    def __init__(self):
        self.current_priority = "IDLE"
        self.lock_time = 0
        self.last_action_time = 0
        
        # State tracking
        self.is_throwing = False
        self.is_peeking = False
        self.voice_active = False
        
    def decide(self, hand_data, face_data, voice_data):
        """
        The Core Brain.
        Inputs: Data from Vision & Voice threads.
        Output: The WINNING Action (string) and its confidence.
        """
        current_time = time.time()
        
        # 0. COOLDOWN CHECK (Prevent spamming)
        if current_time < self.lock_time:
            return "LOCKED", 0.0

        # 1. PHYSICS INTERCEPT (Highest Priority: The "Throw")
        # If moving super fast, it's definitely a Throw, not a slow point.
        velocity = hand_data.get('velocity', 0)
        if velocity > THROW_VELOCITY_THRESH and hand_data.get('is_fist'):
             print(f"🔥 ARBITER: Velocity Spike ({velocity}). WINNER: TELEPORT THROW")
             self.lock_time = current_time + 1.0 # Lock for 1 second after throw
             return "ACTION_THROW", 1.0

        # 2. VOICE INTERCEPT (Context)
        cmd = voice_data.get('last_command', '').lower()
        
        if "color" in cmd:
             print("🎨 ARBITER: Voice Context Detected. WINNER: CHAMELEON")
             return "ACTION_CHAMELEON", 1.0
             
        elif "open" in cmd:
             return "ACTION_OPEN_APP", 1.0
             
        elif "type" in cmd or "write" in cmd:
             return "ACTION_TYPE_TEXT", 1.0
             
        elif "search" in cmd:
             return "ACTION_SEARCH", 1.0
             
        elif "stop" in cmd or "exit" in cmd:
             return "ACTION_EXIT", 1.0

        # General Knowledge Fallback
        elif "what" in cmd or "who" in cmd or "how" in cmd or "explain" in cmd:
             return "ACTION_QUERY", 1.0


        # 3. BIO-ADAPTIVE (Passive)
        # These run in parallel (modify UI, don't block mouse)
        if face_data.get('is_squinting'):
            return "ACTION_SQUINT_SCALE", 0.8
        
        if face_data.get('lean_forward'):
            return "ACTION_PROX_ZOOM", 0.8

        # 4. GESTURE SHAPES (Static)
        # Shadow Clone (Two fingers touching -> Split)
        if hand_data.get('gesture') == "PEACE_SPLIT":
            return "ACTION_SHADOW_CLONE", 0.9

        # Peek Lift (Flat hand lift)
        if hand_data.get('gesture') == "FLAT_HAND" and hand_data.get('y_movement') < -50:
             return "ACTION_PEEK", 0.8
             
        # Silence (Shhh)
        if hand_data.get('gesture') == "INDEX_MOUTH":
            return "ACTION_SILENCE", 0.9

        # 5. DEFAULT FALLBACK
        # If nothing special, just be a mouse.
        return "ACTION_MOUSE_MOVE", 0.5
