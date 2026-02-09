# 🧠 Heisenberg (Elite System) - [Work In Progress]

**Heisenberg** is an advanced, multimodal AI assistant designed to redefine human-computer interaction. It combines **Computer Vision** and **Voice Recognition** to create a seamless, "Iron Man" style interface. 

Currently, the system enables control of your PC with hand gestures, bio-adaptive triggers (squinting/leaning), and natural voice commands.

> **Note**: This project is currently under active development. Some advanced AI features (Local LLM integration) are in the experimental phase.

---

## ✨ Implemented Features

### 1. 🖱️ Advanced Gesture Control (Vision Core)
Navigate your computer without a mouse. The system tracks your hands and face in real-time using MediaPipe.
- **Mouse Movement**: Move your hand to control the cursor with physics-based smoothing.
- **Clicks**: 
  - **Left Click**: Pinch Left Hand (Sniper Mode).
  - **Right Click**: Pinch Right Hand Middle Finger.
  - **Drag & Drop**: Pinch Right Index Finger and move.
- **Scroll**: Vertical hand velocity triggers scrolling.

### 2. 🎭 Special "Jutsu" & Bio-Adaptive Actions
- **Teleport Throw**: Make a fist and "throw" your hand to simulate a file transfer/share (`Win + H`).
- **Shadow Clone**: "Peace Split" gesture (✌️ -> 🖐️) snaps the window to the left (`Win + Left`).
- **Peek Mode**: Lift a flat hand to transparently view the desktop (Aero Peek).
- **Chameleon Mode**: Point at any pixel and say *"Color"*. The system captures the color and copies the HEX code.
- **Squint-to-Zoom**: Squint your eyes to automatically trigger the Magnifier.
- **Proximity Focus**: Lean your face closer to the screen to zoom into the active window/browser.

### 3. 🎤 Intelligent Voice Command (Voice Core)
- **App Launching**: *"Open Calculator"*, *"Open Notepad"*.
- **Dictation**: *"Type Hello World"*.
- **Web Search**: *"Search for quantum physics"*.
- **System Control**: *"Stop"*, *"Exit"*, *"Silence"*.

### 4. 🌐 Basic Knowledge Retrieval (Brain Core)
- **Web Search Fallback**: Currently, the system uses a DuckDuckGo web scraper to answer basic "What/Who/How" questions if no local model is loaded.
- **Complex Output**: Code snippets and long answers are written to a text file for easier reading.

---

## 🚧 In Development / Roadmap

### 🧠 Local Neural Brain (LLM Integration)
*Status: Experimental / Not Fully Implemented*
- We are working on integrating a **Local Large Language Model (Llama-3 / Mistral)** to replace the web scraper.
- The goal is to have offline, private, and highly intelligent conversations without internet access.
- **Neural Architect**: We have the model definitions (`neural_architect.py`) for a custom MoE (Mixture of Experts) architecture, but it is currently a research component and not yet the active brain of the system.

---

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.8+
- Webcam
- Microphone

### 1. Installation
```bash
pip install -r requirements.txt
```
*Key libraries: `opencv-python`, `mediapipe`, `pyautogui`, `SpeechRecognition`, `pyttsx3`, `beautifulsoup4`, `pyperclip`.*

### 2. Running the System
Run the main system functionality:

```bash
python main_file.py
```
*(Replace `main_file.py` with your actual entry point script, e.g., `elite_system_runner.py` or similar if applicable)*

---

## 📂 Project Structure

- **`action_dispatcher.py`**: Executes OS-level commands (Mouse, Keyboard). **[Active]**
- **`gesture_arbiter.py`**: Decides the winning action from Vision/Voice inputs. **[Active]**
- **`vision_core.py`**: Hand and Face tracking. **[Active]**
- **`voice_core.py`**: Speech recognition. **[Active]**
- **`hud_renderer.py`**: Draws the UI overlay. **[Active]**
- **`brain_core.py`**: Handles queries (currently Web Search). **[WIP]**
- **`neural_architect.py`**: Custom PyTorch LLM definitions. **[Research/Inactive]**
- **`config.py`**: Configuration settings.

---

## ⚠️ Disclaimer
This system uses `pyautogui` with `FAILSAFE = False` to allow full screen traversing. The "Throw" and "Squint" features rely on heuristic thresholds which may need tuning in `config.py` for your specific camera setup.
