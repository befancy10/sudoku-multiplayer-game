import socket
import logging
import json
import threading
import time

class ClientInterface:
    def __init__(self, player_id='1', server_address=('localhost', 55555)):
        self.player_id = player_id
        self.server_address = server_address
        self.connected = False
        self.socket = None
        
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.server_address)
            self.connected = True
            logging.info(f"Connected to server at {self.server_address}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            self.leave_game()
            self.socket.close()
            self.connected = False
            logging.info("Disconnected from server")
    
    def send_command(self, command_data):
        """Send command to server and get response"""
        if not self.connected:
            return {"status": "ERROR", "message": "Not connected to server"}
        
        try:
            command_str = json.dumps(command_data)
            self.socket.sendall(command_str.encode() + b'\r\n\r\n')
            
            # Receive response
            data_received = ""
            while True:
                data = self.socket.recv(1024)
                if data:
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break
                else:
                    break
            
            # Remove the delimiter
            data_received = data_received.replace('\r\n\r\n', '')
            result = json.loads(data_received)
            return result
            
        except Exception as e:
            logging.error(f"Error during command sending: {e}")
            return {"status": "ERROR", "message": str(e)}
    
    def join_game(self, player_name):
        """Join the game with player name"""
        command = {
            "command": "join_game",
            "player_id": self.player_id,
            "data": {"player_name": player_name}
        }
        return self.send_command(command)
    
    def get_puzzle(self):
        """Get the current sudoku puzzle"""
        command = {
            "command": "get_puzzle",
            "player_id": self.player_id,
            "data": {}
        }
        return self.send_command(command)
    
    def submit_answer(self, row, col, value):
        """Submit an answer for a cell"""
        command = {
            "command": "submit_answer",
            "player_id": self.player_id,
            "data": {
                "row": row,
                "col": col,
                "value": value
            }
        }
        return self.send_command(command)
    
    def get_scores(self):
        """Get all player scores"""
        command = {
            "command": "get_scores",
            "player_id": self.player_id,
            "data": {}
        }
        return self.send_command(command)
    
    def get_game_state(self):
        """Get current game state"""
        command = {
            "command": "get_game_state",
            "player_id": self.player_id,
            "data": {}
        }
        return self.send_command(command)
    
    def get_player_progress(self):
        """Get all players' progress on the board"""
        command = {
            "command": "get_player_progress",
            "player_id": self.player_id,
            "data": {}
        }
        return self.send_command(command)
    
    def leave_game(self):
        """Leave the current game"""
        command = {
            "command": "leave_game",
            "player_id": self.player_id,
            "data": {}
        }
        return self.send_command(command)