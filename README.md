#  Sudoku Multiplayer Game

[![Python 3.8+]](https://www.python.org/downloads/)
[![pygame]](https://pygame.org/)
[![License: MIT]](https://opensource.org/licenses/MIT)

**Real-time multiplayer sudoku competition game** built with Python, pygame, and TCP sockets. Multiple players compete to solve the same sudoku puzzle with live scoring and real-time updates.

![Game Screenshot](![screenshot_local_multiplayer_gameplay](https://github.com/user-attachments/assets/b41388bc-ed8e-49f8-80fb-6b9f512a4c0d))
*Screenshot: Multiplayer sudoku competition in action*

##  Features

-  **Real-time Multiplayer**: Up to 4 players compete simultaneously
-  **Live Scoring**: +10 points for correct answers, -10 for wrong answers
-  **Professional UI**: Smooth pygame interface with real-time updates
-  **Cross-platform**: Windows, Linux, macOS support
-  **Network Play**: Play across different computers on the same network
-  **Automated Testing**: Comprehensive test suite with 100% pass rate
-  **Easy Deployment**: One-click server and client startup scripts

##  Quick Start

### Prerequisites

- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **pygame library** (will be installed automatically)
- **Network connection** (for multiplayer)

###  Single Computer Setup (Local Testing)

```bash
# 1. Clone the repository
git clone https://github.com/[username]/sudoku-multiplayer-game.git
cd sudoku-multiplayer-game

# 2. Install dependencies
pip install pygame

# 3. Start server (Terminal 1)
cd server
python sudoku_server_simple.py
# Input: Press ENTER for all defaults (0.0.0.0:55555)

# 4. Start client (Terminal 2)
cd client
python sudoku_client.py
# Input: Press ENTER for server IP, enter unique player ID and name

# 5. Start more clients (Terminal 3, 4, etc.)
cd client
python sudoku_client.py
# Use different player IDs for each client
```

###  Network Multiplayer Setup

#### Server Computer Setup:
```bash
# 1. Find your IP address
ipconfig          # Windows
ifconfig          # Linux/macOS

# Example output: IPv4 Address: 10.21.73.115

# 2. Start server
cd server
python sudoku_server_simple.py

# 3. Configuration:
Server host: 0.0.0.0        # Bind to all interfaces
Server port: 55555          # Default port
Max players: 4              # Up to 4 players
```

#### Client Computer(s) Setup:
```bash
# 1. Copy game files to client computer
# You can clone the full repo OR copy just the client folder

# 2. Install dependencies
pip install pygame

# 3. Start client
cd client
python sudoku_client.py

# 4. Configuration:
Server IP: [SERVER_IP]      # e.g., 10.21.73.115
Server port: 55555          # Same as server
Player ID: [unique_id]      # e.g., player1, player2, etc.
Player name: [your_name]    # Display name
```

##  Automated Setup (Recommended)

### Windows Users:
```batch
# Start server
run_server.bat

# Start client (run multiple times for multiple players)
run_client.bat
```

### Linux/macOS Users:
```bash
# Make scripts executable (first time only)
chmod +x run_server.sh run_client.sh

# Start server
./run_server.sh

# Start client
./run_client.sh
```

##  How to Play

### Game Controls:
- **Mouse Click**: Select a sudoku cell (highlighted in yellow)
- **Number Keys (1-9)**: Enter number into selected cell
- **DELETE/Backspace**: Clear selected cell
- **ESC**: Deselect current cell

### Scoring System:
- **+10 points**: Correct answer
- **-10 points**: Wrong answer  
- **Winner**: Player with highest score when puzzle is completed

### Game Interface:
- **9x9 Sudoku Grid**: Main game board (green = given numbers, blue = your answers)
- **Scoreboard**: Real-time player rankings on the right
- **Progress Bars**: Visual completion progress for each player
- **Instructions**: Control guidance at the bottom

##  Network Configuration

### Server Configuration:
```python
# Default settings
HOST = "0.0.0.0"      # Bind to all network interfaces
PORT = 55555          # TCP port for game communication
MAX_PLAYERS = 4       # Maximum concurrent players
PROTOCOL = "JSON over TCP"
```

### Client Configuration:
```python
# Connection settings
SERVER_IP = "localhost"     # For local testing
SERVER_IP = "10.21.73.115"  # For network play (use actual server IP)
SERVER_PORT = 55555         # Must match server port
```

### Firewall Setup:
```bash
# Windows
netsh advfirewall firewall add rule name="Sudoku Game" dir=in action=allow protocol=TCP localport=55555

# Linux (ufw)
sudo ufw allow 55555/tcp

# macOS
# Configure through System Preferences > Security & Privacy > Firewall
```

## 🔧 Troubleshooting

### Common Issues:

#### 1. "python is not recognized"
```bash
# Solution: Install Python and add to PATH
# Download: https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
```

#### 2. "No module named pygame"
```bash
# Solution: Install pygame
pip install pygame
```

#### 3. "Connection refused"
```bash
# Solutions:
# 1. Make sure server is running first
# 2. Check IP address is correct
# 3. Check firewall settings
# 4. Verify port 55555 is not blocked
```

#### 4. "Address already in use"
```bash
# Solution: Port is busy, either:
# 1. Wait a few seconds and retry
# 2. Use different port in both server and client
# 3. Kill existing process using the port
```

#### 5. Network connectivity issues
```bash
# Test network connection:
ping [SERVER_IP]              # Test basic connectivity
telnet [SERVER_IP] 55555      # Test port accessibility (if telnet available)
```

---

##  Quick Demo

Want to see it in action? Follow these 3 steps:

```bash
# 1. Start server
run_server.bat  # or ./run_server.sh

# 2. Start first client
run_client.bat  # or ./run_client.sh
# Enter: player1, Alice

# 3. Start second client  
run_client.bat  # or ./run_client.sh
# Enter: player2, Bob

#  Now play! Click cells, enter numbers, compete for highest score!
```

**🏆 Enjoy your multiplayer sudoku competition! **
