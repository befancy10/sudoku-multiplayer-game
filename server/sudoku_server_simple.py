"""
Simplified Sudoku Server - Skip problematic component testing
Version untuk bypass hang issue
"""

from socket import *
import socket
import threading
import time
import sys
import logging
import json
import traceback

# Import game components dengan error handling
try:
    from game_manager import GameManager
    from protocol_handler import ProtocolHandler
    print(" Game components imported successfully")
except ImportError as e:
    print(f" Import error: {e}")
    print("Make sure game_manager.py and protocol_handler.py are in the server/ directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProcessTheClient(threading.Thread):
    """Simplified client handler"""
    
    def __init__(self, connection, address, game_manager, protocol_handler):
        self.connection = connection
        self.address = address
        self.game_manager = game_manager
        self.protocol_handler = protocol_handler
        self.player_id = None
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        rcv = ""
        try:
            logging.info(f"Client handler started for {self.address}")
            
            while True:
                try:
                    data = self.connection.recv(1024)
                    if data:
                        d = data.decode('utf-8')
                        rcv = rcv + d
                        
                        if '\r\n\r\n' in rcv:
                            message = rcv.replace('\r\n\r\n', '')
                            logging.info(f"RECEIVED from {self.address}: {message}")
                            
                            # Process command
                            response = self.process_command(message)
                            logging.info(f"SENDING to {self.address}: {response}")
                            
                            # Send response
                            response_data = response + "\r\n\r\n"
                            self.connection.sendall(response_data.encode('utf-8'))
                            
                            rcv = ""
                    else:
                        logging.info(f"Client {self.address} disconnected")
                        break
                        
                except Exception as e:
                    logging.error(f"Error with client {self.address}: {e}")
                    break
        
        except Exception as e:
            logging.error(f"Fatal error with client {self.address}: {e}")
        finally:
            self.cleanup()

    def process_command(self, message):
        """Process game command with simple error handling"""
        try:
            # Parse JSON
            command_data = json.loads(message)
            command = command_data.get("command")
            player_id = command_data.get("player_id")
            
            logging.info(f"Processing command: {command} from player: {player_id}")
            
            # Track player for cleanup
            if command == "join_game":
                self.player_id = player_id
            
            # Simple command handling
            if command == "join_game":
                return self.handle_join_game(command_data)
            elif command == "get_puzzle":
                return self.handle_get_puzzle()
            elif command == "submit_answer":
                return self.handle_submit_answer(command_data)
            elif command == "get_scores":
                return self.handle_get_scores()
            elif command == "get_game_state":
                return self.handle_get_game_state()
            elif command == "get_player_progress":
                return self.handle_get_player_progress()
            else:
                return json.dumps({
                    "status": "ERROR",
                    "message": f"Unknown command: {command}",
                    "data": {}
                })
            
        except json.JSONDecodeError:
            return json.dumps({
                "status": "ERROR",
                "message": "Invalid JSON",
                "data": {}
            })
        except Exception as e:
            logging.error(f"Command processing error: {e}")
            return json.dumps({
                "status": "ERROR", 
                "message": f"Server error: {str(e)}",
                "data": {}
            })

    def handle_join_game(self, command_data):
        """Handle join game command"""
        try:
            player_id = command_data.get("player_id")
            player_name = command_data["data"]["player_name"]
            
            success, message = self.game_manager.add_player(player_id, player_name)
            
            if success:
                return json.dumps({
                    "status": "OK",
                    "message": message,
                    "data": {
                        "player_id": player_id,
                        "player_name": player_name
                    }
                })
            else:
                return json.dumps({
                    "status": "ERROR",
                    "message": message,
                    "data": {}
                })
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "message": f"Join game error: {str(e)}",
                "data": {}
            })

    def handle_get_puzzle(self):
        """Handle get puzzle command"""
        try:
            puzzle = self.game_manager.get_puzzle()
            return json.dumps({
                "status": "OK",
                "message": "Puzzle retrieved",
                "data": {"puzzle": puzzle}
            })
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "message": f"Puzzle error: {str(e)}",
                "data": {}
            })

    def handle_submit_answer(self, command_data):
        """Handle submit answer command"""
        try:
            player_id = command_data.get("player_id")
            data = command_data["data"]
            row = int(data["row"])
            col = int(data["col"])
            value = int(data["value"])
            
            success, message, result = self.game_manager.submit_answer(player_id, row, col, value)
            
            return json.dumps({
                "status": "OK" if success else "ERROR",
                "message": message,
                "data": result
            })
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "message": f"Submit error: {str(e)}",
                "data": {}
            })

    def handle_get_scores(self):
        """Handle get scores command"""
        try:
            scores = self.game_manager.get_scores()
            return json.dumps({
                "status": "OK",
                "message": "Scores retrieved",
                "data": {"scores": scores}
            })
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "message": f"Scores error: {str(e)}",
                "data": {}
            })

    def handle_get_game_state(self):
        """Handle get game state command"""
        try:
            state = self.game_manager.get_game_state()
            return json.dumps({
                "status": "OK",
                "message": "Game state retrieved",
                "data": state
            })
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "message": f"Game state error: {str(e)}",
                "data": {}
            })

    def handle_get_player_progress(self):
        """Handle get player progress command"""
        try:
            progress = self.game_manager.get_player_progress()
            return json.dumps({
                "status": "OK",
                "message": "Progress retrieved",
                "data": {"progress": progress}
            })
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "message": f"Progress error: {str(e)}",
                "data": {}
            })

    def cleanup(self):
        """Cleanup when client disconnects"""
        if self.player_id:
            try:
                self.game_manager.remove_player(self.player_id)
                logging.info(f"Cleaned up player {self.player_id}")
            except Exception as e:
                logging.error(f"Cleanup error: {e}")
        
        try:
            self.connection.close()
        except:
            pass

