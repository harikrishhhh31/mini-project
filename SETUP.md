# Heisenberg System Setup Guide

## Overview

Heisenberg is a multimodal assistive interface for contactless computing. This guide covers the installation and setup of the new Settings Management System.

## Architecture

```
Heisenberg (main_file.py)
    ├── Spawns FastAPI Server (server.py)
    │       └── Port: 2026 (with fallback)
    │       └── REST API + SSE
    └── SystemController
            ├── Loads settings from JSON
            ├── Syncs with server via HTTP
            └── Auto-saves on changes

software.py (Desktop UI)
    └── pywebview application
        ├── Professional settings interface
        ├── Preview/Commit/Revert (120s)
        └── Actions Guide documentation
```

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi` - REST API framework
- `uvicorn` - ASGI server
- `platformdirs` - Cross-platform config paths
- `sse-starlette` - Server-Sent Events
- `pywebview` - Desktop web UI
- `requests` - HTTP client
- Existing: opencv-python, mediapipe, torch, etc.

### Step 2: Verify Installation

```bash
python test_system.py
```

This runs automated tests for:
- Settings Manager (cross-platform config)
- Server Port Fallback
- API Endpoints
- Auto-revert functionality
- Live sync

## Usage

### Starting Heisenberg

```bash
python main_file.py
```

This will:
1. Start the FastAPI settings server on port 2026 (or next available)
2. Load settings from cross-platform config directory
3. Initialize vision, voice, and gesture systems
4. Start the main loop

**Settings Storage Location:**
- Windows: `C:\Users\<user>\AppData\Local\Heisenberg\settings.json`
- Linux: `/home/<user>/.config/heisenberg/settings.json`
- macOS: `/Users/<user>/Library/Application Support/Heisenberg/settings.json`

### Opening Settings UI

When you need to adjust settings, run:

```bash
python software.py
```

**Features:**
- **Single Instance**: Only one window allowed at a time
- **Live Sync**: Changes reflect immediately in Heisenberg
- **Preview Mode**: Test settings for 120 seconds before committing
- **Auto-revert**: Returns to original values if not committed

### Settings Available

1. **Sensitivity (0.5x - 2.0x)**
   - Controls cursor movement speed
   - Can be adjusted via voice: "increase sensitivity"

2. **System Mode**
   - Hybrid: Both gesture and voice
   - Gesture Only: Vision-based control only
   - Voice Only: Speech commands only

3. **Speech Speed (0.5x - 2.0x)**
   - Controls TTS playback rate

### Preview/Commit/Revert Workflow

1. **Change Settings**: Adjust sliders or dropdowns
2. **Preview Changes**: Click button to apply temporarily
   - 120-second countdown starts
   - Settings applied to running Heisenberg
   - "Keep Changes" or "Revert" buttons shown
3. **Keep Changes**: Saves to JSON permanently
4. **Revert**: Restores original values immediately
5. **Auto-revert**: If no action in 120s, automatically reverts

### Close Button Behavior

If preview mode is active when you try to close:
- Modal appears: "Please Keep or Revert before closing"
- Options: Keep Changes, Revert & Close, Cancel
- Window cannot be closed without decision

## Voice Commands

The following voice commands work with the new system:

- **"increase sensitivity"** / **"decrease sensitivity"**
  - Adjusts by 0.1x steps
  - Auto-saves to JSON
  - Updates server

- **"gesture only"** / **"voice only"** / **"hybrid"**
  - Changes system mode
  - Auto-saves to JSON

- **"reset sensitivity"**
  - Returns to 1.0x
  - Auto-saves

## Actions Guide

The software.py includes a professional Actions Guide documenting all 16 control methods:

### Gesture Actions
- Mouse Navigation (Point gesture)
- Primary Click (Fist gesture)
- Context Menu (Peace gesture)
- Release/Stop (Open palm)
- Inertial Throw (High velocity)
- Shadow Clone (Split peace)

### Voice Commands
- "open [app]", "type [text]", "search [query]"
- "color", "what is [topic]"
- "exit heisenberg"

### Facial Triggers
- Magnifier Zoom (Squint)
- Focus Mode (Lean forward)

### System Controls
- Silence Protocol
- Peek Mode
- Scroll Control

## Troubleshooting

### Server Won't Start

**Symptom:** "CRITICAL ERROR: Could not start settings server"

**Solutions:**
1. Check if port 2026-2100 are all in use:
   ```bash
   netstat -tuln | grep 2026
   ```
2. Check permissions for config directory
3. Try manual server start:
   ```bash
   python server.py
   ```

### Settings Not Persisting

**Symptom:** Changes lost after restart

**Check:**
1. Config directory exists and is writable
2. settings.json is created
3. No errors in console

### UI Won't Connect

**Symptom:** "Cannot connect to Heisenberg server"

**Solutions:**
1. Verify Heisenberg is running first
2. Check settings.json for correct port
3. Try:
   ```bash
   curl http://127.0.0.1:2026/settings
   ```

### Port Already in Use

**Symptom:** Server starts on different port

**Expected Behavior:**
- Server tries 2026 first
- Falls back to 2027, 2028, etc.
- Updates settings.json with actual port
- UI reads port from JSON automatically

## Configuration Files

### settings.json

Located in cross-platform config directory:

```json
{
  "sensitivity": 1.0,
  "mode": "hybrid",
  "speech_speed": 1.0,
  "port": 2026
}
```

**Note:** This file is created automatically if missing.

## System Integration

### Auto-start on Boot

To auto-start Heisenberg on system boot:

**Windows:**
1. Create shortcut to `main_file.py`
2. Place in `shell:startup` folder
3. Or use Task Scheduler

**Linux:**
1. Create systemd service:
   ```bash
   sudo nano /etc/systemd/system/heisenberg.service
   ```
2. Add service configuration
3. Enable: `sudo systemctl enable heisenberg`

**macOS:**
1. Create plist file in `~/Library/LaunchAgents/`
2. Load with `launchctl load`

## Development

### Testing

Run the test suite:

```bash
python test_system.py
```

Tests cover:
- Settings persistence
- Port fallback
- API endpoints
- Integration

### API Documentation

When server is running, access:
- `http://127.0.0.1:2026/settings` - GET current settings
- `http://127.0.0.1:2026/settings/preview` - POST preview changes
- `http://127.0.0.1:2026/settings/commit` - POST commit changes
- `http://127.0.0.1:2026/settings/revert` - POST revert changes
- `http://127.0.0.1:2026/settings/stream` - SSE live updates

## Security Notes

1. Server only binds to localhost (127.0.0.1)
2. No authentication required (local only)
3. Settings stored in user config directory
4. Cross-Origin requests enabled for UI

## Support

For issues or questions:
1. Check test output: `python test_system.py`
2. Verify config directory permissions
3. Check console for error messages
4. Review settings.json contents

## Version History

- **v2.0** - Added Settings Management System
  - Cross-platform config storage
  - FastAPI server with port fallback
  - Desktop UI with preview/commit/revert
  - Live sync between components
  - 120s auto-revert timer
