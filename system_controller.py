import time
import requests
from enum import Enum, auto
from settings_manager import load_settings, save_settings

class SystemState(Enum):
    IDLE = auto()
    VOICE = auto()
    GESTURE = auto()
    HYBRID = auto()
    SAFE_EXIT = auto()

class SystemController:
    def __init__(self, server_port=None):
        self.current_state = SystemState.IDLE
        self.server_port = server_port
        self.server_url = f"http://127.0.0.1:{server_port}" if server_port else None
        
        # Load settings from JSON
        settings = load_settings()
        
        # Sensitivity Control (Scale Factor: 0.5x to 2.0x)
        self.sensitivity = settings.get('sensitivity', 1.0)
        self.speech_speed = settings.get('speech_speed', 1.0)
        self.mode = settings.get('mode', 'hybrid')
        self.MIN_SENS = 0.5
        self.MAX_SENS = 2.0
        self.STEP = 0.1
        
        # HUD Message System
        self.system_message = None
        self.message_expiry = 0
        
        # Apply loaded mode
        if self.mode == 'gesture':
            self.current_state = SystemState.GESTURE
        elif self.mode == 'voice':
            self.current_state = SystemState.VOICE
        elif self.mode == 'hybrid':
            self.current_state = SystemState.HYBRID
    
    def notify_server(self, key, value):
        """Notify settings server of local changes via HTTP"""
        if not self.server_url:
            return
        
        try:
            payload = {key: value}
            requests.post(
                f"{self.server_url}/settings/preview",
                json=payload,
                timeout=0.5
            )
        except:
            pass  # Silent fail - server might not be ready

    def set_state(self, new_state: SystemState):
        """
        Updates the current system state.
        """
        self.current_state = new_state
        
        # Map state to mode string and save
        mode_map = {
            SystemState.GESTURE: 'gesture',
            SystemState.VOICE: 'voice',
            SystemState.HYBRID: 'hybrid'
        }
        if new_state in mode_map:
            self.mode = mode_map[new_state]
            save_settings({
                'sensitivity': self.sensitivity,
                'mode': self.mode,
                'speech_speed': self.speech_speed,
                'port': self.server_port if self.server_port else 2026
            })
            # Notify server
            self.notify_server('mode', self.mode)
        
    def adjust_sensitivity(self, direction, speaker=None):
        """
        Safely adjusts sensitivity within bounds.
        Saves to JSON and notifies server.
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
        
        # Save to JSON
        if old_sens != self.sensitivity:
            save_settings({
                'sensitivity': self.sensitivity,
                'mode': self.mode,
                'speech_speed': self.speech_speed,
                'port': self.server_port if self.server_port else 2026
            })
            # Notify server
            self.notify_server('sensitivity', self.sensitivity)
        
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
    
    def update_from_server(self, settings):
        """Update local settings from server (when web UI changes them)"""
        if 'sensitivity' in settings:
            self.sensitivity = settings['sensitivity']
        if 'mode' in settings:
            self.mode = settings['mode']
            # Update state enum
            mode_map = {
                'gesture': SystemState.GESTURE,
                'voice': SystemState.VOICE,
                'hybrid': SystemState.HYBRID
            }
            if self.mode in mode_map:
                self.current_state = mode_map[self.mode]
        if 'speech_speed' in settings:
            self.speech_speed = settings['speech_speed']

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
