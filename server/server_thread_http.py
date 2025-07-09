from socket import *
import socket
import threading
import time
import sys
import logging
from http import HttpServer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

httpserver = HttpServer()

# Original template constructor 
class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.player_id = None  # NEW: Track player for cleanup
        threading.Thread.__init__(self)
    
    # MODIFIED for JSON commands
    def run(self):
        rcv = ""
        try:
            logging.info(f"Client handler started for {self.address}")
            
            while True:
                try:
                    # MODIFIED: Increased buffer size for JSON data
                    data = self.connection.recv(1024)  # Was 32, now 1024
                    if data:
                        # merubah input dari socket (berupa bytes) ke dalam string
                        # agar bisa mendeteksi \r\n
                        d = data.decode('utf-8', errors='ignore')
                        rcv = rcv + d
                        
                        # MODIFIED: Check for JSON command delimiter
                        if rcv.endswith('\r\n\r\n'):
                            # Remove delimiter for processing
                            message = rcv.replace('\r\n\r\n', '')
                            logging.info(f"Data dari client {self.address}: {message}")
                            
                            # Track player ID for cleanup
                            self.extract_player_id(message)
                            
                            # Process command using HttpServer
                            hasil = httpserver.proses(message)
                            
                            # hasil akan berupa bytes
                            # untuk bisa ditambahi dengan string, maka string harus di encode
                            hasil = hasil + "\r\n\r\n".encode()
                            logging.info(f"Balas ke client {self.address}: {len(hasil)} bytes")
                            
                            # hasil sudah dalam bentuk bytes
                            self.connection.sendall(hasil)
                            rcv = ""
                            
                            ## NOTE: Don't close connection immediately for game clients
                            # Let them maintain persistent connection
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
    
    # Extract player ID from JSON command for cleanup
    def extract_player_id(self, message):
        try:
            import json
            command_data = json.loads(message)
            if command_data.get("command") == "join_game":
                self.player_id = command_data.get("player_id")
        except:
            pass
        
    # Cleanup when client disconnects
    def cleanup(self):
        if self.player_id:
            try:
                httpserver.game_manager.remove_player(self.player_id)
                logging.info(f"Cleaned up player {self.player_id}")
            except Exception as e:
                logging.error(f"Cleanup error: {e}")
        
        try:
            self.connection.close()
        except:
            pass

# Original template constructor
class Server(threading.Thread):
    def __init__(self):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)
    
    # MODIFIED for game port and logging
    def run(self):
        try:
            # MODIFIED: Use game port instead of 8889
            self.my_socket.bind(('0.0.0.0', 55555))  # Was 8889, now 55555
            self.my_socket.listen(10)  # MODIFIED: Increased backlog
            
            logging.info("Sudoku Game Server started on 0.0.0.0:55555")
            print("=== Sudoku Multiplayer Game Server ===")
            print("Server running on port 55555")
            print("Waiting for clients... (Ctrl+C to stop)")
            
            while True:
                self.connection, self.client_address = self.my_socket.accept()
                logging.info("Connection from {}".format(self.client_address))
                print(f"!!! New connection: {self.client_address} !!!")
                
                clt = ProcessTheClient(self.connection, self.client_address)
                clt.start()
                self.the_clients.append(clt)
                
                # NEW: Cleanup finished threads
                self.cleanup_finished_clients()
                print(f"Active connections: {len([c for c in self.the_clients if c.is_alive()])}")
                
        except Exception as e:
            logging.error(f"Server error: {e}")
            print(f"Server error: {e}")
        finally:
            self.cleanup()
    
    # Remove finished client threads
    def cleanup_finished_clients(self):
        try:
            active_clients = []
            for client in self.the_clients:
                if client.is_alive():
                    active_clients.append(client)
            self.the_clients = active_clients
        except Exception as e:
            logging.warning(f"Error cleaning up threads: {e}")
    
    # Clean up server resources
    def cleanup(self):
        logging.info("Cleaning up server resources...")
        try:
            self.my_socket.close()
        except:
            pass

# Original template function - Tambahan error handling
def main():
    try:
        print("Initializing Sudoku Game Server...")
        svr = Server()
        svr.daemon = True  # Allow program to exit
        svr.start()
        
        # Keep main thread alive
        try:
            while svr.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            svr.cleanup()
            print("Server stopped.")
    
    except Exception as e:
        logging.error(f"Error in main: {e}")
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()