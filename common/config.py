# Configuration settings for Sudoku Multiplayer Game

# Server Configuration
SERVER_CONFIG = {
    "DEFAULT_HOST": "localhost",
    "DEFAULT_PORT": 55555,
    "MAX_PLAYERS": 4,
    "SOCKET_TIMEOUT": 30,  # seconds
    "BUFFER_SIZE": 1024
}

# Game Configuration
GAME_CONFIG = {
    "DEFAULT_DIFFICULTY": "medium",
    "SCORE_CORRECT": 10,
    "SCORE_INCORRECT": -10,
    "AUTO_SAVE_INTERVAL": 60,  # seconds
    "GAME_TIMEOUT": 3600,  # 1 hour max game time
}

# Client Configuration
CLIENT_CONFIG = {
    "WINDOW_WIDTH": 1000,
    "WINDOW_HEIGHT": 700,
    "FPS": 60,
    "UPDATE_INTERVAL": 1,  # seconds
    "CONNECTION_RETRY_ATTEMPTS": 3,
    "CONNECTION_RETRY_DELAY": 2  # seconds
}

# UI Colors (RGB)
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "BLUE": (0, 100, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "GRAY": (200, 200, 200),
    "LIGHT_BLUE": (173, 216, 230),
    "LIGHT_GREEN": (144, 238, 144),
    "LIGHT_RED": (255, 182, 193),
    "DARK_GRAY": (169, 169, 169),
    "YELLOW": (255, 255, 0),
    "LIGHT_GRAY": (211, 211, 211)
}

# Sudoku Configuration
SUDOKU_CONFIG = {
    "BOARD_SIZE": 9,
    "BOX_SIZE": 3,
    "EMPTY_CELL": 0,
    "MIN_VALUE": 1,
    "MAX_VALUE": 9,
    "DIFFICULTY_LEVELS": {
        "easy": 35,      # Remove 35 numbers (46 given)
        "medium": 45,    # Remove 45 numbers (36 given)
        "hard": 55,      # Remove 55 numbers (26 given)
        "expert": 65     # Remove 65 numbers (16 given)
    }
}

# Protocol Configuration
PROTOCOL_CONFIG = {
    "MESSAGE_DELIMITER": "\r\n\r\n",
    "ENCODING": "utf-8",
    "MAX_MESSAGE_SIZE": 8192,  # bytes
    "COMMAND_TIMEOUT": 10  # seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    "LEVEL": "INFO",
    "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "FILE_MAX_SIZE": 10 * 1024 * 1024,  # 10MB
    "BACKUP_COUNT": 5
}

# File Paths
PATHS = {
    "LOGS_DIR": "logs/",
    "SAVES_DIR": "saves/",
    "ASSETS_DIR": "client/assets/",
    "FONTS_DIR": "client/assets/fonts/",
    "SOUNDS_DIR": "client/assets/sounds/"
}

# Network Configuration
NETWORK_CONFIG = {
    "TCP_NODELAY": True,
    "SO_REUSEADDR": True,
    "KEEPALIVE": True,
    "KEEPALIVE_IDLE": 60,
    "KEEPALIVE_INTERVAL": 10,
    "KEEPALIVE_PROBES": 3
}

# Development/Debug Configuration
DEBUG_CONFIG = {
    "ENABLE_DEBUG": False,
    "SHOW_SOLUTION": False,  # For debugging only
    "VERBOSE_LOGGING": False,
    "PROFILE_PERFORMANCE": False,
    "AUTO_GENERATE_PLAYERS": False  # For testing
}

def get_server_config():
    """Get server configuration"""
    return SERVER_CONFIG.copy()

def get_client_config():
    """Get client configuration"""
    return CLIENT_CONFIG.copy()

def get_game_config():
    """Get game configuration"""
    return GAME_CONFIG.copy()

def get_colors():
    """Get color configuration"""
    return COLORS.copy()

def get_sudoku_config():
    """Get sudoku configuration"""
    return SUDOKU_CONFIG.copy()

def update_config(section, key, value):
    """Update configuration value"""
    config_map = {
        "server": SERVER_CONFIG,
        "client": CLIENT_CONFIG,
        "game": GAME_CONFIG,
        "colors": COLORS,
        "sudoku": SUDOKU_CONFIG,
        "protocol": PROTOCOL_CONFIG,
        "logging": LOGGING_CONFIG,
        "paths": PATHS,
        "network": NETWORK_CONFIG,
        "debug": DEBUG_CONFIG
    }
    
    if section in config_map and key in config_map[section]:
        config_map[section][key] = value
        return True
    return False

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Validate server config
    if SERVER_CONFIG["DEFAULT_PORT"] < 1024 or SERVER_CONFIG["DEFAULT_PORT"] > 65535:
        errors.append("Invalid server port range")
    
    if SERVER_CONFIG["MAX_PLAYERS"] < 1 or SERVER_CONFIG["MAX_PLAYERS"] > 10:
        errors.append("Invalid max players range")
    
    # Validate game config
    if GAME_CONFIG["SCORE_CORRECT"] <= 0:
        errors.append("Score for correct answers must be positive")
    
    if GAME_CONFIG["SCORE_INCORRECT"] >= 0:
        errors.append("Score for incorrect answers must be negative")
    
    # Validate client config
    if CLIENT_CONFIG["WINDOW_WIDTH"] < 800 or CLIENT_CONFIG["WINDOW_HEIGHT"] < 600:
        errors.append("Minimum window size is 800x600")
    
    if CLIENT_CONFIG["FPS"] < 30 or CLIENT_CONFIG["FPS"] > 120:
        errors.append("FPS should be between 30 and 120")
    
    return errors

def load_config_from_file(filename):
    """Load configuration from file (future implementation)"""
    # This would load configuration from a JSON or INI file
    pass

def save_config_to_file(filename):
    """Save configuration to file (future implementation)"""
    # This would save current configuration to a file
    pass

if __name__ == "__main__":
    # Validate configuration on import
    validation_errors = validate_config()
    if validation_errors:
        print("Configuration validation errors:")
        for error in validation_errors:
            print(f"- {error}")
    else:
        print("Configuration validation passed")