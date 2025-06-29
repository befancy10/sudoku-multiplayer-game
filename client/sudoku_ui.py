import pygame

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
        self.font_small = pygame.font.Font(None, 18)
        
        # Scoreboard position
        self.scoreboard_x = self.board_x + self.board_size + 50
        self.scoreboard_y = self.board_y
        self.scoreboard_width = 200
        
    def draw_sudoku_board(self, puzzle, player_board, cell_status, selected_cell):
        """Draw the sudoku board with current state"""
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
                    # Color: black for given numbers, blue for player input
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
    
    def draw_scores(self, scores, current_player_name):
        """Draw player scores"""
        if not scores:
            return
        
        # Title
        title_text = self.font_medium.render("SCORES", True, BLACK)
        self.screen.blit(title_text, (self.scoreboard_x, self.scoreboard_y))
        
        y_offset = 40
        
        # Sort players by score (descending)
        sorted_players = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        for i, (player_id, player_info) in enumerate(sorted_players):
            player_name = player_info.get("name", player_id)
            score = player_info.get("score", 0)
            
            # Highlight current player
            text_color = RED if player_name == current_player_name else BLACK
            
            # Rank
            rank_text = f"{i+1}."
            rank_surface = self.font_small.render(rank_text, True, text_color)
            self.screen.blit(rank_surface, (self.scoreboard_x, self.scoreboard_y + y_offset))
            
            # Name
            name_text = f"{player_name}"
            name_surface = self.font_small.render(name_text, True, text_color)
            self.screen.blit(name_surface, (self.scoreboard_x + 30, self.scoreboard_y + y_offset))
            
            # Score
            score_text = f"{score}"
            score_surface = self.font_small.render(score_text, True, text_color)
            self.screen.blit(score_surface, (self.scoreboard_x + 130, self.scoreboard_y + y_offset))
            
            y_offset += 25
    
    def draw_players_progress(self, players_progress):
        """Draw other players' progress indicators"""
        if not players_progress:
            return
        
        progress_y = self.scoreboard_y + 250
        
        # Title
        title_text = self.font_medium.render("PLAYER PROGRESS", True, BLACK)
        self.screen.blit(title_text, (self.scoreboard_x, progress_y))
        
        y_offset = 40
        
        for player_id, progress in players_progress.items():
            player_name = progress.get("name", player_id)
            filled_cells = progress.get("filled_cells", 0)
            total_cells = progress.get("total_empty_cells", 81)
            
            # Progress bar
            bar_width = 150
            bar_height = 15
            bar_x = self.scoreboard_x
            bar_y = progress_y + y_offset + 15
            
            # Background
            pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Progress
            if total_cells > 0:
                progress_width = int((filled_cells / total_cells) * bar_width)
                pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, progress_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Player name
            name_text = self.font_small.render(player_name, True, BLACK)
            self.screen.blit(name_text, (bar_x, progress_y + y_offset))
            
            # Progress text
            progress_text = f"{filled_cells}/{total_cells}"
            progress_surface = self.font_small.render(progress_text, True, BLACK)
            self.screen.blit(progress_surface, (bar_x + bar_width + 10, progress_y + y_offset + 5))
            
            y_offset += 50
    
    def draw_instructions(self):
        """Draw game instructions"""
        instructions_y = self.board_y + self.board_size + 30
        
        instructions = [
            "Instructions:",
            "• Click a cell to select it",
            "• Press 1-9 to enter numbers",
            "• Press DELETE to clear cell",
            "• +10 points for correct answers",
            "• -10 points for wrong answers"
        ]
        
        for i, instruction in enumerate(instructions):
            text_color = BLACK if i == 0 else DARK_GRAY
            font = self.font_medium if i == 0 else self.font_small
            
            text = font.render(instruction, True, text_color)
            self.screen.blit(text, (self.board_x, instructions_y + i * 20))
    
    def get_cell_from_pos(self, pos):
        """Get sudoku cell coordinates from mouse position"""
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
    
    def draw_game_over(self, winner_info):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Winner text
        if winner_info:
            winner_text = f"Winner: {winner_info['name']} with {winner_info['score']} points!"
            winner_surface = self.font_medium.render(winner_text, True, WHITE)
            winner_rect = winner_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(winner_surface, winner_rect)
        
        # Continue instruction
        continue_text = "Press ESC to exit"
        continue_surface = self.font_small.render(continue_text, True, WHITE)
        continue_rect = continue_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        self.screen.blit(continue_surface, continue_rect)