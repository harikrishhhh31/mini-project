import threading
import speech_recognition as sr

import queue

class VoiceCore(threading.Thread):
    def __init__(self, command_queue):
        super().__init__()
        self.command_queue = command_queue # Queue to send messages to Main Thread
        self.daemon = True # Kills thread when main app closes
        self.is_listening = True
        
        # Audio Setup
        self.recognizer = sr.Recognizer()
        
    def run(self):
        """The Main Loop of the Voice Thread"""
        print("🎤 Voice Core: Online & Listening...")
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening:
                try:
                    # Listen for audio (this blocks THIS thread, but not the Main one)
                    audio = self.recognizer.listen(source, timeout=None)
                    
                    # Convert to text
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"👂 Heard: '{command}'")
                    
                    # Send to the central processing queue
                    self.command_queue.put({"type": "VOICE_COMMAND", "payload": command})
                    
                    # Immediate Feedback (Preserved via Queue)
                    if "heisenberg" in command:
                        self.command_queue.put({"type": "FEEDBACK", "payload": "Say my name."})
                        
                except sr.UnknownValueError:
                    pass # Just couldn't understand, ignore.
                except sr.RequestError:
                    print("⚠️ Network Error for Voice")
                except Exception as e:
                    print(f"⚠️ Voice Error: {e}")

    def stop(self):
        self.is_listening = False
