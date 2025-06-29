#!/bin/bash
# ========================================
# Sudoku Multiplayer Game - Server Launcher
# For Linux/macOS
# ========================================

echo ""
echo " ======================================"
echo "  SUDOKU MULTIPLAYER GAME SERVER"
echo " ======================================"
echo ""
echo " Starting server..."
echo " Server akan running pada port 55555"
echo " Press Ctrl+C untuk stop server"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/server"

# Pindah ke directory server
cd "$SERVER_DIR" || {
    echo " ERROR: Tidak dapat masuk ke directory server/"
    exit 1
}

# Check jika file server ada
if [ ! -f "sudoku_server_simple.py" ]; then
    echo " ERROR: sudoku_server_simple.py tidak ditemukan!"
    echo "   Pastikan file ada di folder server/"
    exit 1
fi

# Check jika Python terinstall
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo " ERROR: Python tidak terinstall!"
    echo "   Install Python dari: https://python.org/downloads/"
    echo "   Atau gunakan package manager:"
    echo "   - Ubuntu/Debian: sudo apt install python3"
    echo "   - macOS: brew install python3"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 6 ]); then
    echo " ERROR: Python 3.6+ required. Current: $PYTHON_VERSION"
    exit 1
fi

# Check jika pygame terinstall
if ! $PYTHON_CMD -c "import pygame" 2>/dev/null; then
    echo " WARNING: pygame tidak terinstall!"
    echo "   Installing pygame..."
    
    if ! $PYTHON_CMD -m pip install pygame; then
        echo " ERROR: Gagal install pygame!"
        echo "   Try manual install: $PYTHON_CMD -m pip install pygame"
        exit 1
    fi
fi

echo " Prerequisites check: OK"
echo ""
echo " Starting Sudoku Server..."
echo "====================================="

# Jalankan server
$PYTHON_CMD sudoku_server_simple.py

# Jika server exit, tunjukkan pesan
echo ""
echo " Server stopped"
echo ""
