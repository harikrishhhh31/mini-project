from .config import *
import time
import math
from gesture_network import GestureEngine

class GestureArbiter:
    def __init__(self):
        self.current_priority = "IDLE"
        self.lock_time = 0
        self.engine = GestureEngine() # Initialize Neural Network
        
    def train_neural_net(self, X, y):
        """Pass-through for training"""
        self.engine.train_batch(X, y)

    def decide(self, hand_data, face_data, voice_data):
        current_time = time.time()
        
        if current_time < self.lock_time:
             return "LOCKED", 0.0

        # ... (Physics Check Same) ...
        velocity = hand_data.get('velocity', 0)
        # Check Right hand for fist throw
        right_hand = hand_data.get('hands', {}).get('Right', {})
        
        if velocity > THROW_VELOCITY_THRESH and right_hand.get('is_fist'):
             print(f"🔥 ARBITER: Velocity Spike ({velocity}). WINNER: TELEPORT THROW")
             self.lock_time = current_time + 1.0 
             return "ACTION_THROW", 1.0

        # ... (Voice Check Same) ...
        cmd = voice_data.get('last_command', '').lower()
        if "color" in cmd: return "ACTION_CHAMELEON", 1.0
        elif "click" in cmd: return "ACTION_CLICK", 1.0
        elif "open" in cmd: return "ACTION_OPEN_APP", 1.0
        elif "type" in cmd or "write" in cmd: return "ACTION_TYPE_TEXT", 1.0
        elif "search" in cmd: return "ACTION_SEARCH", 1.0
        elif "exit" in cmd:
             if "heisenberg" in cmd: return "ACTION_EXIT", 1.0
             else: return "ACTION_VOICE_REJECTED", 1.0
        elif "stop" in cmd: return "ACTION_EXIT", 1.0
        elif "what" in cmd or "who" in cmd or "how" in cmd or "explain" in cmd: return "ACTION_QUERY", 1.0
        elif len(cmd) > 0: return "ACTION_VOICE_REJECTED", 1.0

        # 3. NEURAL NETWORK (The Brain)
        # Check Right Hand first
        if right_hand.get('raw_landmarks'):
             nn_gesture, nn_conf = self.engine.predict(right_hand['raw_landmarks'])
             
             if nn_conf > 0.8: # High confidence neural prediction
                 if nn_gesture == "PEACE": return "ACTION_PEACE_MODE", nn_conf
                 if nn_gesture == "POINT": return "ACTION_MOUSE_MOVE", nn_conf # Pointing = Mouse
                 if nn_gesture == "FIST":  return "ACTION_GRIP", nn_conf
                 if nn_gesture == "OPEN":  return "ACTION_RELEASE", nn_conf

        # 4. HEURISTIC FALLBACKS (If NN is unsure or untained)
        # Face
        if face_data.get('is_squinting'): return "ACTION_SQUINT_SCALE", 0.8
        if face_data.get('lean_forward'): return "ACTION_PROX_ZOOM", 0.8

        # Hand Shapes
        if right_hand.get('gesture') == "PEACE_SPLIT": return "ACTION_SHADOW_CLONE", 0.9

        # Default
        return "ACTION_MOUSE_MOVE", 0.5
