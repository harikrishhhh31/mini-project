import pyautogui
import time
import os
import pyperclip
from .config import *

class ActionDispatcher:
    def __init__(self, speaker=None):
        pyautogui.FAILSAFE = True
        self.screen_w, self.screen_h = pyautogui.size()
        self.speaker = speaker # The Voice Output Thread
        
        # State for "Drag and Drop"
        self.is_dragging = False
        self.last_click_time = 0

    def feedback(self, text):
        """Helper to speak only if speaker is attached"""
        if self.speaker:
            self.speaker.speak(text)

    def execute(self, action, data):
        """
        Executes the command decided by the Arbiter.
        """
        # 1. STANDARD MOUSE CONTROL (With Bimanual Click Logic)
        if action == "ACTION_MOUSE_MOVE":
            # ... (Mouse logic remains same) ...
            x, y = data.get('cursor', (0,0))
            if x and y:
                pyautogui.moveTo(x, y, _pause=False)
            
            hands = data.get('hands', {})
            right = hands.get('Right', {})
            left = hands.get('Left', {})

            # A. RIGHT CLICK: Right Hand Middle Pinch
            if right.get('pinch_middle', 1000) < CLICK_DIST:
                 if time.time() - self.last_click_time > 0.5: # Debounce
                     pyautogui.rightClick()
                     self.last_click_time = time.time()
                     print("🖱️ RIGHT CLICK")
                     # self.feedback("Menu") # Too chatty for clicks?

            # B. LEFT CLICK: Left Hand Middle Pinch (Sniper Mode)
            if left.get('pinch_middle', 1000) < CLICK_DIST:
                 if time.time() - self.last_click_time > 0.3:
                     pyautogui.click()
                     self.last_click_time = time.time()
                     print("🖱️ LEFT CLICK (Bimanual)")

            # C. DRAG / PRIMARY: Right Hand Index Pinch
            if right.get('pinch_index', 1000) < CLICK_DIST:
                if not self.is_dragging:
                    pyautogui.mouseDown()
                    self.is_dragging = True
            else:
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False

        # 2. ELITE FEATURES
        elif action == "ACTION_SCROLL_GRAB":
            dy = data.get('velocity_y', 0)
            pyautogui.scroll(int(dy / 10)) 
            
        elif action == "ACTION_THROW":
           print("🚀 EXECUTING TELEPORT THROW NETWORK REQUEST...")
           # Simulate Windows Share / Dictation
           pyautogui.hotkey('win', 'h')
           self.feedback("Transferring Data.")
           
        elif action == "ACTION_SILENCE":
            pyautogui.press('volumemute')
            self.feedback("Silence Protocol Active.")
            
        elif action == "ACTION_SHADOW_CLONE":
            pyautogui.hotkey('win', 'left') 
            self.feedback("Workspace Splintered.")
            
        elif action == "ACTION_PEEK":
            print("👁️ PEEK MODE ACTIVE")
            # Aero Peek: Win + Comma (Hold briefly to see desktop)
            pyautogui.hotkey('win', ',')
            
        elif action == "ACTION_CHAMELEON":
            print("🎨 CHAMELEON MODE ACTIVATE")
            try:
                x, y = pyautogui.position()
                pixel_color = pyautogui.pixel(x, y)
                hex_color = '#{:02x}{:02x}{:02x}'.format(*pixel_color)
                pyperclip.copy(hex_color)
                print(f"🎨 COLOR COPIED: {hex_color} at ({x}, {y})")
                self.feedback(f"Color {hex_color} copied.")
            except Exception as e:
                print(f"🎨 CHAMELEON ERROR: {e}")
                self.feedback("Color capture failed.")
            
        elif action == "ACTION_SQUINT_SCALE":
            print("🔍 SQUINT DETECTED: MAGNIFIER ZOOM")
            # Windows Magnifier: Win + Plus
            # Note: '+' usually requires shift if not using keypad, 
            # but pyautogui handles generic '+' as the key. 
            # If that fails, might need to try '=' or numpad key.
            pyautogui.hotkey('win', '+')
            
        elif action == "ACTION_PROX_ZOOM":
            print("🔭 PROXIMITY ZOOM: FOCUS MODE")
            # Browser / App Zoom: Ctrl + Plus
            pyautogui.hotkey('ctrl', '+')

        elif action == "ACTION_OPEN_APP":
            cmd = data.get('voice_command', '')
            app = cmd.replace('open', '').strip()
            if app:
                self.feedback(f"Opening {app}")
                print(f"📂 OPENING APP: {app}")
                pyautogui.press('win')
                time.sleep(0.1)
                pyautogui.write(app)
                time.sleep(0.1)
                pyautogui.press('enter')

        elif action == "ACTION_TYPE_TEXT":
            cmd = data.get('voice_command', '')
            text = cmd.replace('type', '').replace('write', '').strip()
            if text:
                self.feedback("Dictating.")
                print(f"⌨️ TYPING: {text}")
                pyautogui.write(text + " ")

        elif action == "ACTION_SEARCH":
            # If it's a direct search command
            cmd = data.get('voice_command', '')
            query = cmd.replace('search', '').strip()
            if query:
                self.feedback(f"Searching the web for {query}")
                print(f"🔍 SEARCHING: {query}")
                pyautogui.hotkey('ctrl', 't')
                time.sleep(0.1)
                pyautogui.write(query)
                pyautogui.press('enter')

        elif action == "ACTION_QUERY":
            answer = data.get('brain_response', '')
            if answer:
                print(f"🧠 BRAIN: {answer}")
                
                # INTELLIGENT OUTPUT SELECTOR
                # If answer is short (simple fact), speak it.
                # If answer is long (Code, Math Proof), write it to a file and show it.
                is_complex = len(answer) > 200 or "```" in answer or "public class" in answer or "import" in answer
                
                if is_complex:
                    self.feedback("Visualizing data on screen.")
                    # Save to file
                    slate_path = "heisenberg_output.txt"
                    with open(slate_path, "w", encoding="utf-8") as f:
                        f.write("--------------------------------------------------\n")
                        f.write("   HEISENBERG NEURAL OUTPUT   \n")
                        f.write("--------------------------------------------------\n\n")
                        f.write(answer)
                    
                    # Open file (Windows Default, usually Notepad)
                    os.startfile(slate_path)
                else:
                    # Simple answer, just speak it
                    self.feedback(answer)

        elif action == "ACTION_EXIT":
            self.feedback("Shutting down core systems.")
            pass
