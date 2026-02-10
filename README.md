# Heisenberg: A Multimodal Assistive Interface for Contactless Computing

**Heisenberg** is a prototype Human-Computer Interaction (HCI) system designed to enable contactless computer operation. By integrating computer vision and voice recognition, the system provides alternative input modalities for users with limited upper-limb mobility, spinal cord injuries, or motor impairments that make traditional mouse and keyboard interaction difficult or impossible.

The project aims to create a robust, error-tolerant interface that translates natural bio-mechanical cues (hand tracking, facial expressions, voice commands) into precise operating system inputs.

---

## 1. System Overview & Design Philosophy

The system is built upon the principle of **Multi-Modal Redundancy**: critical actions can be performed through multiple independent channels (voice or gesture), ensuring that if one modality fails or causes fatigue, the user has a backup method.

### Primary User Group
Individuals who retain partial motor control of the head or hands but lack the fine motor skills or range of motion required for physical peripherals.

### Interaction Loop
The system follows a strict feedback loop to ensure user confidence:
1.  **User Action**: The user performs a gesture (e.g., pinch) or vocalizes a command.
2.  **System Interpretation**: The `Gesture Arbiter` and `Vision Core` analyze the input against pre-defined confidence thresholds.
3.  **Visual/Audio Feedback**: The `Hud Renderer` displays a visual confirmation (e.g., skeletal overlay change), or the system provides auditory cues ("Click confirmed"), complying with WCAG accessibility principles for non-visual feedback.
4.  **Execution & Recovery**: The command is executed. If the confidence is low, the action is discarded to prevent erroneous inputs, allowing the user to re-attempt the gesture.

---

## 2. Input Modalities

### A. Computer Vision (Kinematic Input)
Utilizing MediaPipe for real-time tracking, the system maps relative hand coordinates to the screen cursor using a proprietary smoothing algorithm (`OneEuroFilter`) to filter out tremors and jitters common in motor impairments.

| Feature | Interaction Design | Assistive Function |
| :--- | :--- | :--- |
| **Cursor Navigation** | Hand tracking with velocity smoothing. | Replaces physical mouse movement. |
| **Primary Click** | Thumb-Index Pinch (Left Hand). | Alternative to left-click button. |
| **Context Click** | Thumb-Middle Pinch (Right Hand). | Alternative to right-click button. |
| **Drag Operations** | Thumb-Index Pinch + Hold. | Enables window movement and file selection. |
| **Inertial Scroll** | Vertical velocity thresholding. | Scroll without repetitive wheel movement. |

### B. Bio-Adaptive Triggers (Facial Analysis)
These passive triggers continuously monitor user state to provide assistive visual aids without explicit commands.

-   **Visual Magnification (Squint Detection)**: Detecting a reduction in Eye Aspect Ratio (EAR) triggers the System Magnifier. This assists users with visual impairments or allows detailed viewing without leaning forward.
-   **Focus Mode (Proximity Detection)**: Measuring the Z-depth of facial landmarks triggers a "Focus" state (Browser Zoom) when the user leans towards the screen, mimicking natural human vision accommodation.

### C. Voice Control (Semantic Input)
A secondary layer for complex commands that are difficult to encode in gestures.

-   **System Control**: *"Stop"*, *"Silence"* (Mute Audio).
-   **Application Management**: *"Open Calculator"*, *"Open Notepad"*.
-   **Text Input**: Dictation mode for hands-free typing.
-   **Information Retrieval**: Fallback web-search for quick information access.

---

## 3. Advanced Assistive Actions

The system abstracts complex keyboard shortcuts into discrete, macroscopic gestures to reduce cognitive load and physical strain.

-   **Inertial Transfer (High Velocity Gesture)**: A rapid hand movement simulates `Win + H` (Share/Dictation), simplifying the initiation of data transfer protocols.
-   **Layout Management (Gesture Parsing)**: A specific "Split" gesture triggers `Win + Left`, allowing users to snap windows and organize their workspace with a single gross motor movement.
-   **Visibility (Peek)**: Lifting a flat hand triggers Windows Aero Peek, providing a quick overview of the desktop without minimizing windows.
-   **Color Sampling**: A voice-triggered context action ("Color") samples the pixel under the cursor, aiding in design tasks without requiring precise mouse positioning.

---

## 4. Architecture

The codebase is modularized to support independent development of input streams:

-   `vision_core.py`: Handling landmark extraction and noise filtering.
-   `voice_core.py`: Asynchronous speech recognition engine.
-   `gesture_arbiter.py`: Deterministic state machine that resolves conflicts between inputs (e.g., ignoring voice while a gesture is active).
-   `action_dispatcher.py`: Interface with the Operating System API (Win32/PyAutoGUI).
-   `neural_architect.py`: *[Experimental]* Prototype code for a local Large Language Model (LLM) to provide context-aware predictive text and assistance.

---

## 5. Limitations & Constraints

As a prototype, the system has several known limitations that affect its viability in a production environment:

1.  **Environmental Sensitivity**: Performance is highly dependent on lighting conditions. Low light or backlighting significantly degrades tracking accuracy.
2.  **Gorilla Arm Syndrome**: Prolonged use of mid-air gestures causes rapid arm fatigue. The system is currently best suited for burst interactions rather than sustained usage.
3.  **False Positives**: "Squint" and "pinch" detection may occasionally trigger falsely during normal behavior (e.g., blinking or resting hands).
4.  **Hardware Dependency**: Requires a functional webcam and microphone. Processing latency is dependent on CPU/GPU performance.

---

## 6. Installation

### Requirements
-   Python 3.8+
-   Standard Webcam & Microphone

### Setup
```bash
pip install -r requirements.txt
```
*(Dependencies include `opencv-python`, `mediapipe`, `pyautogui`, `SpeechRecognition`, etc.)*

### Execution
Run the main entry point to initialize the gesture and voice threads:
```bash
python main_file.py
```

---

## 8. Project Status (Feb 2026)

### ✅ Completed & Shippable
- **Core Architecture**: Full separation of concerns (Perception → Decision → Authority → Execution).
- **System Controller**: State-based authority layer (IDLE, VOICE, GESTURE, HYBRID) is fully operational.
- **Multimodal Input**: concurrent processing of Hand Tracking (MediaPipe) and Voice Commands (SpeechRecognition).
- **Safety protocols**: `pyautogui` Fail-Safe enabled; dedicated ACTION_EXIT paths.
- **Feedback Loop**: HUD rendering and Text-to-Speech feedback are synchronized with system state.

### 🚧 In Progress / Experimental
- **Neural Architect**: The custom `neural_architect.py` (PyTorch MoE model) is implemented but the system currently defaults to `llama.cpp` bindings for stability.
- **Calibration**: User-specific threshold tuning is currently hardcoded for demonstration.

---

## 7. Future Work
-   **Fatigue Reduction**: Implementation of "Micro-gestures" that require minimal range of motion.
-   **Local Intelligence**: Full integration of the local LLM to allow the system to predict user intent and automate repetitive workflows.
-   **Calibration**: User-specific calibration profiles to account for varying ranges of motion and asymmetry in motor control
