#!/bin/bash
# ========================================
# Sudoku Multiplayer Game - Client Launcher
# For Linux/macOS  
# ========================================

echo ""
echo " ======================================"
echo "  SUDOKU MULTIPLAYER GAME CLIENT"
echo " ======================================"
echo ""
echo " Starting game client..."
echo " Pastikan server sudah running dulu!"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_DIR="$SCRIPT_DIR/client"

# Pindah ke directory client
cd "$CLIENT_DIR" || {
    echo " ERROR: Tidak dapat masuk ke directory client/"
    exit 1
}

# Check jika file client ada
if [ ! -f "sudoku_client.py" ]; then
    echo " ERROR: sudoku_client.py tidak ditemukan!"
    echo "   Pastikan file ada di folder client/"
    exit 1
fi

# Check jika Python terinstall
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo " ERROR: Python tidak terinstall!"
    echo "   Install Python dari: https://python.org/downloads/"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Check jika pygame terinstall
if ! $PYTHON_CMD -c "import pygame" 2>/dev/null; then
    echo " WARNING: pygame tidak terinstall!"
    echo "   Installing pygame..."
    
    if ! $PYTHON_CMD -m pip install pygame; then
        echo " ERROR: Gagal install pygame!"
        exit 1
    fi
fi

echo " Prerequisites check: OK"
echo ""
echo " Starting Sudoku Client..."
echo "====================================="
echo ""
echo "INSTRUCTIONS:"
echo "- Server IP: localhost (untuk local)"
echo "- Server Port: 55555"
echo "- Player ID: masukkan ID unik (contoh: player1)"
echo "- Player Name: masukkan nama Anda"
echo ""

# Jalankan client
$PYTHON_CMD sudoku_client.py

# Jika client exit, tunjukkan pesan
echo ""
echo " Client stopped"
echo ""