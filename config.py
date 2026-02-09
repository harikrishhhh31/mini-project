# COLOR PALETTE (Iron Man / Sci-Fi)
COLOR_CYAN_CORE = (255, 255, 0) # BGR
COLOR_CYAN_GLOW = (255, 200, 0)
COLOR_GOLD = (0, 215, 255)
COLOR_RED_ALERT = (0, 0, 255)
COLOR_WHITE = (255, 255, 255)

# GESTURE THRESHOLDS
SMOOTHING_BETA = 0.05
THROW_VELOCITY_THRESH = 800 # Pixels/sec
CLICK_DIST = 30 # px distance for pinch

# AI CONFIGURATION (Neural Core)
# Path to your GGUF model file. 
# Recommended: Llama-3-8B-Instruct-v0.1.Q6_K.gguf (~6-8GB)
# If file not found, system falls back to Web Search mode.
MODEL_PATH = "models/heisenberg_neural_core.gguf" 
MODEL_N_CTX = 2048 # Context window
MODEL_N_GPU_LAYERS = 35 # Offload all to GPU if possible (adjust for RTX 3050)
