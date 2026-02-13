"""
Settings Manager - Cross-platform configuration management for Heisenberg
Stores user settings in OS-appropriate config directory
"""

import json
import os
from platformdirs import user_config_dir

# Default settings
DEFAULT_SETTINGS = {
    "sensitivity": 1.0,
    "mode": "hybrid",
    "speech_speed": 1.0,
    "port": 2026
}

# Cross-platform config directory
CONFIG_DIR = user_config_dir("Heisenberg", "HeisenbergAI")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")


def ensure_config_dir():
    """Create config directory if it doesn't exist"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)


def load_settings():
    """
    Load settings from JSON file.
    If file doesn't exist, create it with default values.
    
    Returns:
        dict: Current settings
    """
    ensure_config_dir()
    
    if not os.path.exists(SETTINGS_FILE):
        # Create with defaults
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        
        # Merge with defaults to ensure all keys exist
        merged = DEFAULT_SETTINGS.copy()
        merged.update(settings)
        return merged
        
    except (json.JSONDecodeError, IOError):
        # If file is corrupted, recreate with defaults
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    Save settings to JSON file.
    
    Args:
        settings (dict): Settings to save
    """
    ensure_config_dir()
    
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except IOError:
        return False


def update_setting(key, value):
    """
    Update a single setting and save to file.
    
    Args:
        key (str): Setting key to update
        value: New value
        
    Returns:
        bool: True if successful
    """
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)


def get_setting(key, default=None):
    """
    Get a single setting value.
    
    Args:
        key (str): Setting key
        default: Default value if key not found
        
    Returns:
        Setting value or default
    """
    settings = load_settings()
    return settings.get(key, default)


def reset_to_defaults():
    """Reset all settings to default values"""
    return save_settings(DEFAULT_SETTINGS.copy())


# Convenience functions for common settings
def get_sensitivity():
    """Get current sensitivity setting"""
    return get_setting('sensitivity', 1.0)


def set_sensitivity(value):
    """Set sensitivity and save"""
    return update_setting('sensitivity', value)


def get_mode():
    """Get current mode setting"""
    return get_setting('mode', 'hybrid')


def set_mode(value):
    """Set mode and save"""
    return update_setting('mode', value)


def get_speech_speed():
    """Get current speech speed setting"""
    return get_setting('speech_speed', 1.0)


def set_speech_speed(value):
    """Set speech speed and save"""
    return update_setting('speech_speed', value)


def get_port():
    """Get current port setting"""
    return get_setting('port', 2026)


def set_port(value):
    """Set port and save"""
    return update_setting('port', value)