class SimpleServer:
    """Simplified server without component testing"""
    
    def __init__(self, host='0.0.0.0', port=55555, max_players=4):
        self.host = host
        self.port = port
        self.max_players = max_players
        self.socket = None
        self.running = False
        self.clients = []
        
        # Initialize game components WITHOUT testing
        print("Initializing game components...")
        try:
            self.game_manager = GameManager(max_players)
            self.protocol_handler = ProtocolHandler(self.game_manager)
            print(" Game components initialized")
        except Exception as e:
            print(f" Game component initialization failed: {e}")
            raise

    def start(self):
        """Start the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            
            self.running = True
            print(f" Sudoku Server STARTED on {self.host}:{self.port}")
            print(f"Max players: {self.max_players}")
            print("Waiting for clients... (Ctrl+C to stop)")
            
            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    print(f"🔗 New connection: {addr}")
                    
                    # Create client handler
                    client = ProcessTheClient(conn, addr, self.game_manager, self.protocol_handler)
                    client.start()
                    self.clients.append(client)
                    
                    # Cleanup finished clients
                    self.clients = [c for c in self.clients if c.is_alive()]
                    print(f"Active connections: {len(self.clients)}")
                    
                except Exception as e:
                    if self.running:
                        print(f"Accept error: {e}")
                        
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the server"""
        print("Stopping server...")
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("Server stopped")

def main():
    """Main function - simplified startup"""
    print("=== Sudoku Multiplayer Game Server (Simple) ===")
    
    # Quick config
    HOST = input("Server host (default 0.0.0.0): ").strip() or "0.0.0.0"
    
    try:
        PORT = int(input("Server port (default 55555): ").strip() or "55555")
    except ValueError:
        PORT = 55555
    
    try:
        MAX_PLAYERS = int(input("Max players (default 4): ").strip() or "4")
    except ValueError:
        MAX_PLAYERS = 4
    
    print(f"\nStarting server: {HOST}:{PORT} (max {MAX_PLAYERS} players)")
    
    try:
        server = SimpleServer(HOST, PORT, MAX_PLAYERS)
        server.start()
    except KeyboardInterrupt:
        print("\nShutdown requested")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()