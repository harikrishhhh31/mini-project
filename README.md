# Heisenberg: A Multimodal Assistive Interface for Contactless Computing

**Heisenberg** is a prototype Human-Computer Interaction (HCI) system designed to enable contactless computer operation. By integrating computer vision, voice recognition, and local neural intelligence, the system provides alternative input modalities for users with limited upper-limb mobility or motor impairments.

The project aims to create a robust, error-tolerant interface that translates natural bio-mechanical cues (hand tracking, facial expressions, voice commands) into precise operating system inputs.

---

## 1. System Overview & Design Philosophy

The system is built upon the principle of **Hybrid Neuro-Symbolic Control**: combining deterministic rules (Heuristics) for safety and speed with probabilistic AI (Neural Networks) for adaptability.

### Interaction Loop
The system follows a strict feedback loop to ensure user confidence:
1.  **Perception**: `Vision Core` tracks 42 hand landmarks and facial cues; `Voice Core` listens for commands.
2.  **Intelligence**: 
    *   **Neural Engine**: Classifies complex hand shapes (Open, Fist, Peace, Point).
    *   **Heuristic Arbiter**: Fallback logic for physics-based actions (Throw, Peek).
    *   **Brain Core**: LLM parsing for natural language queries.
3.  **Authority**: `System Controller` validates actions against the current state and safety rules.
4.  **Feedback**: Visual HUD updates (Mode, Recording Status, Sensitivity) and Auditory cues.

---

## 2. Input Modalities

### A. Neural & Kinematic Gestures (Vision)
Utilizing MediaPipe for tracking and a Custom PyTorch Neural Network for classification.

| Feature | Trigger | Function |
| :--- | :--- | :--- |
| **Mouse Navigation** | "Point" Gesture / Index Finger | Hand tracking with dynamic sensitivity scaling. |
| **Primary Click** | "Fist" Gesture / Pinch | Left-click execution. |
| **Context Menu** | "Peace" Gesture | Right-click / Mode Switch. |
| **Release/Stop** | "Open Palm" Gesture | Stops dragging or resets state. |
| **Inertial Throw** | High Velocity Fist | Rapidly moves windows/cursor. |

### B. Smart Voice Control (Semantic)
A secondary layer for complex commands and system tuning.

*   **Sensitivity Control**: *"Increase sensitivity"*, *"Make cursor faster"*, *"Reset sensitivity"*. (Safe 0.5x - 2.0x range).
*   **System Control**: *"Stop"*, *"Exit Heisenberg"*.
*   **App Management**: *"Open Calculator"*, *"Type [text]"*.
*   **Knowledge**: *"What is [topic]?"* (Powered by Local LLM / Web Fallback).

### C. In-App Training (New!)
Users can define their own gesture triggers at runtime without coding.
*   **'R'**: Toggle Recording Mode.
*   **'0'-'4'**: Label current hand pose (0: None, 1: Open, 2: Fist, 3: Peace, 4: Point).
*   **'T'**: Train the Neural Network immediately on collected data.
*   **'C'**: Clear training data.

---

## 3. Advanced Features

### Safe Sensitivity System
*   **Step-Based Adjustment**: Increments of 0.1x to prevent loss of control.
*   **Visual Feedback**: HUD displays "Sensitivity: 1.X" for 2 seconds on change.
*   **Zoom/Gain Model**: Sensitivity > 1.0 expands the effective input range relative to screen center.

### Bio-Adaptive Triggers
*   **Squint Detection**: Reduces Eye Aspect Ratio (EAR) to trigger automatic zoom.
*   **Leaning**: Detects head Z-depth to engage "Focus Mode".

---

## 4. Architecture

The codebase is modularized for scalability:

*   `main_file.py`: The central event loop orchestrating Input -> Decision -> Execution.
*   `vision_core.py`: Extracting 42 raw landmarks and calculating velocities.
*   `gesture_network.py`: PyTorch Neural Network implementation and Training Engine.
*   `gesture_arbiter.py`: The decision brain that weighs Neural predictions vs Heuristics.
*   `brain_core.py`: Handling Natural Language Processing (LLM) with strict JSON schema enforcement.
*   `system_controller.py`: Managing State (IDLE, VOICE, GESTURE), Safety Bounds, and Persistent Settings.
*   `hud_renderer.py`: Drawing the Sci-Fi Overlay, Skeleton tracking, and Status messages.

---

## 5. Status (Feb 2026) - ✅ 100% COMPLETE

### Completed Features
*   **Neural Network Integration**: Fully active `GestureNet` with real-time inference.
*   **Self-Correction**: In-app data collection and training pipeline.
*   **Safe Sensitivity**: Voice-controlled cursor speed with visual confirmation.
*   **Hybrid Arbiter**: Seamless switching between ML predictions and hard-coded physics rules.
*   **Robust Error Handling**: Camera auto-reconnect, JSON parsing fallbacks, and Thread-safe queues.

---

## 6. Installation & Run

1.  **Install Dependencies**:
    ```bash
    pip install opencv-python mediapipe torch numpy pyaudio SpeechRecognition pyttsx3
    ```

2.  **Run System**:
    ```bash
    python main_file.py
    ```

3.  **Controls**:
    *   **'Q'**: Quit.
    *   **'R'**: Record Training Data.
    *   **'T'**: Train Model.
