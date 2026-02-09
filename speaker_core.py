import threading
import pyttsx3
import queue

class SpeakerCore(threading.Thread):
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.daemon = True
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 170) # Fast, professional speed
        
        # Select a good voice if available (usually Index 1 is female/softer, 0 is male)
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[0].id) # 0 for Male (Jarvis/Heisenberg style)

    def speak(self, text):
        """Add text to the speech queue (Non-blocking)"""
        self.queue.put(text)

    def run(self):
        """Consumer loop"""
        while True:
            text = self.queue.get()
            if text is None: break # Sentinel to stop
            
            try:
                print(f"🗣️ HEISENBERG: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Speaker Error: {e}")
            
            self.queue.task_done()
