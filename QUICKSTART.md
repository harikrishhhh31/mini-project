# Heisenberg Quick Start

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install fastapi uvicorn platformdirs sse-starlette pywebview requests
# Or install all at once:
pip install -r requirements.txt
```

### 2. Start Heisenberg
```bash
python main_file.py
```

### 3. Open Settings (when needed)
```bash
python software.py
```

---

## 📁 New Files Added

| File | Purpose |
|------|---------|
| `settings_manager.py` | Cross-platform config management |
| `server.py` | FastAPI server (port 2026) |
| `software.py` | Desktop settings UI |
| `test_system.py` | Automated testing |
| `SETUP.md` | Full documentation |

---

## ⚙️ Settings Available

- **Sensitivity** (0.5x - 2.0x): Cursor speed
- **Mode**: Hybrid / Gesture / Voice
- **Speech Speed** (0.5x - 2.0x): TTS rate

---

## 🔄 Preview Workflow

1. Adjust settings in UI
2. Click **"Preview Changes"**
3. Test for 120 seconds
4. Click **"Keep Changes"** or **"Revert"**
5. Auto-reverts if no action taken

---

## 🎯 Key Features

✅ **Persistent Settings** - Survive restarts  
✅ **Port Fallback** - Auto-finds available port  
✅ **Live Sync** - Real-time updates  
✅ **Single Instance** - One UI window only  
✅ **Cross-Platform** - Works on Windows/Linux/macOS  

---

## 🔧 Config Location

- **Windows**: `%LOCALAPPDATA%\Heisenberg\settings.json`
- **Linux**: `~/.config/heisenberg/settings.json`
- **macOS**: `~/Library/Application Support/Heisenberg/settings.json`

---

## 🧪 Test System

```bash
python test_system.py
```

Tests:
- Settings persistence
- Port fallback
- API endpoints
- Integration

---

## 📝 API Endpoints

```
GET    /settings              - Read current settings
POST   /settings/preview      - Apply temporarily (120s)
POST   /settings/commit       - Save permanently
POST   /settings/revert       - Restore original
GET    /settings/stream       - Live updates (SSE)
```

---

## 🎤 Voice Commands

- **"increase sensitivity"** / **"decrease sensitivity"**
- **"reset sensitivity"**
- **"gesture only"** / **"voice only"** / **"hybrid"**

---

## ❓ Troubleshooting

**Server won't start?**
```bash
# Check ports
netstat -tuln | grep 2026

# Test manually
python server.py
```

**UI won't connect?**
- Ensure Heisenberg is running first
- Check port in settings.json

**Settings not saving?**
- Check config directory permissions
- Verify settings.json exists

---

## 📚 Documentation

- **Full Guide**: See `SETUP.md`
- **Actions Guide**: In software.py UI
- **Test Results**: Run `test_system.py`

---

## ✅ Implementation Complete

All 5 phases finished:
1. ✅ Settings Foundation
2. ✅ FastAPI Server  
3. ✅ System Integration
4. ✅ Web UI (software.py)
5. ✅ Testing & Documentation

**System ready for use!**
