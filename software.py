"""
Heisenberg Control Software - Desktop Settings Interface
pywebview-based professional control center for Heisenberg system
"""

import os
import sys
import time
import socket
import threading
import requests
import webview
from settings_manager import load_settings, get_port

class HeisenbergAPI:
    """JavaScript API bridge for the web interface"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.preview_active = False
        self.countdown_thread = None
        self.remaining_time = 120
    
    def get_settings(self):
        """Get current settings from server"""
        try:
            response = requests.get(f"{self.base_url}/settings", timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return load_settings()  # Fallback to local file
    
    def preview_settings(self, sensitivity, mode, speech_speed):
        """Apply preview settings"""
        try:
            payload = {
                "sensitivity": float(sensitivity) if sensitivity else None,
                "mode": mode if mode else None,
                "speech_speed": float(speech_speed) if speech_speed else None
            }
            response = requests.post(
                f"{self.base_url}/settings/preview",
                json=payload,
                timeout=2
            )
            if response.status_code == 200:
                self.preview_active = True
                self.remaining_time = 120
                self.start_countdown()
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def commit_settings(self):
        """Commit preview settings"""
        try:
            response = requests.post(f"{self.base_url}/settings/commit", timeout=2)
            if response.status_code == 200:
                self.preview_active = False
                self.remaining_time = 0
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def revert_settings(self):
        """Revert to original settings"""
        try:
            response = requests.post(f"{self.base_url}/settings/revert", timeout=2)
            if response.status_code == 200:
                self.preview_active = False
                self.remaining_time = 0
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def start_countdown(self):
        """Start the 120s countdown in background"""
        if self.countdown_thread and self.countdown_thread.is_alive():
            return
        
        def countdown():
            while self.preview_active and self.remaining_time > 0:
                time.sleep(1)
                self.remaining_time -= 1
                if window:
                    try:
                        window.evaluate_js(f"updateCountdown({self.remaining_time})")
                    except:
                        pass
            
            if self.remaining_time <= 0 and self.preview_active:
                # Auto-revert triggered
                self.revert_settings()
                if window:
                    try:
                        window.evaluate_js("showAutoRevertMessage()")
                    except:
                        pass
        
        self.countdown_thread = threading.Thread(target=countdown, daemon=True)
        self.countdown_thread.start()
    
    def get_remaining_time(self):
        """Get remaining countdown time"""
        return self.remaining_time if self.preview_active else 0


# HTML/CSS/JS Frontend
HTML_CONTENT = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Heisenberg Multimodal Assistive</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
            border-bottom: 2px solid #00d4ff;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
            color: #00d4ff;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff00;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .container {
            display: flex;
            min-height: calc(100vh - 70px);
        }
        
        .sidebar {
            width: 250px;
            background: #111;
            border-right: 1px solid #333;
            padding: 20px 0;
        }
        
        .nav-item {
            padding: 15px 25px;
            cursor: pointer;
            transition: all 0.3s;
            border-left: 3px solid transparent;
        }
        
        .nav-item:hover {
            background: #1a1a2e;
            border-left-color: #00d4ff;
        }
        
        .nav-item.active {
            background: #1a1a2e;
            border-left-color: #00d4ff;
            color: #00d4ff;
        }
        
        .content {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        
        .section {
            display: none;
        }
        
        .section.active {
            display: block;
        }
        
        .section-title {
            font-size: 20px;
            margin-bottom: 25px;
            color: #00d4ff;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
        
        .setting-group {
            background: #111;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .setting-label {
            display: block;
            margin-bottom: 10px;
            color: #aaa;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .setting-value {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        input[type="range"] {
            flex: 1;
            -webkit-appearance: none;
            height: 6px;
            background: #333;
            border-radius: 3px;
            outline: none;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            background: #00d4ff;
            border-radius: 50%;
            cursor: pointer;
        }
        
        .value-display {
            min-width: 60px;
            text-align: center;
            background: #1a1a2e;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 16px;
            color: #00d4ff;
        }
        
        select {
            width: 100%;
            padding: 10px;
            background: #1a1a2e;
            border: 1px solid #00d4ff;
            color: #ffffff;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
        }
        
        select option {
            background: #1a1a2e;
            color: #ffffff;
            padding: 10px;
        }
        
        select:focus {
            outline: none;
            border-color: #00d4ff;
            box-shadow: 0 0 5px rgba(0, 212, 255, 0.3);
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #00d4ff;
            color: #000;
        }
        
        .btn-primary:hover {
            background: #00b8e0;
        }
        
        .btn-success {
            background: #00ff88;
            color: #000;
        }
        
        .btn-success:hover {
            background: #00e67a;
        }
        
        .btn-danger {
            background: #ff4444;
            color: #fff;
        }
        
        .btn-danger:hover {
            background: #e60000;
        }
        
        .countdown-container {
            display: none;
            background: #1a1a2e;
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
        }
        
        .countdown-container.active {
            display: block;
        }
        
        .countdown-timer {
            font-size: 48px;
            font-weight: bold;
            color: #ff8800;
            margin: 10px 0;
        }
        
        .countdown-message {
            color: #aaa;
            margin-bottom: 15px;
        }
        
        /* Actions Guide Styles */
        .actions-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        
        .actions-table th {
            background: #1a1a2e;
            color: #00d4ff;
            padding: 15px;
            text-align: left;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
            border-bottom: 2px solid #333;
        }
        
        .actions-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #222;
            font-size: 14px;
        }
        
        .actions-table tr:hover {
            background: #1a1a2e;
        }
        
        .section-header {
            background: #16213e;
            color: #00d4ff;
            padding: 10px 15px;
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
        }
        
        .live-value {
            display: inline-block;
            background: #00d4ff;
            color: #000;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 10px;
        }
        
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-overlay.active {
            display: flex;
        }
        
        .modal {
            background: #1a1a2e;
            border: 2px solid #ff4444;
            border-radius: 8px;
            padding: 30px;
            max-width: 400px;
            text-align: center;
        }
        
        .modal h3 {
            color: #ff4444;
            margin-bottom: 15px;
        }
        
        .modal p {
            color: #aaa;
            margin-bottom: 20px;
        }
        
        .modal-buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Heisenberg Multimodal Assistive</h1>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span>System Online</span>
        </div>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="nav-item active" onclick="showSection('settings')">Settings</div>
            <div class="nav-item" onclick="showSection('actions')">How to Use</div>
        </div>
        
        <div class="content">
            <!-- Settings Section -->
            <div id="settings" class="section active">
                <h2 class="section-title">System Settings</h2>
                
                <div class="setting-group">
                    <label class="setting-label">Sensitivity (Cursor Speed)</label>
                    <div class="setting-value">
                        <input type="range" id="sensitivity" min="0.5" max="2.0" step="0.1" value="1.0" oninput="updateValue('sensitivity', this.value)">
                        <span class="value-display" id="sensitivity-value">1.0x</span>
                        <span class="live-value" id="sensitivity-live">LIVE</span>
                    </div>
                </div>
                
                <div class="setting-group">
                    <label class="setting-label">System Mode</label>
                    <select id="mode" onchange="updateMode(this.value)">
                        <option value="hybrid">Hybrid (Gesture + Voice)</option>
                        <option value="gesture">Gesture Only</option>
                        <option value="voice">Voice Only</option>
                    </select>
                </div>
                
                <div class="setting-group">
                    <label class="setting-label">Speech Speed</label>
                    <div class="setting-value">
                        <input type="range" id="speech_speed" min="0.5" max="2.0" step="0.1" value="1.0" oninput="updateValue('speech_speed', this.value)">
                        <span class="value-display" id="speech_speed-value">1.0x</span>
                    </div>
                </div>
                
                <div class="button-group" id="button-group-main">
                    <button class="btn btn-primary" id="save-btn" onclick="saveChanges()">Save Changes</button>
                    <button class="btn btn-success" id="keep-btn" onclick="commitChanges()" style="display:none;">Keep Changes</button>
                    <button class="btn btn-danger" id="revert-btn" onclick="revertChanges()" style="display:none;">Revert</button>
                </div>
                
                <div id="countdown" class="countdown-container">
                    <div class="countdown-message">Preview Mode Active - Auto-revert in:</div>
                    <div class="countdown-timer" id="countdown-timer">120s</div>
                    <div class="countdown-message">Click "Keep Changes" to save permanently</div>
                </div>
            </div>
            
            <!-- Actions Guide Section -->
            <div id="actions" class="section">
                <h2 class="section-title">How to Use Heisenberg Multimodal Assistive</h2>
                
                <div class="intro-text" style="color: #ccc; margin-bottom: 25px; line-height: 1.6;">
                    Heisenberg Multimodal Assistive lets you control your computer without touching it! Use hand gestures, voice commands, or facial expressions.
                </div>
                
                <div class="section-header">Hand Gestures - Move Your Mouse</div>
                <div class="simple-guide">
                    <div class="guide-item">
                        <div class="guide-icon">☝️</div>
                        <div class="guide-content">
                            <div class="guide-title">Point with Index Finger</div>
                            <div class="guide-desc">Move your mouse cursor around the screen</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">✊</div>
                        <div class="guide-content">
                            <div class="guide-title">Make a Fist</div>
                            <div class="guide-desc">Click and hold to drag items</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">✌️</div>
                        <div class="guide-content">
                            <div class="guide-title">Peace Sign (Two Fingers)</div>
                            <div class="guide-desc">Right-click to open menus</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">✋</div>
                        <div class="guide-content">
                            <div class="guide-title">Open Palm</div>
                            <div class="guide-desc">Release and stop dragging</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">🚀</div>
                        <div class="guide-content">
                            <div class="guide-title">Fast Hand Movement</div>
                            <div class="guide-desc">Quickly move windows around</div>
                        </div>
                    </div>
                </div>
                
                <div class="section-header">Voice Commands - Just Say It</div>
                <div class="simple-guide">
                    <div class="guide-item">
                        <div class="guide-icon">🗣️</div>
                        <div class="guide-content">
                            <div class="guide-title">"Open [App Name]"</div>
                            <div class="guide-desc">Example: "Open Calculator" or "Open Browser"</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">⌨️</div>
                        <div class="guide-content">
                            <div class="guide-title">"Type [What You Want]"</div>
                            <div class="guide-desc">Example: "Type Hello World"</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">🔍</div>
                        <div class="guide-content">
                            <div class="guide-title">"Search [Topic]"</div>
                            <div class="guide-desc">Example: "Search weather today"</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">🎨</div>
                        <div class="guide-content">
                            <div class="guide-title">Say "Color"</div>
                            <div class="guide-desc">Copies the color under your cursor</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">❓</div>
                        <div class="guide-content">
                            <div class="guide-title">"What is [Question]"</div>
                            <div class="guide-desc">Example: "What is the capital of France?"</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">⚡</div>
                        <div class="guide-content">
                            <div class="guide-title">"Faster" or "Slower"</div>
                            <div class="guide-desc">Adjust how fast the cursor moves</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">🛑</div>
                        <div class="guide-content">
                            <div class="guide-title">"Exit Heisenberg Interface"</div>
                            <div class="guide-desc">Closes the program</div>
                        </div>
                    </div>
                </div>
                
                <div class="section-header">Face Expressions - Special Powers</div>
                <div class="simple-guide">
                    <div class="guide-item">
                        <div class="guide-icon">👀</div>
                        <div class="guide-content">
                            <div class="guide-title">Squint Your Eyes</div>
                            <div class="guide-desc">Zooms in like a magnifying glass</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">🧘</div>
                        <div class="guide-content">
                            <div class="guide-title">Lean Forward</div>
                            <div class="guide-desc">Makes everything bigger (focus mode)</div>
                        </div>
                    </div>
                </div>
                
                <div class="section-header">Extra Features</div>
                <div class="simple-guide">
                    <div class="guide-item">
                        <div class="guide-icon">🔇</div>
                        <div class="guide-content">
                            <div class="guide-title">Silence Mode</div>
                            <div class="guide-desc">Mutes your computer</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">👁️</div>
                        <div class="guide-content">
                            <div class="guide-title">Peek at Desktop</div>
                            <div class="guide-desc">Quickly see what's behind your windows</div>
                        </div>
                    </div>
                    <div class="guide-item">
                        <div class="guide-icon">📜</div>
                        <div class="guide-content">
                            <div class="guide-title">Scroll Pages</div>
                            <div class="guide-desc">Move up and down on websites</div>
                        </div>
                    </div>
                </div>
                
                <style>
                    .simple-guide {
                        margin-bottom: 30px;
                    }
                    .guide-item {
                        display: flex;
                        align-items: center;
                        padding: 15px;
                        background: #111;
                        border: 1px solid #333;
                        border-radius: 8px;
                        margin-bottom: 10px;
                        transition: background 0.3s;
                    }
                    .guide-item:hover {
                        background: #1a1a2e;
                    }
                    .guide-icon {
                        font-size: 24px;
                        margin-right: 15px;
                        min-width: 40px;
                        text-align: center;
                    }
                    .guide-title {
                        color: #00d4ff;
                        font-weight: 600;
                        margin-bottom: 5px;
                    }
                    .guide-desc {
                        color: #aaa;
                        font-size: 14px;
                    }
                </style>
            </div>
        </div>
    </div>
    
    <!-- Close Confirmation Modal -->
    <div id="close-modal" class="modal-overlay">
        <div class="modal">
            <h3>Confirm Action</h3>
            <p>You have unsaved changes. Please Keep or Revert before closing.</p>
            <div class="modal-buttons">
                <button class="btn btn-success" onclick="commitChanges(); closeWindow()">Keep Changes</button>
                <button class="btn btn-danger" onclick="revertChanges(); closeWindow()">Revert & Close</button>
                <button class="btn btn-primary" onclick="hideCloseModal()">Cancel</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentSettings = {};
        let previewActive = false;
        
        // Initialize
        window.onload = function() {
            loadSettings();
            startSSE();
        };
        
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            
            // Show selected
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
        }
        
        function updateValue(id, value) {
            document.getElementById(id + '-value').textContent = value + 'x';
        }
        
        function updateMode(value) {
            // Mode changed
        }
        
        function loadSettings() {
            // Load via pywebview API
            if (window.pywebview) {
                window.pywebview.api.get_settings().then(function(settings) {
                    currentSettings = settings;
                    document.getElementById('sensitivity').value = settings.sensitivity || 1.0;
                    document.getElementById('sensitivity-value').textContent = (settings.sensitivity || 1.0) + 'x';
                    document.getElementById('mode').value = settings.mode || 'hybrid';
                    document.getElementById('speech_speed').value = settings.speech_speed || 1.0;
                    document.getElementById('speech_speed-value').textContent = (settings.speech_speed || 1.0) + 'x';
                });
            }
        }
        
        function saveChanges() {
            const sensitivity = document.getElementById('sensitivity').value;
            const mode = document.getElementById('mode').value;
            const speechSpeed = document.getElementById('speech_speed').value;
            
            if (window.pywebview) {
                window.pywebview.api.preview_settings(sensitivity, mode, speechSpeed).then(function(result) {
                    if (!result.error) {
                        previewActive = true;
                        document.getElementById('countdown').classList.add('active');
                        
                        // Hide Save button, show Keep and Revert buttons
                        document.getElementById('save-btn').style.display = 'none';
                        document.getElementById('keep-btn').style.display = 'inline-block';
                        document.getElementById('revert-btn').style.display = 'inline-block';
                    }
                });
            }
        }
        
        function commitChanges() {
            if (window.pywebview) {
                window.pywebview.api.commit_settings().then(function(result) {
                    if (!result.error) {
                        previewActive = false;
                        document.getElementById('countdown').classList.remove('active');
                        
                        // Show Save button, hide Keep and Revert buttons
                        document.getElementById('save-btn').style.display = 'inline-block';
                        document.getElementById('keep-btn').style.display = 'none';
                        document.getElementById('revert-btn').style.display = 'none';
                        
                        loadSettings();
                    }
                });
            }
        }
        
        function revertChanges() {
            if (window.pywebview) {
                window.pywebview.api.revert_settings().then(function(result) {
                    if (!result.error) {
                        previewActive = false;
                        document.getElementById('countdown').classList.remove('active');
                        
                        // Show Save button, hide Keep and Revert buttons
                        document.getElementById('save-btn').style.display = 'inline-block';
                        document.getElementById('keep-btn').style.display = 'none';
                        document.getElementById('revert-btn').style.display = 'none';
                        
                        loadSettings();
                    }
                });
            }
        }
        
        function updateCountdown(seconds) {
            document.getElementById('countdown-timer').textContent = seconds + 's';
            if (seconds <= 0) {
                document.getElementById('countdown').classList.remove('active');
                previewActive = false;
                
                // Show Save button, hide Keep and Revert buttons
                document.getElementById('save-btn').style.display = 'inline-block';
                document.getElementById('keep-btn').style.display = 'none';
                document.getElementById('revert-btn').style.display = 'none';
                
                loadSettings();
            }
        }
        
        function showAutoRevertMessage() {
            alert('Settings automatically reverted to original values.');
            document.getElementById('countdown').classList.remove('active');
            previewActive = false;
            
            // Show Save button, hide Keep and Revert buttons
            document.getElementById('save-btn').style.display = 'inline-block';
            document.getElementById('keep-btn').style.display = 'none';
            document.getElementById('revert-btn').style.display = 'none';
            
            loadSettings();
        }
        
        function showCloseModal() {
            if (previewActive) {
                document.getElementById('close-modal').classList.add('active');
                return true;
            }
            return false;
        }
        
        function hideCloseModal() {
            document.getElementById('close-modal').classList.remove('active');
        }
        
        function closeWindow() {
            hideCloseModal();
            if (window.pywebview) {
                window.pywebview.api.close_window();
            }
        }
        
        function startSSE() {
            // Server-Sent Events for live updates
            // This would connect to the FastAPI SSE endpoint
            // For now, poll every 2 seconds
            setInterval(function() {
                if (!previewActive && window.pywebview) {
                    window.pywebview.api.get_settings().then(function(settings) {
                        if (JSON.stringify(settings) !== JSON.stringify(currentSettings)) {
                            currentSettings = settings;
                            document.getElementById('sensitivity').value = settings.sensitivity || 1.0;
                            document.getElementById('sensitivity-value').textContent = (settings.sensitivity || 1.0) + 'x';
                            document.getElementById('sensitivity-live').style.display = 'inline-block';
                            setTimeout(function() {
                                document.getElementById('sensitivity-live').style.display = 'none';
                            }, 1000);
                        }
                    });
                }
            }, 2000);
        }
        
        // Intercept close button
        window.onbeforeunload = function(e) {
            if (showCloseModal()) {
                e.preventDefault();
                e.returnValue = '';
                return '';
            }
        };
    </script>
</body>
</html>
'''


def check_single_instance():
    """Check if another instance is already running using socket"""
    try:
        # Try to bind to a specific port - if taken, another instance is running
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 20260))  # Different port from server
        sock.listen(1)
        return True, sock
    except socket.error:
        return False, None


def main():
    """Main entry point for the desktop application"""
    global window, api
    
    # Check for single instance
    is_single, lock_socket = check_single_instance()
    if not is_single:
        print("[SOFTWARE] Another instance is already running.")
        print("[SOFTWARE] Please close the existing window first.")
        sys.exit(1)
    
    # Get server port from settings
    settings = load_settings()
    port = settings.get('port', 2026)
    
    # Check if server is running
    server_url = f"http://127.0.0.1:{port}"
    try:
        response = requests.get(f"{server_url}/settings", timeout=2)
        if response.status_code != 200:
            print(f"[SOFTWARE] Heisenberg server not found on port {port}")
            print("[SOFTWARE] Please start Heisenberg first.")
            sys.exit(1)
    except:
        print(f"[SOFTWARE] Cannot connect to Heisenberg server on port {port}")
        print("[SOFTWARE] Please start Heisenberg first.")
        sys.exit(1)
    
    print(f"[SOFTWARE] Connected to Heisenberg server on port {port}")
    
    # Create API bridge
    api = HeisenbergAPI(server_url)
    
    # Create window
    window = webview.create_window(
        'Heisenberg Multimodal Assistive',
        html=HTML_CONTENT,
        width=1200,
        height=800,
        resizable=True,
        min_size=(1000, 600),
        confirm_close=True
    )
    
    # Expose API to JavaScript
    window.expose(api.get_settings)
    window.expose(api.preview_settings)
    window.expose(api.commit_settings)
    window.expose(api.revert_settings)
    window.expose(api.get_remaining_time)
    
    # Custom close handler
    def on_closing():
        if api.preview_active:
            return False  # Prevent closing
        return True
    
    window.events.closing += on_closing
    
    # Start webview
    webview.start(debug=False)
    
    # Cleanup
    if lock_socket:
        lock_socket.close()


if __name__ == "__main__":
    main()
