from enum import Enum, auto

class SystemState(Enum):
    IDLE = auto()
    VOICE = auto()
    GESTURE = auto()
    HYBRID = auto()
    SAFE_EXIT = auto()

class SystemController:
    def __init__(self):
        self.current_state = SystemState.IDLE
        # Sensitivity Control (Scale Factor: 0.5x to 2.0x)
        self.sensitivity = 1.0
        self.MIN_SENS = 0.5
        self.MAX_SENS = 2.0
        self.STEP = 0.1
        
        # HUD Message System
        self.system_message = None
        self.message_expiry = 0

    def set_state(self, new_state: SystemState):
        """
        Updates the current system state.
        """
        self.current_state = new_state
        
    def adjust_sensitivity(self, direction, speaker=None):
        """
        Safely adjusts sensitivity within bounds.
        """
        old_sens = self.sensitivity
        
        if direction == "increase":
            self.sensitivity = min(self.MAX_SENS, self.sensitivity + self.STEP)
        elif direction == "decrease":
            self.sensitivity = max(self.MIN_SENS, self.sensitivity - self.STEP)
        elif direction == "reset":
            self.sensitivity = 1.0
            
        # Round to 1 decimal to avoid float drift
        self.sensitivity = round(self.sensitivity, 1)
        
        if speaker and old_sens != self.sensitivity:
             speaker.speak(f"Sensitivity set to {self.sensitivity}")
             
        # Set HUD Message for 2 seconds
        self.system_message = f"Sensitivity: {self.sensitivity}"
        self.message_expiry = time.time() + 2.0
             
        return self.sensitivity

    def get_sensitivity(self) -> float:
        """
        Returns the current sensitivity value.
        """
        return self.sensitivity

    def get_active_message(self):
        """Returns temporary system message if active"""
        if time.time() < self.message_expiry:
             return self.system_message
        return None

    def authorize_action(self, suggested_action: str, source: str) -> bool:
        """
        Decides whether an action is allowed based on the current state.
        
        Args:
            suggested_action: The name of the action (e.g., "ACTION_THROW").
            source: The origin of the action (e.g., "VOICE" or "GESTURE").
            
        Returns:
            bool: True if the action is authorized, False otherwise.
        """
        # 1. Global Safety Override
        if self.current_state == SystemState.SAFE_EXIT:
            return False

        # 2. State-Based Authorization
        if self.current_state == SystemState.IDLE:
            # In IDLE, effectively all actions are blocked until a specific 'Wake' event
            # changes the state (handled externally via set_state).
            return False

        if self.current_state == SystemState.VOICE:
            # Only allow Voice commands
            return source == "VOICE"

        if self.current_state == SystemState.GESTURE:
            # Only allow Gesture commands
            return source == "GESTURE"

        if self.current_state == SystemState.HYBRID:
            # Allow all inputs
            return True

        return False
