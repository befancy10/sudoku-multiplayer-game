import pygame
import time

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)
DARK_GRAY = (169, 169, 169)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

class SudokuUI:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Board dimensions
        self.board_size = 450
        self.board_x = 50
        self.board_y = 50
        self.cell_size = self.board_size // 9
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Scoreboard position - consistent spacing
        self.scoreboard_x = self.board_x + self.board_size + 40
        self.scoreboard_y = self.board_y
        self.scoreboard_width = 280
        
        # Standard spacing constants
        self.section_spacing = 30
        self.line_spacing = 22
        self.item_spacing = 18
        self.margin = 15

    # Draw the sudoku board with current state
    def draw_sudoku_board(self, puzzle, player_board, cell_status, selected_cell):
        if not puzzle or not player_board or not cell_status:
            return
        
        # Draw board background
        board_rect = pygame.Rect(self.board_x, self.board_y, self.board_size, self.board_size)
        pygame.draw.rect(self.screen, WHITE, board_rect)
        pygame.draw.rect(self.screen, BLACK, board_rect, 3)
        
        # Draw cells
        for row in range(9):
            for col in range(9):
                x = self.board_x + col * self.cell_size
                y = self.board_y + row * self.cell_size
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                status = cell_status[row][col]

                # Determine cell color
                cell_color = WHITE
                if selected_cell and selected_cell == (row, col):
                    cell_color = YELLOW
                elif status == 'given':
                    cell_color = LIGHT_GREEN
                elif status == 'correct':
                    cell_color = LIGHT_BLUE
                elif status == 'incorrect':
                    cell_color = LIGHT_RED
                
                pygame.draw.rect(self.screen, cell_color, cell_rect)
                pygame.draw.rect(self.screen, BLACK, cell_rect, 1)
                
                # Draw number if present
                number = player_board[row][col]
                if number != 0:
                    if status == 'given':
                        text_color = BLACK
                    elif status == 'correct':
                        text_color = BLUE
                    elif status == 'incorrect':
                        text_color = RED
                    else:
                        text_color = GRAY
                    
                    text = self.font_large.render(str(number), True, text_color)
                    text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    self.screen.blit(text, text_rect)
        
        # Draw thick lines for 3x3 boxes
        for i in range(1, 3):
            # Vertical lines
            x = self.board_x + i * 3 * self.cell_size
            pygame.draw.line(self.screen, BLACK, (x, self.board_y), 
                           (x, self.board_y + self.board_size), 3)
            # Horizontal lines
            y = self.board_y + i * 3 * self.cell_size
            pygame.draw.line(self.screen, BLACK, (self.board_x, y), 
                           (self.board_x + self.board_size, y), 3)
    
    # Format duration in seconds to readable format
    def format_duration(self, duration_seconds):
        if duration_seconds is None:
            return "--:--"
        
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    # Get color for completion rank
    def get_rank_color(self, rank):
        if rank == 1:
            return GOLD
        elif rank == 2:
            return SILVER
        elif rank == 3:
            return BRONZE
        else:
            return GRAY
    
    # Draw player scores with completion ranking
    def draw_scores(self, scores, current_player_name):
        if not scores:
            return
        
        current_y = self.scoreboard_y
        
        # Title with consistent styling
        title_text = self.font_medium.render("LEADERBOARD", True, BLACK)
        self.screen.blit(title_text, (self.scoreboard_x, current_y))
        current_y += self.section_spacing
        
        # Separate completed and playing players
        completed_players = []
        playing_players = []
        
        for player_id, player_info in scores.items():
            if player_info.get("player_status") == "completed":
                completed_players.append((player_id, player_info))
            else:
                playing_players.append((player_id, player_info))
        
        # Sort completed players by completion rank
        completed_players.sort(key=lambda x: x[1].get("completion_rank", 999))
        
        # Sort playing players by current score
        playing_players.sort(key=lambda x: x[1].get("score", 0), reverse=True)
        
        # Display completed players first
        if completed_players:
            # Completed section header
            completed_header = self.font_small.render("COMPLETED:", True, GREEN)
            self.screen.blit(completed_header, (self.scoreboard_x, current_y))
            current_y += self.line_spacing
            
            for player_id, player_info in completed_players:
                player_name = player_info.get("name", player_id)
                score = player_info.get("score", 0)
                completion_rank = player_info.get("completion_rank", 0)
                completion_duration = player_info.get("completion_duration", 0)
                
                # Highlight current player
                text_color = RED if player_name == current_player_name else BLACK
                rank_color = self.get_rank_color(completion_rank)
                
                # Rank with medal colors (aligned)
                rank_text = f"#{completion_rank}"
                rank_surface = self.font_small.render(rank_text, True, rank_color)
                self.screen.blit(rank_surface, (self.scoreboard_x + 5, current_y))
                
                # Name (aligned)
                name_text = f"{player_name}"
                name_surface = self.font_small.render(name_text, True, text_color)
                self.screen.blit(name_surface, (self.scoreboard_x + 40, current_y))
                
                # Score (right-aligned)
                score_text = f"{score}pts"
                score_surface = self.font_small.render(score_text, True, text_color)
                self.screen.blit(score_surface, (self.scoreboard_x + 140, current_y))
                
                # Completion time (right-aligned)
                time_text = self.format_duration(completion_duration)
                time_surface = self.font_tiny.render(time_text, True, GREEN)
                self.screen.blit(time_surface, (self.scoreboard_x + 190, current_y))
                
                # Status indicator (right-aligned)
                status_surface = self.font_tiny.render("C", True, GREEN)
                self.screen.blit(status_surface, (self.scoreboard_x + 240, current_y))
                
                current_y += self.item_spacing
        
        # Display playing players
        if playing_players:
            # Add spacing if there were completed players
            if completed_players:
                current_y += self.margin
            
            # Playing section header
            playing_header = self.font_small.render("PLAYING:", True, BLUE)
            self.screen.blit(playing_header, (self.scoreboard_x, current_y))
            current_y += self.line_spacing
            
            for i, (player_id, player_info) in enumerate(playing_players):
                player_name = player_info.get("name", player_id)
                score = player_info.get("score", 0)
                
                # Highlight current player
                text_color = RED if player_name == current_player_name else BLACK
                
                # Temporary rank among playing players (aligned)
                temp_rank = f"{i+1}."
                rank_surface = self.font_small.render(temp_rank, True, text_color)
                self.screen.blit(rank_surface, (self.scoreboard_x + 5, current_y))
                
                # Name (aligned)
                name_text = f"{player_name}"
                name_surface = self.font_small.render(name_text, True, text_color)
                self.screen.blit(name_surface, (self.scoreboard_x + 40, current_y))
                
                # Score (right-aligned)
                score_text = f"{score}pts"
                score_surface = self.font_small.render(score_text, True, text_color)
                self.screen.blit(score_surface, (self.scoreboard_x + 140, current_y))
                
                # Status indicator (right-aligned)
                status_surface = self.font_tiny.render("P", True, BLUE)
                self.screen.blit(status_surface, (self.scoreboard_x + 240, current_y))
                
                current_y += self.item_spacing
        
        # Legend with consistent spacing
        current_y += self.margin
        legend_items = [
            ("C = Completed", GREEN),
            ("P = Playing", BLUE),
            ("Time = Minute:Second", BLACK)
        ]
        
        for i, (legend_text, color) in enumerate(legend_items):
            legend_surface = self.font_tiny.render(legend_text, True, color)
            self.screen.blit(legend_surface, (self.scoreboard_x, current_y + i * 14))
    
    # Draw other players' progress indicators
    def draw_players_progress(self, players_progress):
        if not players_progress:
            return
        
        # Position below scoreboard with consistent spacing
        progress_y = self.scoreboard_y + 320
        current_y = progress_y
        
        # Title with consistent styling
        title_text = self.font_medium.render("PROGRESS", True, BLACK)
        self.screen.blit(title_text, (self.scoreboard_x, current_y))
        current_y += self.section_spacing
        
        # Sort by completion status and progress
        sorted_progress = sorted(
            players_progress.items(),
            key=lambda x: (
                x[1].get("player_status") == "completed",
                -x[1].get("completion_percentage", 0)
            ),
            reverse=True
        )
        
        for player_id, progress in sorted_progress:
            player_name = progress.get("name", player_id)
            filled_cells = progress.get("filled_cells", 0)
            total_cells = progress.get("total_empty_cells", 81)
            completion_percentage = progress.get("completion_percentage", 0)
            player_status = progress.get("player_status", "playing")
            completion_rank = progress.get("completion_rank")
            
            # Player name with status (consistent height)
            if player_status == "completed":
                name_display = f"{player_name} (#{completion_rank})"
                name_color = GREEN
            else:
                name_display = player_name
                name_color = BLACK
                
            name_text = self.font_small.render(name_display, True, name_color)
            self.screen.blit(name_text, (self.scoreboard_x, current_y))
            
            # Progress bar (consistent positioning)
            bar_width = 160
            bar_height = 12
            bar_x = self.scoreboard_x
            bar_y = current_y + self.line_spacing - 2
            
            # Background
            pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar color based on status
            if player_status == "completed":
                progress_color = GREEN
                bar_progress = 1.0
            else:
                progress_color = BLUE
                bar_progress = completion_percentage / 100.0
            
            # Progress fill
            if total_cells > 0:
                progress_width = int(bar_progress * bar_width)
                pygame.draw.rect(self.screen, progress_color, (bar_x, bar_y, progress_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)
            
            # Progress text (aligned right of progress bar)
            if player_status == "completed":
                progress_text = "DONE!"
                progress_color_text = GREEN
            else:
                progress_text = f"{filled_cells}/{total_cells} ({completion_percentage:.0f}%)"
                progress_color_text = BLACK
                
            progress_surface = self.font_tiny.render(progress_text, True, progress_color_text)
            self.screen.blit(progress_surface, (bar_x + bar_width + 10, bar_y + 2))
            
            current_y += 40  # Consistent spacing between progress items
    
    # Draw game instructions
    def draw_instructions(self):
        instructions_y = self.board_y + self.board_size + self.section_spacing
        current_y = instructions_y
        
        instructions = [
            "Instructions:",
            "• Click a cell to select it",
            "• Press 1-9 to enter numbers", 
            "• Press DELETE to clear cell",
            "• +10 points for correct answers",
            "• -10 points for wrong answers",
            "",
            "Ranking by score first, then completion time",
            "Accuracy matters more than speed!"
        ]
        
        for i, instruction in enumerate(instructions):
            if instruction == "":
                current_y += 8  # Smaller gap for empty lines
                continue
                
            # Consistent font and color choices
            if i == 0:  # Title
                font = self.font_medium
                text_color = BLACK
            elif "Ranking" in instruction or "Accuracy" in instruction:  # Emphasis
                font = self.font_small
                text_color = BLUE
            else:  # Regular instructions
                font = self.font_small
                text_color = DARK_GRAY
            
            text = font.render(instruction, True, text_color)
            self.screen.blit(text, (self.board_x, current_y))
            current_y += self.item_spacing
    
    # Get sudoku cell coordinates from mouse position
    def get_cell_from_pos(self, pos):
        x, y = pos
        
        # Check if click is within board
        if (self.board_x <= x <= self.board_x + self.board_size and 
            self.board_y <= y <= self.board_y + self.board_size):
            
            col = (x - self.board_x) // self.cell_size
            row = (y - self.board_y) // self.cell_size
            
            # Ensure valid coordinates
            if 0 <= row < 9 and 0 <= col < 9:
                return (row, col)
        
        return None
    
    # Draw game over screen with completion ranking
    def draw_game_over(self, winner_info, completion_order):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        center_x = self.screen_width // 2
        current_y = self.screen_height // 2 - 120
        
        # Game over text
        game_over_text = self.font_large.render("GAME COMPLETE!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(center_x, current_y))
        self.screen.blit(game_over_text, game_over_rect)
        current_y += 50
        
        # Winner text
        if winner_info:
            winner_text = f"Winner: {winner_info['name']}"
            winner_surface = self.font_medium.render(winner_text, True, GOLD)
            winner_rect = winner_surface.get_rect(center=(center_x, current_y))
            self.screen.blit(winner_surface, winner_rect)
            current_y += 30
            
            # Winner details
            score_text = f"Score: {winner_info.get('score', 0)} points"
            score_surface = self.font_small.render(score_text, True, WHITE)
            score_rect = score_surface.get_rect(center=(center_x, current_y))
            self.screen.blit(score_surface, score_rect)
            current_y += 20
            
            time_text = f"Time: {self.format_duration(winner_info.get('completion_duration', 0))}"
            time_surface = self.font_small.render(time_text, True, WHITE)
            time_rect = time_surface.get_rect(center=(center_x, current_y))
            self.screen.blit(time_surface, time_rect)
            current_y += 35
        
        # Final rankings
        if completion_order:
            rankings_title = self.font_medium.render("Final Rankings:", True, WHITE)
            rankings_rect = rankings_title.get_rect(center=(center_x, current_y))
            self.screen.blit(rankings_title, rankings_rect)
            current_y += 30
            
            for i, player in enumerate(completion_order[:3]):  # Show top 3
                rank_color = self.get_rank_color(i + 1)
                score_text = f"{player.get('score', 0)}pts"
                time_text = self.format_duration(player.get('completion_duration', 0))
                rank_text = f"#{i+1}: {player['name']} - {score_text} - {time_text}"
                
                rank_surface = self.font_small.render(rank_text, True, rank_color)
                rank_rect = rank_surface.get_rect(center=(center_x, current_y))
                self.screen.blit(rank_surface, rank_rect)
                current_y += 22
        
        # Continue instruction
        current_y += 30
        continue_text = "Press ESC to exit"
        continue_surface = self.font_small.render(continue_text, True, WHITE)
        continue_rect = continue_surface.get_rect(center=(center_x, current_y))
        self.screen.blit(continue_surface, continue_rect)
    
    # Draw notification when a player completes the puzzle
    def draw_player_completed_notification(self, player_name, rank, completion_time):
        notification_text = f"{player_name} finished #{rank}! Time: {self.format_duration(completion_time)}"
        notification_surface = self.font_medium.render(notification_text, True, GREEN)
        
        # Center at top of screen
        notification_rect = notification_surface.get_rect(center=(self.screen_width//2, 35))
        
        # Background with consistent styling
        bg_rect = notification_rect.inflate(30, 16)
        pygame.draw.rect(self.screen, WHITE, bg_rect)
        pygame.draw.rect(self.screen, GREEN, bg_rect, 2)
        
        self.screen.blit(notification_surface, notification_rect)