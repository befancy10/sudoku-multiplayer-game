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
GOLD = (255, 215, 0)

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
        self.cell_status = None  # untuk menyimpan status tiap sel
        self.scores = {}
        self.players_progress = {}
        
        # Individual completion tracking
        self.player_completed = False
        self.completion_time = None
        self.completion_rank = None
        self.game_finished = False
        self.completion_notification = None  # For showing completion messages
        self.notification_timer = 0
        
        # Ranking announcement tracking
        self.last_completed_count = 0  # Track how many players were completed in last check
        self.ranking_announcement = None  # Store current ranking announcement
        self.ranking_announcement_timer = 0
        
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
        
    # Connect to the game server
    def connect_to_server(self):
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
            
            logging.info(f"Connecting to {server_ip}:{server_port} as {self.player_name}...")
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
    
    # Load the sudoku puzzle from server
    def load_puzzle(self):
        try:
            logging.info("Loading puzzle and player board...")
            board_response = self.client.send_command({
                "command": "get_player_board",
                "player_id": self.player_id,
                "data": {}
            })

            if board_response["status"] == "OK":
                self.player_board = board_response["data"]["board"]
                self.cell_status = board_response["data"]["cell_status"]
                logging.info("Player board loaded")
            else:
                logging.error(f"Failed to load player board: {board_response['message']}")

            puzzle_response = self.client.get_puzzle()
            if puzzle_response["status"] == "OK":
                self.puzzle = puzzle_response["data"]["puzzle"]
                logging.info("Puzzle loaded")
            else:
                logging.error(f"Failed to load puzzle: {puzzle_response['message']}")
            
        except Exception as e:
            logging.error(f"Error loading puzzle: {e}")
    
    # Start background thread for updates
    def start_update_thread(self):
        try:
            self.update_running = True
            self.update_thread = threading.Thread(target=self.update_game_state)
            self.update_thread.daemon = True
            self.update_thread.start()
            print("Update thread started")  # DEBUG
        except Exception as e:
            logging.error(f"Failed to start update thread: {e}")
    
    # Background thread to update game state
    def update_game_state(self):
        while self.update_running and self.connected:
            try:
                # Update scores
                scores_response = self.client.get_scores()
                if scores_response and scores_response["status"] == "OK":
                    new_scores = scores_response["data"]["scores"]
                    
                    # Check for new completions and get ranking announcements
                    self.check_for_completions_and_rankings(new_scores)
                    
                    self.scores = new_scores
                
                # Update players progress
                progress_response = self.client.get_player_progress()
                if progress_response and progress_response["status"] == "OK":
                    self.players_progress = progress_response["data"]["progress"]
                
                # Update game state
                game_state_response = self.client.get_game_state()
                if game_state_response and game_state_response["status"] == "OK":
                    game_state = game_state_response["data"]
                    
                    # Check if game is finished and show final ranking
                    if game_state.get("game_state") == "finished" and not self.game_finished:
                        self.game_finished = True
                        self.show_final_ranking()
                        logging.info("Game finished! All players completed.")
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                logging.error(f"Error updating game state: {e}")
                time.sleep(5)  # Wait longer on error
    
    # Check for newly completed players and fetch ranking announcements
    def check_for_completions_and_rankings(self, new_scores):
        try:
            # Count completed players
            current_completed_count = sum(1 for info in new_scores.values() if info.get("player_status") == "completed")
            
            # Check if someone new completed
            if current_completed_count > self.last_completed_count:
                # Someone new completed, fetch current ranking
                self.fetch_and_show_current_ranking()
                self.last_completed_count = current_completed_count
            
            # Check for individual player completions for notifications
            for player_id, player_info in new_scores.items():
                if player_info.get("player_status") == "completed":
                    # Check if this is a new completion
                    old_info = self.scores.get(player_id, {})
                    if old_info.get("player_status") != "completed":
                        # New completion detected
                        player_name = player_info.get("name", player_id)
                        completion_rank = player_info.get("completion_rank", 0)
                        completion_duration = player_info.get("completion_duration", 0)
                        
                        if player_id == self.player_id:
                            # This player completed
                            self.player_completed = True
                            self.completion_time = completion_duration
                            self.completion_rank = completion_rank
                            self.show_completion_notification(f"You finished #{completion_rank}!", True)
                            logging.info(f"Congratulations! You completed the puzzle!")
                            logging.info(f"You completed the puzzle! Rank: #{completion_rank}")
                        else:
                            # Another player completed
                            self.show_completion_notification(f"{player_name} finished #{completion_rank}!", False)
                            logging.info(f"{player_name} completed the puzzle! Rank: #{completion_rank}")
                            
        except Exception as e:
            logging.error(f"Error checking new completions: {e}")
    
    # Fetch current ranking from server and display announcement
    def fetch_and_show_current_ranking(self):
        try:
            ranking_response = self.client.get_current_ranking()
            if ranking_response and ranking_response["status"] == "OK":
                ranking_data = ranking_response["data"]
                ranking_text = ranking_data.get("ranking_text", "")
                
                # Log the ranking announcement
                logging.info(ranking_text)
                
                # Show ranking announcement in UI
                self.show_ranking_announcement(ranking_text)
                
        except Exception as e:
            logging.error(f"Error fetching current ranking: {e}")
    
    # Show final ranking when game finishes
    def show_final_ranking(self):
        try:
            ranking_response = self.client.get_current_ranking()
            if ranking_response and ranking_response["status"] == "OK":
                ranking_data = ranking_response["data"]
                ranking_text = ranking_data.get("ranking_text", "")
                
                # Convert to final ranking format
                final_ranking_text = ranking_text.replace("Current Ranking:", "Final Ranking:")
                
                # Log the final ranking
                logging.info("Game finished! All players completed.")
                logging.info(final_ranking_text)
                
                # Show final ranking announcement in UI
                self.show_ranking_announcement(final_ranking_text, is_final=True)
                
        except Exception as e:
            logging.error(f"Error showing final ranking: {e}")
    
    # Show completion notification
    def show_completion_notification(self, message, is_self=False):
        self.completion_notification = {
            "message": message,
            "is_self": is_self,
            "start_time": time.time()
        }
        self.notification_timer = 5.0  # Show for 5 seconds
    
    # Show ranking announcement
    def show_ranking_announcement(self, ranking_text, is_final=False):
        self.ranking_announcement = {
            "text": ranking_text,
            "is_final": is_final,
            "start_time": time.time()
        }
        self.ranking_announcement_timer = 8.0  # Show for 8 seconds
    
    # Handle clicking on a sudoku cell
    def handle_cell_click(self, row, col):
        # Block input if player is completed
        if self.player_completed:
            print("You have completed the puzzle! You can only spectate now.")
            return
            
        if self.puzzle and self.puzzle[row][col] == 0:
            if self.cell_status and self.cell_status[row][col] != 'correct':
                self.selected_cell = (row, col)
    
    # Handle number input for selected cell
    def handle_number_input(self, number):
        # Block input if player is completed
        if self.player_completed:
            print("You have completed the puzzle! You can only spectate now.")
            return
            
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
                        self.cell_status = result.get("cell_status", self.cell_status)
                        self.player_board = result.get("board", self.player_board)
                        self.player_board[row][col] = number
                        
                        # Handle answer feedback
                        if result["correct"]:
                            logging.info(f"Correct! +10 points. Cell ({row},{col}) = {number}")
                            print(f"Correct! Score: {result['new_score']}")
                        else:
                            logging.info(f"Incorrect! -10 points. Cell ({row},{col}) ≠ {number}")
                            print(f"Incorrect! Score: {result['new_score']}")
                        
                        # Handle player completion
                        if result.get("player_completed", False):
                            self.player_completed = True
                            print(f"🎉 Congratulations! You completed the puzzle!")
                            # Completion details will be updated in the next score update
                        
                        # Handle game completion
                        if result.get("game_complete", False):
                            self.game_finished = True
                            print("🏁 Game finished! All players have completed.")
                            
                    else:
                        error_msg = response.get("message", "Unknown error") if response else "No response"
                        logging.error(f"Failed to submit answer: {error_msg}")
                        print(f"Submit failed: {error_msg}")
                        
                        # Special message for completed players
                        if "already completed" in error_msg:
                            self.player_completed = True
                        
                except Exception as e:
                    logging.error(f"Error submitting answer: {e}")
                    print(f"Submit error: {e}")
    
    # Handle pygame events
    def handle_events(self):
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
                    if self.game_finished:
                        # Allow exit when game is finished
                        self.running = False
                    else:
                        self.selected_cell = None
    
    # Draw completion notification overlay
    def draw_completion_notification(self):
        if self.completion_notification and self.notification_timer > 0:
            current_time = time.time()
            elapsed = current_time - self.completion_notification["start_time"]
            
            if elapsed < 5.0:  # Show for 5 seconds
                message = self.completion_notification["message"]
                is_self = self.completion_notification["is_self"]
                
                # Determine colors
                if is_self:
                    bg_color = GREEN
                    text_color = WHITE
                else:
                    bg_color = BLUE
                    text_color = WHITE
                
                # Create notification
                font = pygame.font.Font(None, 32)
                text_surface = font.render(message, True, text_color)
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, 80))
                
                # Background
                bg_rect = text_rect.inflate(40, 20)
                pygame.draw.rect(self.screen, bg_color, bg_rect)
                pygame.draw.rect(self.screen, BLACK, bg_rect, 3)
                
                # Text
                self.screen.blit(text_surface, text_rect)
                
                # Fade effect (optional)
                alpha = max(0, 255 - int((elapsed / 5.0) * 255))
                if alpha < 255:
                    fade_surface = pygame.Surface(bg_rect.size)
                    fade_surface.set_alpha(255 - alpha)
                    fade_surface.fill(WHITE)
                    self.screen.blit(fade_surface, bg_rect)
            else:
                # Clear notification
                self.completion_notification = None
                self.notification_timer = 0
    
    # Draw ranking announcement overlay
    def draw_ranking_announcement(self):
        if self.ranking_announcement and self.ranking_announcement_timer > 0:
            current_time = time.time()
            elapsed = current_time - self.ranking_announcement["start_time"]
            
            if elapsed < 8.0:  # Show for 8 seconds
                ranking_text = self.ranking_announcement["text"]
                is_final = self.ranking_announcement["is_final"]
                
                # Split text into lines
                lines = ranking_text.split('\n')
                
                # Colors
                bg_color = GOLD if is_final else LIGHT_BLUE
                text_color = BLACK
                header_color = RED if is_final else BLUE
                
                # Calculate position and size
                font_header = pygame.font.Font(None, 28)
                font_line = pygame.font.Font(None, 20)
                
                # Measure text dimensions
                line_height = 25
                header_height = 35
                margin = 20
                
                max_width = 0
                total_height = header_height + (len(lines) - 1) * line_height + margin * 2
                
                for line in lines:
                    if line.strip():
                        font = font_header if lines.index(line) == 0 else font_line
                        text_surface = font.render(line, True, text_color)
                        max_width = max(max_width, text_surface.get_width())
                
                # Position overlay in center-right area
                overlay_width = max_width + margin * 2
                overlay_height = total_height
                overlay_x = WINDOW_WIDTH - overlay_width - 20
                overlay_y = 120
                
                # Background
                overlay_rect = pygame.Rect(overlay_x, overlay_y, overlay_width, overlay_height)
                pygame.draw.rect(self.screen, bg_color, overlay_rect)
                pygame.draw.rect(self.screen, BLACK, overlay_rect, 3)
                
                # Draw text lines
                y_offset = overlay_y + margin
                for i, line in enumerate(lines):
                    if line.strip():
                        font = font_header if i == 0 else font_line
                        color = header_color if i == 0 else text_color
                        
                        text_surface = font.render(line, True, color)
                        text_x = overlay_x + margin
                        
                        self.screen.blit(text_surface, (text_x, y_offset))
                        
                        if i == 0:
                            y_offset += header_height
                        else:
                            y_offset += line_height
                
                # Fade effect for the last 2 seconds
                if elapsed > 6.0:
                    fade_progress = (elapsed - 6.0) / 2.0  # 0 to 1 over 2 seconds
                    alpha = int(255 * fade_progress)
                    fade_surface = pygame.Surface((overlay_width, overlay_height))
                    fade_surface.set_alpha(alpha)
                    fade_surface.fill(WHITE)
                    self.screen.blit(fade_surface, (overlay_x, overlay_y))
            else:
                # Clear announcement
                self.ranking_announcement = None
                self.ranking_announcement_timer = 0
    
    # Draw current player status
    def draw_player_status(self):
        status_y = 20
        font = pygame.font.Font(None, 24)
        
        if self.player_completed:
            if self.completion_rank:
                status_text = f"Status: COMPLETED (Rank #{self.completion_rank})"
                if self.completion_time:
                    minutes = int(self.completion_time // 60)
                    seconds = int(self.completion_time % 60)
                    status_text += f" - Time: {minutes:02d}:{seconds:02d}"
            else:
                status_text = "Status: COMPLETED - Spectating..."
            status_color = GREEN
        else:
            status_text = "Status: Playing..."
            status_color = BLUE
        
        status_surface = font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (10, status_y))
    
    # Draw connection status when not connected
    def draw_connection_status(self):
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
                "4. If game is full, wait for the next game generated"
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
    
    # Main game loop
    def run(self):
        print("Starting game loop...")  # DEBUG
        
        while self.running:
            try:
                self.handle_events()
                
                # Clear screen
                self.screen.fill(WHITE)
                
                if self.connected and self.puzzle:
                    # Draw the game
                    self.ui.draw_sudoku_board(self.puzzle, self.player_board, self.cell_status, self.selected_cell)
                    self.ui.draw_scores(self.scores, self.player_name)
                    self.ui.draw_players_progress(self.players_progress)
                    self.ui.draw_instructions()
                    
                    # Draw player status
                    self.draw_player_status()
                    
                    # Draw completion notifications
                    self.draw_completion_notification()
                    
                    # Draw ranking announcements
                    self.draw_ranking_announcement()
                    
                    # Draw game over screen if finished
                    if self.game_finished:
                        # Get completion order from scores
                        completion_order = []
                        for player_id, player_info in self.scores.items():
                            if player_info.get("player_status") == "completed":
                                completion_order.append({
                                    "name": player_info.get("name"),
                                    "completion_duration": player_info.get("completion_duration"),
                                    "score": player_info.get("score"),
                                    "rank": player_info.get("completion_rank")
                                })
                        
                        # Sort by rank
                        completion_order.sort(key=lambda x: x.get("rank", 999))
                        
                        # Get winner (first in completion order)
                        winner_info = completion_order[0] if completion_order else None
                        
                        self.ui.draw_game_over(winner_info, completion_order)
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
    
    # Cleanup resources
    def cleanup(self):
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

# Main function with better error handling
def main():
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