import cv2
import time
import queue
import sys
import threading

# Core Modules
from vision_core import VisionCore
from voice_core import VoiceCore
from gesture_arbiter import GestureArbiter
from system_controller import SystemController, SystemState
from action_dispatcher import ActionDispatcher
from hud_renderer import HudRenderer
from speaker_core import SpeakerCore
from brain_core import BrainCore

def main():
    # 1. Initialize Communication Channels
    command_queue = queue.Queue() # Voice -> Main
    
    # 2. visual Feedback & Audio
    renderer = HudRenderer()
    speaker = SpeakerCore()
    speaker.start() # Start TTS Consumer Thread
    
    # 3. Input Cores
    vision = VisionCore()
    voice = VoiceCore(command_queue)
    voice.start() # Start Background Listener
    
    # 4. Intelligence & Decision
    brain = BrainCore() # LLM / Web Search
    arbiter = GestureArbiter() # Intent Resolver
    controller = SystemController() # State Authority
    
    # 5. Execution
    dispatcher = ActionDispatcher(speaker=speaker)
    
    # 6. Camera Setup
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("CRITICAL ERROR: Camera not found.")
        sys.exit(1)
        
    print("SYSTEM: Initialization Complete. HEISENBERG CORE ONLINE.")
    speaker.speak("Core systems online.")

    # State Tracking variables
    voice_data = {"last_command": ""}
    
    try:
        while True:
            # A. CAPTURE FRAME
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1) # Mirror view
            
            # B. PROCESS INPUTS
            # 1. Vision
            vision_data = vision.process_frame(frame)
            
            # 2. Voice (Poll Queue)
            try:
                while not command_queue.empty():
                    msg = command_queue.get_nowait()
                    if msg['type'] == 'VOICE_COMMAND':
                        cmd = msg['payload']
                        voice_data["last_command"] = cmd
                        
                        # Controller State Update based on Keyword?
                        # For now, simplistic: Any specific keywords to change state?
                        if "gesture only" in cmd:
                            controller.set_state(SystemState.GESTURE)
                            speaker.speak("Gesture Mode.")
                        elif "voice only" in cmd:
                            controller.set_state(SystemState.VOICE)
                            speaker.speak("Voice Mode.")
                        elif "hybrid" in cmd:
                            controller.set_state(SystemState.HYBRID)
                            speaker.speak("Hybrid Mode.")
                            
                    elif msg['type'] == 'FEEDBACK':
                        speaker.speak(msg['payload'])
            except queue.Empty:
                pass
                
            # C. DECISION (Arbiter)
            # We assume Hybrid Mode default effectively for the Arbiter's logic, 
            # but the Controller will filter it.
            # Ideally, we should initialize Controller to HYBRID.
            if controller.current_state == SystemState.IDLE:
                 # Auto-start in Hybrid for this demo
                 controller.set_state(SystemState.HYBRID)
            
            suggested_action, confidence = arbiter.decide(vision_data, vision_data, voice_data)
            
            # Determine Source for Authority Check
            source = "GESTURE"
            if suggested_action in ["ACTION_OPEN_APP", "ACTION_TYPE_TEXT", "ACTION_SEARCH", "ACTION_QUERY", "ACTION_EXIT", "ACTION_CHAMELEON"]:
                source = "VOICE"
            
            # D. AUTHORITY CHECK (System Controller)
            is_allowed = controller.authorize_action(suggested_action, source)
            
            final_action = "IDLE"
            action_data = vision_data.copy() # Start with vision data
            action_data['voice_command'] = voice_data.get('last_command', '')
            
            if is_allowed and confidence > 0.7:
                final_action = suggested_action
                
                # Special Handling for Brain Query (It needs the answer first)
                if final_action == "ACTION_QUERY":
                    # Fetch from Brain
                    is_cmd, answer = brain.process_query(voice_data['last_command'])
                    action_data['brain_response'] = answer
                    
                # E. EXECUTION (Dispatcher)
                # Only execute if it's not LOCKED (Arbiter returns locked for cooldowns)
                if final_action != "LOCKED":
                    dispatcher.execute(final_action, action_data)
                    
                    # Clear voice command after successful execution to prevent looping
                    if source == "VOICE":
                        voice_data["last_command"] = ""
            
            # F. RENDER HUD
            # Pass the *Authorized* action for display
            ui_state = f"{final_action}" 
            if not is_allowed and suggested_action != "MOUSE_MOVE":
                 ui_state = f"BLOCKED ({suggested_action})"
                 
            processed_frame = renderer.render(frame, vision_data, ui_state)
            
            cv2.imshow('Heisenberg HUD', processed_frame)
            
            # G. EXIT CONDITION
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            if final_action == "ACTION_EXIT":
                break
                
    except KeyboardInterrupt:
        print("User Interrupt.")
    finally:
        # Cleanup
        print("Shutting down...")
        voice.stop()
        cap.release()
        cv2.destroyAllWindows()
        speaker.speak("Systems offline.")
        sys.exit(0)

if __name__ == "__main__":
    main()
