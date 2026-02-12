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
    
    # Training Data
    recorded_data = []
    recorded_labels = []
    is_recording = False
    
    try:
        while True:
            # A. CAPTURE FRAME
            ret, frame = cap.read()
            if not ret: 
                # Fix 3: Camera Failure Feedback & Recon
                print("⚠️ CAMERA DISCONNECTED. Retrying...")
                speaker.speak("Camera connection lost.")
                
                # Try to reconnect
                reconnected = False
                for _ in range(5):
                    cap.release()
                    time.sleep(1)
                    cap = cv2.VideoCapture(0)
                    if cap.isOpened():
                         _, check = cap.read()
                         if check is not None:
                             reconnected = True
                             speaker.speak("Camera online.")
                             break
                
                if not reconnected:
                    print("CRITICAL: Camera reconnect failed.")
                    break
                else:
                    continue # Skip this loop iter, get fresh frame
            
            frame = cv2.flip(frame, 1) # Mirror view
            
            # B. PROCESS INPUTS
            # 1. Vision
            # Use Controller Sensitivity for "Faster Cursor" logic
            current_sens = controller.get_sensitivity()
            vision_data = vision.process_frame(frame, sensitivity=current_sens)
            
            # 2. Voice (Poll Queue)
            try:
                while not command_queue.empty():
                    msg = command_queue.get_nowait()
                    if msg['type'] == 'VOICE_COMMAND':
                        cmd = msg['payload']
                        voice_data["last_command"] = cmd
                        
                        # Controller State Update based on Keyword?
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
            if controller.current_state == SystemState.IDLE:
                 # Auto-start in Hybrid for this demo
                 controller.set_state(SystemState.HYBRID)
            
            suggested_action, confidence = arbiter.decide(vision_data, vision_data, voice_data)
            
            # Determine Source for Authority Check
            source = "GESTURE"
            if suggested_action in ["ACTION_OPEN_APP", "ACTION_TYPE_TEXT", "ACTION_SEARCH", "ACTION_QUERY", "ACTION_EXIT", "ACTION_CHAMELEON", "ACTION_CLICK", "ACTION_VOICE_REJECTED"]:
                source = "VOICE"
            
            # D. AUTHORITY CHECK (System Controller)
            is_allowed = controller.authorize_action(suggested_action, source)
            
            # Fix: Clear blocked voice commands to prevent jam
            if not is_allowed and source == "VOICE":
                 voice_data["last_command"] = ""
            
            final_action = "IDLE"
            action_data = vision_data.copy() # Start with vision data
            action_data['voice_command'] = voice_data.get('last_command', '')
            
            if is_allowed and confidence > 0.7:
                final_action = suggested_action
                
                # Special Handling for Brain Query (It needs the answer first)
                if final_action == "ACTION_QUERY":
                    # Fetch from Brain (Returns JSON now)
                    is_cmd, brain_output = brain.process_query(voice_data['last_command'])
                    
                    # Handle Structured Output
                    if isinstance(brain_output, dict):
                        b_type = brain_output.get("type", "none")
                        b_intent = brain_output.get("intent")
                        b_params = brain_output.get("parameters", {})
                        b_response = brain_output.get("response", "")
                        
                        if b_type == "system_control":
                            if b_intent == "ADJUST_SENSITIVITY":
                                direction = b_params.get("direction", "reset")
                                controller.adjust_sensitivity(direction, speaker)
                            elif b_intent == "RESET_SENSITIVITY":
                                controller.adjust_sensitivity("reset", speaker)
                            
                            # Speak response
                            if b_response:
                                speaker.speak(b_response)
                                
                            # Don't execute confusing actions if it was a system control
                            final_action = "IDLE" 

                        elif b_intent == "OPEN_APP":
                             # Convert to ACTION_OPEN_APP manually if Brain detected it better
                             final_action = "ACTION_OPEN_APP"
                             action_data['voice_command'] = f"open {b_params.get('app_name', '')}" # Simplified
                        
                        else:
                            # Standard Query Response
                            action_data['brain_response'] = b_response
                    else:
                        # Legacy string fallback (just in case)
                        action_data['brain_response'] = str(brain_output)

                # Fix 1: Voice Rejection Handling
                elif final_action == "ACTION_VOICE_REJECTED":
                    voice_data["last_command"] = "" # Clear invalid command
                    final_action = "VOICE: REJECTED" # Show on HUD
                    # optional sound? speaker.speak("Unknown.")
                    
                # E. EXECUTION (Dispatcher)
                # Only execute if it's not LOCKED (Arbiter returns locked for cooldowns)
                hud_events = []
                if final_action not in ["LOCKED", "IDLE", "VOICE: REJECTED"]:
                    try:
                        hud_events = dispatcher.execute(final_action, action_data)
                    except Exception as e:
                        if "FailSafe" in str(e):
                             print("🛑 EMERGENCY STOP TRIGGERED. Cursor reset.")
                             # Maybe reset cursor?
                        else:
                             print(f"⚠️ DISPATCH ERROR: {e}")
                    
                    # Clear voice command after successful execution to prevent looping
                    if source == "VOICE":
                        voice_data["last_command"] = ""
            
            # F. RENDER HUD
            # Pass the *Authorized* action for display
            ui_state = f"{final_action}" 
            if not is_allowed and suggested_action != "MOUSE_MOVE":
                 ui_state = f"BLOCKED ({suggested_action})"
            elif confidence <= 0.7 and suggested_action not in ["ACTION_MOUSE_MOVE", "LOCKED"]:
                 ui_state = f"REJECTED ({int(confidence*100)}%)"

            # OVERRIDE with System Message (e.g. Sensitivity)
            sys_msg = controller.get_active_message()
            if sys_msg:
                 ui_state = sys_msg
            elif is_recording:
                 ui_state = f"REC: {len(recorded_data)} SAMPLES"

            vision_data["voice_active"] = True # Always listening
                 
            processed_frame = renderer.render(frame, vision_data, ui_state, events=hud_events)
            
            cv2.imshow('Heisenberg HUD', processed_frame)
            
            # G. EXIT CONDITION
            key = cv2.waitKey(1) & 0xFF
            
            # --- TRAINING CONTROLS ---
            if key == ord('r'):
                is_recording = not is_recording
                state_msg = "🔴 RECORDING ON" if is_recording else "⚪ RECORDING OFF"
                print(state_msg)
                speaker.speak(state_msg)
                
            if is_recording:
                label = -1
                if key == ord('0'): label = 0 # NONE
                elif key == ord('1'): label = 1 # OPEN
                elif key == ord('2'): label = 2 # FIST
                elif key == ord('3'): label = 3 # PEACE
                elif key == ord('4'): label = 4 # POINT
                
                if label != -1:
                    # Get raw landmarks from Vision Data
                    rhs = vision_data.get('hands', {}).get('Right', {})
                    raw_landmarks = rhs.get('raw_landmarks')
                    
                    if raw_landmarks and len(raw_landmarks) == 42:
                        recorded_data.append(raw_landmarks)
                        recorded_labels.append(label)
                        print(f"✅ Sample Saved. Label: {label}. Total: {len(recorded_data)}")
                        speaker.speak(f"Saved {label}")
                    else:
                        print("⚠️ No Hand Detected for Training.")
                        speaker.speak("No hand.")
                    
            if key == ord('t'):
                if len(recorded_data) > 5:
                    print("🧠 TRAINING NEURAL NET...")
                    speaker.speak("Training neural network.")
                    arbiter.train_neural_net(recorded_data, recorded_labels)
                    speaker.speak("Training complete.")
                    recorded_data = [] # Clear after train
                    recorded_labels = []
                else:
                     print("⚠️ Not enough data to train.")
            
            if key == ord('c'):
                recorded_data = []
                recorded_labels = []
                print("🗑️ Training Data Cleared.")
                speaker.speak("Data cleared.")
            
            # --- END TRAINING CONTROLS ---
            
            if key == ord('q'):
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
