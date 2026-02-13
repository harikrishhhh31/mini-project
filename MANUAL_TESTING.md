# Manual Testing Checklist

## Pre-requisites
Install dependencies first:
```bash
pip3 install fastapi uvicorn platformdirs sse-starlette pywebview requests
```

---

## Test 1: Settings Manager
**File:** `settings_manager.py`

```python
python3 -c "
from settings_manager import *
import os

# Test 1: Reset to defaults
reset_to_defaults()
print('✓ Reset to defaults')

# Test 2: Load settings
settings = load_settings()
print(f'✓ Loaded: {settings}')

# Test 3: Update and save
settings['sensitivity'] = 1.5
save_settings(settings)
print('✓ Saved settings')

# Test 4: Verify persistence
new_settings = load_settings()
assert new_settings['sensitivity'] == 1.5
print('✓ Persistence verified')

# Test 5: Config directory
from platformdirs import user_config_dir
config_dir = user_config_dir('Heisenberg', 'HeisenbergAI')
print(f'✓ Config dir: {config_dir}')
print(f'✓ File exists: {os.path.exists(os.path.join(config_dir, \"settings.json\"))}')

print('\n✅ All Settings Manager tests passed!')
"
```

**Expected:** All checks pass, settings.json created in config directory.

---

## Test 2: Server Startup & Port Fallback
**File:** `server.py`

### Test 2a: Basic Startup
```bash
# Terminal 1: Start server
python3 server.py
```

**Expected Output:**
```
🧠 NEURAL CORE DETECTED: ... (if model exists)
[SERVER] Using port 2026
INFO:     Started server process [xxx]
INFO:     Uvicorn running on http://127.0.0.1:2026
```

### Test 2b: Port Fallback
```bash
# Terminal 1: Start first server
python3 server.py

# Terminal 2: Start second server (should fallback)
python3 server.py
```

**Expected:**
- First server: port 2026
- Second server: port 2027
- settings.json updated with new port

### Test 2c: API Endpoints
```bash
# Get settings
curl http://127.0.0.1:2026/settings

# Preview changes
curl -X POST http://127.0.0.1:2026/settings/preview \
  -H "Content-Type: application/json" \
  -d '{"sensitivity": 1.5, "mode": "voice"}'

# Check time remaining
curl http://127.0.0.1:2026/settings/time-remaining

# Commit changes
curl -X POST http://127.0.0.1:2026/settings/commit

# Revert changes
curl -X POST http://127.0.0.1:2026/settings/revert
```

**Expected:** All return JSON responses with 200 status.

---

## Test 3: Main Integration
**File:** `main_file.py`

```bash
# Start Heisenberg (server starts automatically)
python3 main_file.py
```

**Expected:**
```
[MAIN] Settings server online on port 2026
SYSTEM: Initialization Complete. HEISENBERG CORE ONLINE.
```

### Test Voice Commands
With Heisenberg running, say:
- **"increase sensitivity"**
  - Heisenberg: "Sensitivity set to 1.1"
  - HUD shows: "Sensitivity: 1.1"
  - settings.json updated
  - Server notified

- **"gesture only"**
  - Mode changes to GESTURE
  - Saved to JSON

- **"reset sensitivity"**
  - Returns to 1.0
  - Saved to JSON

---

## Test 4: Web UI (software.py)
**File:** `software.py`

### Test 4a: Single Instance
```bash
# Terminal 1
python3 software.py

# Terminal 2 (try to open another)
python3 software.py
```

**Expected:**
- First: Window opens
- Second: "Another instance is already running"

### Test 4b: Server Connection
Without Heisenberg running:
```bash
python3 software.py
```

**Expected:** "Please start Heisenberg first"

### Test 4c: Preview/Commit/Revert
1. Start Heisenberg
2. Start software.py
3. Change sensitivity to 1.5
4. Click "Preview Changes"
   - 120s countdown starts
   - Heisenberg cursor speed changes immediately
5. Click "Keep Changes"
   - Saved to JSON
6. Or click "Revert"
   - Returns to original
7. Or wait 120s
   - Auto-reverts

### Test 4d: Close Button
With preview active, try to close window:
- Modal appears: "Please Keep or Revert"
- Options: Keep Changes, Revert & Close, Cancel

### Test 4e: Live Sync
1. Open software.py
2. Say "increase sensitivity" via voice
3. Watch slider update automatically (within 2 seconds)

---

## Test 5: Auto-Revert Timer
**Time:** 120 seconds

```bash
# 1. Start Heisenberg
python3 main_file.py

# 2. Open UI
python3 software.py

# 3. Change settings and preview

# 4. Wait 120 seconds (do not click Keep or Revert)

# 5. Verify auto-revert message
```

**Expected:**
- Settings revert automatically
- "Settings automatically reverted" message
- Values return to original

---

## Test 6: Persistence
**Restart Test**

1. Start Heisenberg
2. Say "increase sensitivity" twice (now 1.2)
3. Stop Heisenberg (Ctrl+C or q key)
4. Check settings.json - should show 1.2
5. Restart Heisenberg
6. Verify sensitivity is still 1.2

---

## Test 7: Cross-Platform Config

### Linux/macOS
```bash
# Check config location
cat ~/.config/heisenberg/settings.json
# or
ls ~/Library/Application\ Support/Heisenberg/settings.json
```

### Windows
```powershell
# Check config location
Get-Content $env:LOCALAPPDATA\Heisenberg\settings.json
```

**Expected:** JSON file exists in correct OS-specific location.

---

## Test 8: Graceful Shutdown

Start Heisenberg, then stop:
```bash
python3 main_file.py
# Wait for startup
# Press 'q' or Ctrl+C
```

**Expected:**
```
Shutting down...
[MAIN] Stopping settings server...
Systems offline.
```

Server process terminated cleanly.

---

## Summary Checklist

- [ ] Settings Manager loads/saves correctly
- [ ] Config file created in proper location
- [ ] Server starts on port 2026
- [ ] Port fallback works (second instance)
- [ ] API endpoints respond correctly
- [ ] Main Heisenberg starts server automatically
- [ ] Voice commands update settings + save
- [ ] Web UI opens and connects
- [ ] Single instance enforced
- [ ] Preview mode applies immediately
- [ ] 120s countdown displays correctly
- [ ] Keep Changes saves permanently
- [ ] Revert restores original values
- [ ] Auto-revert after 120s timeout
- [ ] Close button blocked during preview
- [ ] Live sync updates UI when voice changes
- [ ] Settings persist after restart
- [ ] Graceful shutdown stops server

---

## Troubleshooting

**Import errors:**
```bash
pip3 install fastapi uvicorn platformdirs sse-starlette pywebview requests
```

**Port in use:**
- Check: `netstat -tuln | grep 2026`
- Kill: `kill $(lsof -t -i:2026)`

**Server not starting:**
```bash
# Test manually
python3 server.py
```

**UI won't connect:**
1. Check Heisenberg is running
2. Check port in settings.json
3. Test: `curl http://127.0.0.1:2026/settings`
