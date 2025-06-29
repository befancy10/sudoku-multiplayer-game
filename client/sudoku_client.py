import pygame
import sys
import logging
import time
import threading
from client_interface import ClientInterface
from sudoku_ui import SudokuUI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

class SudokuMultiplayerClient:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sudoku Multiplayer Game")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.connected = False
        self.player_id = ""
        self.player_name = ""
        self.puzzle = None
        self.player_board = None
        self.scores = {}
        self.players_progress = {}
        
        # UI
        self.ui = SudokuUI(self.screen)
        self.selected_cell = None
        
        # Client interface
        self.client = None
        
        # Auto-update thread
        self.update_thread = None
        self.update_running = False
        
        # Connection status
        self.connection_status = "Connecting..."
        
    def connect_to_server(self):
        """Connect to the game server"""
        try:
            server_ip = input("Enter server IP (default: localhost): ").strip()
            if not server_ip:
                server_ip = "localhost"
            
            try:
                server_port = int(input("Enter server port (default: 55555): ").strip() or "55555")
            except ValueError:
                server_port = 55555
            
            self.player_id = input("Enter your player ID: ").strip()
            self.player_name = input("Enter your name: ").strip()
            
            print(f"Connecting to {server_ip}:{server_port} as {self.player_name}...")
            
            self.client = ClientInterface(self.player_id, (server_ip, server_port))
            
            if self.client.connect():
                print("Connected! Joining game...")
                response = self.client.join_game(self.player_name)
                
                print(f"Join game response: {response}")  # DEBUG
                
                if response["status"] == "OK":
                    self.connected = True
                    self.connection_status = "Connected"
                    logging.info(f"Successfully joined game as {self.player_name}")
                    
                    # Load puzzle
                    self.load_puzzle()
                    
                    # Start update thread
                    self.start_update_thread()
                    return True
                else:
                    logging.error(f"Failed to join game: {response['message']}")
                    self.connection_status = f"Join failed: {response['message']}"
                    return False
            else:
                logging.error("Failed to connect to server")
                self.connection_status = "Connection failed"
                return False
                
        except Exception as e:
            logging.error(f"Connection error: {e}")
            self.connection_status = f"Error: {str(e)}"
            return False
    
    def load_puzzle(self):
        """Load the sudoku puzzle from server"""
        try:
            print("Loading puzzle...")  # DEBUG
            response = self.client.get_puzzle()
            print(f"Puzzle response: {response}")  # DEBUG
            
            if response["status"] == "OK":
                self.puzzle = response["data"]["puzzle"]
                # Initialize player board with the same structure
                self.player_board = [[0 for _ in range(9)] for _ in range(9)]
                # Copy the given numbers to player board
                for i in range(9):
                    for j in range(9):
                        if self.puzzle[i][j] != 0:
                            self.player_board[i][j] = self.puzzle[i][j]
                logging.info("Puzzle loaded successfully")
                print("Puzzle loaded!")  # DEBUG
            else:
                logging.error(f"Failed to load puzzle: {response['message']}")
                self.connection_status = f"Puzzle load failed: {response['message']}"
                
        except Exception as e:
            logging.error(f"Error loading puzzle: {e}")
            self.connection_status = f"Puzzle error: {str(e)}"
    
    def start_update_thread(self):
        """Start background thread for updates"""
        try:
            self.update_running = True
            self.update_thread = threading.Thread(target=self.update_game_state)
            self.update_thread.daemon = True
            self.update_thread.start()
            print("Update thread started")  # DEBUG
        except Exception as e:
            logging.error(f"Failed to start update thread: {e}")
    
    def update_game_state(self):
        """Background thread to update game state"""
        while self.update_running and self.connected:
            try:
                # Update scores
                scores_response = self.client.get_scores()
                if scores_response and scores_response["status"] == "OK":
                    self.scores = scores_response["data"]["scores"]
                
                # Update players progress
                progress_response = self.client.get_player_progress()
                if progress_response and progress_response["status"] == "OK":
                    self.players_progress = progress_response["data"]["progress"]
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                logging.error(f"Error updating game state: {e}")
                time.sleep(5)  # Wait longer on error
    
    def handle_cell_click(self, row, col):
        """Handle clicking on a sudoku cell"""
        if self.puzzle and self.puzzle[row][col] == 0:  # Only allow editing empty cells
            self.selected_cell = (row, col)
            print(f"Selected cell: ({row}, {col})")  # DEBUG
    
    def handle_number_input(self, number):
        """Handle number input for selected cell"""
        if self.selected_cell and self.puzzle:
            row, col = self.selected_cell
            if self.puzzle[row][col] == 0:  # Only allow editing empty cells
                try:
                    print(f"Submitting answer: ({row}, {col}) = {number}")  # DEBUG
                    
                    # Submit answer to server
                    response = self.client.submit_answer(row, col, number)
                    print(f"Submit response: {response}")  # DEBUG
                    
                    if response and response["status"] == "OK":
                        result = response["data"]
                        if result["correct"]:
                            self.player_board[row][col] = number
                            logging.info(f"Correct! +10 points. Cell ({row},{col}) = {number}")
                            print(f"Correct! Score: {result['new_score']}")
                        else:
                            logging.info(f"Incorrect! -10 points. Cell ({row},{col}) ≠ {number}")
                            print(f"Incorrect! Score: {result['new_score']}")
                    else:
                        error_msg = response.get("message", "Unknown error") if response else "No response"
                        logging.error(f"Failed to submit answer: {error_msg}")
                        print(f"Submit failed: {error_msg}")
                        
                except Exception as e:
                    logging.error(f"Error submitting answer: {e}")
                    print(f"Submit error: {e}")
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    cell = self.ui.get_cell_from_pos(mouse_pos)
                    if cell:
                        row, col = cell
                        self.handle_cell_click(row, col)
            
            elif event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    number = event.key - pygame.K_0
                    self.handle_number_input(number)
                elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    self.handle_number_input(0)  # Clear cell
                elif event.key == pygame.K_ESCAPE:
                    self.selected_cell = None
    
    def draw_connection_status(self):
        """Draw connection status when not connected"""
        self.screen.fill(WHITE)
        
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        # Title
        title_text = font_large.render("Sudoku Multiplayer Game", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Status
        status_color = GREEN if self.connected else RED
        status_text = font_medium.render(self.connection_status, True, status_color)
        status_rect = status_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(status_text, status_rect)
        
        # Instructions
        if not self.connected:
            instructions = [
                "1. Make sure server is running",
                "2. Check server IP and port",
                "3. Try restarting the client",
                "",
                "Press ESC to exit"
            ]
            
            y_offset = WINDOW_HEIGHT//2 + 50
            for instruction in instructions:
                if instruction:  # Skip empty lines
                    text = font_small.render(instruction, True, GRAY)
                    text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y_offset))
                    self.screen.blit(text, text_rect)
                y_offset += 30
    
    def run(self):
        """Main game loop"""
        print("Starting game loop...")  # DEBUG
        
        while self.running:
            try:
                self.handle_events()
                
                # Clear screen
                self.screen.fill(WHITE)
                
                if self.connected and self.puzzle:
                    # Draw the game
                    self.ui.draw_sudoku_board(self.puzzle, self.player_board, self.selected_cell)
                    self.ui.draw_scores(self.scores, self.player_name)
                    self.ui.draw_players_progress(self.players_progress)
                    self.ui.draw_instructions()
                else:
                    # Draw connection status
                    self.draw_connection_status()
                
                pygame.display.flip()
                self.clock.tick(FPS)
                
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                # Continue running to show error state
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up...")  # DEBUG
        self.update_running = False
        if self.client and self.connected:
            try:
                self.client.disconnect()
            except:
                pass
        if self.update_thread:
            self.update_thread.join(timeout=2)
        pygame.quit()
        sys.exit()

def main():
    """Main function with better error handling"""
    try:
        print("Initializing game...")
        game = SudokuMultiplayerClient()
        
        print("Connecting to server...")
        # Connect to server first (but don't block if it fails)
        connection_success = game.connect_to_server()
        
        print(f"Connection result: {connection_success}")
        
        # Start game loop regardless of connection status
        print("Starting game...")
        game.run()
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        
        # Show error message
        try:
            screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("Error")
            font = pygame.font.Font(None, 36)
            
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                screen.fill(WHITE)
                error_text = font.render(f"Error: {str(e)}", True, RED)
                screen.blit(error_text, (50, 50))
                
                exit_text = font.render("Press X to exit", True, BLACK)
                screen.blit(exit_text, (50, 100))
                
                pygame.display.flip()
                
        except:
            print("Could not show error window")
            sys.exit(1)

if __name__ == "__main__":
    main()