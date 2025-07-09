#!/usr/bin/env python3
"""
Test client untuk Sudoku Game Server (Integrated Template)
Menggunakan raw socket dengan JSON commands
"""

import socket
import json
import time
import sys

class SudokuTestClient:
    def __init__(self, server_host="localhost", server_port=55555):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.player_id = None
        self.player_name = None
        
    def connect(self):
        """Connect to the integrated server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            print(f"✅ Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def send_command(self, command_data):
        """Send JSON command to server"""
        if not self.connected:
            print("❌ Not connected to server")
            return None
        
        try:
            # Send JSON command with delimiter
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
            
            # Remove delimiter and parse JSON
            data_received = data_received.replace('\r\n\r\n', '')
            result = json.loads(data_received)
            return result
            
        except Exception as e:
            print(f"❌ Command error: {e}")
            return None
    
    def join_game(self, player_name, player_id=None):
        """Join the game"""
        if not player_id:
            player_id = f"test_player_{int(time.time())}"
        
        command = {
            "command": "join_game",
            "player_id": player_id,
            "data": {"player_name": player_name}
        }
        
        response = self.send_command(command)
        if response and response["status"] == "OK":
            self.player_id = player_id
            self.player_name = player_name
            print(f"✅ Joined game as {player_name} (ID: {player_id})")
            return True
        else:
            error_msg = response["message"] if response else "No response"
            print(f"❌ Failed to join: {error_msg}")
            return False
    
    def get_puzzle(self):
        """Get current puzzle"""
        command = {
            "command": "get_puzzle",
            "player_id": self.player_id,
            "data": {}
        }
        
        response = self.send_command(command)
        if response and response["status"] == "OK":
            puzzle = response["data"]["puzzle"]
            print("✅ Current Puzzle:")
            self.print_board(puzzle)
            return puzzle
        else:
            error_msg = response["message"] if response else "No response"
            print(f"❌ Failed to get puzzle: {error_msg}")
            return None
    
    def submit_answer(self, row, col, value):
        """Submit an answer"""
        if not self.player_id:
            print("❌ Not joined to any game")
            return False
        
        command = {
            "command": "submit_answer",
            "player_id": self.player_id,
            "data": {
                "row": row,
                "col": col,
                "value": value
            }
        }
        
        response = self.send_command(command)
        if response and response["status"] == "OK":
            data = response["data"]
            if data["correct"]:
                print(f"✅ Correct! +{data['score_change']} points. Score: {data['new_score']}")
            else:
                print(f"❌ Incorrect! {data['score_change']} points. Score: {data['new_score']}")
            return True
        else:
            error_msg = response["message"] if response else "No response"
            print(f"❌ Failed to submit: {error_msg}")
            return False
    
    def get_scores(self):
        """Get all player scores"""
        command = {
            "command": "get_scores",
            "player_id": self.player_id,
            "data": {}
        }
        
        response = self.send_command(command)
        if response and response["status"] == "OK":
            scores = response["data"]["scores"]
            print("🏆 Current Scores:")
            if not scores:
                print("   No players yet")
            else:
                sorted_scores = sorted(scores.items(), 
                                     key=lambda x: x[1]["score"], 
                                     reverse=True)
                for i, (player_id, info) in enumerate(sorted_scores, 1):
                    print(f"   {i}. {info['name']}: {info['score']} points")
            return scores
        else:
            error_msg = response["message"] if response else "No response"
            print(f"❌ Failed to get scores: {error_msg}")
            return None
    
    def get_game_state(self):
        """Get current game state"""
        command = {
            "command": "get_game_state",
            "player_id": self.player_id,
            "data": {}
        }
        
        response = self.send_command(command)
        if response and response["status"] == "OK":
            state = response["data"]
            print(f"🎮 Game State: {state['game_state']}")
            print(f"   Players: {state['players_count']}/{state['max_players']}")
            print(f"   Duration: {state['game_duration']:.1f}s")
            return state
        else:
            error_msg = response["message"] if response else "No response"
            print(f"❌ Failed to get state: {error_msg}")
            return None
    
    def print_board(self, board):
        """Print Sudoku board in readable format"""
        print("   0 1 2   3 4 5   6 7 8")
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("  ------+-------+------")
            
            row_str = f"{i} "
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                
                if board[i][j] == 0:
                    row_str += ". "
                else:
                    row_str += f"{board[i][j]} "
            
            print(row_str)
    
    def disconnect(self):
        """Disconnect from server"""
        if self.connected and self.socket:
            try:
                self.socket.close()
                self.connected = False
                print("👋 Disconnected from server")
            except:
                pass

def demo_session():
    """Demo session untuk testing"""
    print("🎮 Sudoku Game Server Test Client")
    print("=" * 40)
    
    client = SudokuTestClient()
    
    # Connect to server
    if not client.connect():
        print("❌ Please start the server first: python server_thread_http.py")
        return
    
    try:
        # Join game
        player_name = input("Enter your name: ").strip() or "TestPlayer"
        if not client.join_game(player_name):
            return
        
        # Get game info
        print("\n📋 Getting game information...")
        client.get_game_state()
        client.get_scores()
        
        # Get puzzle
        print("\n🧩 Getting puzzle...")
        puzzle = client.get_puzzle()
        
        if puzzle:
            # Find some empty cells for testing
            empty_cells = []
            for i in range(9):
                for j in range(9):
                    if puzzle[i][j] == 0:
                        empty_cells.append((i, j))
            
            if empty_cells:
                print(f"\n💡 Found {len(empty_cells)} empty cells")
                print("📝 Try submitting some answers...")
                
                # Interactive mode
                while True:
                    try:
                        print("\nCommands: submit, scores, state, puzzle, quit")
                        cmd = input("> ").strip().lower()
                        
                        if cmd == "quit" or cmd == "q":
                            break
                        elif cmd == "submit":
                            try:
                                row = int(input("Row (0-8): "))
                                col = int(input("Col (0-8): "))
                                value = int(input("Value (1-9): "))
                                client.submit_answer(row, col, value)
                            except ValueError:
                                print("❌ Invalid input. Use numbers only.")
                        elif cmd == "scores":
                            client.get_scores()
                        elif cmd == "state":
                            client.get_game_state()
                        elif cmd == "puzzle":
                            client.get_puzzle()
                        elif cmd == "help" or cmd == "":
                            print("Available commands:")
                            print("  submit - Submit an answer")
                            print("  scores - Get player scores")
                            print("  state  - Get game state")
                            print("  puzzle - Show puzzle again")
                            print("  quit   - Exit")
                        else:
                            print("❌ Unknown command. Type 'help' for commands.")
                            
                    except KeyboardInterrupt:
                        break
                    except EOFError:
                        break
        
    except Exception as e:
        print(f"❌ Error during session: {e}")
    finally:
        client.disconnect()

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_session()
        else:
            print("Usage: python test_client.py [demo]")
    else:
        demo_session()

if __name__ == "__main__":
    main()