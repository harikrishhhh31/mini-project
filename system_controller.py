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

    def set_state(self, new_state: SystemState):
        """
        Updates the current system state.
        """
        self.current_state = new_state

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
