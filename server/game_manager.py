import threading
import time
import logging
from sudoku_generator import SudokuGenerator

class GameManager:
    def __init__(self, max_players=4):
        self.max_players = max_players
        self.players = {}  # player_id: player_info
        self.current_puzzle = None
        self.solution = None
        self.game_state = "waiting"  # waiting, playing, finished
        self.game_start_time = None
        
        # SIMPLIFIED THREAD SAFETY - Remove complex locking that might hang
        self.lock = threading.RLock()  # Use RLock instead of Lock
        
        # Generate initial puzzle
        self.generate_new_puzzle()
        
        logging.info("Game Manager initialized")
    
    def generate_new_puzzle(self):
        """Generate a new sudoku puzzle - FIXED VERSION"""
        try:
            # TRY generator first, fallback to mock if it hangs
            generator = SudokuGenerator()
            self.current_puzzle, self.solution = generator.generate_puzzle()
            logging.info("New puzzle generated")
            return True
        except Exception as e:
            logging.warning(f"Puzzle generation failed, using mock puzzle: {e}")
            # FALLBACK: Use mock puzzle
            self.current_puzzle = [
                [5, 3, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 9, 5, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [8, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 8, 0, 3, 0, 0, 1],
                [7, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 1, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 9]
            ]
            
            self.solution = [
                [5, 3, 4, 6, 7, 8, 9, 1, 2],
                [6, 7, 2, 1, 9, 5, 3, 4, 8],
                [1, 9, 8, 3, 4, 2, 5, 6, 7],
                [8, 5, 9, 7, 6, 1, 4, 2, 3],
                [4, 2, 6, 8, 5, 3, 7, 9, 1],
                [7, 1, 3, 9, 2, 4, 8, 5, 6],
                [9, 6, 1, 5, 3, 7, 2, 8, 4],
                [2, 8, 7, 4, 1, 9, 6, 3, 5],
                [3, 4, 5, 2, 8, 6, 1, 7, 9]
            ]
            logging.info("Mock puzzle loaded")
            return True
    
    def add_player(self, player_id, player_name):
        """Add a new player to the game - FIXED VERSION"""
        try:
            # Quick validation without lock first
            if len(self.players) >= self.max_players:
                return False, "Game is full"
            
            if player_id in self.players:
                return False, "Player ID already exists"
            
            # ACQUIRE LOCK FOR MINIMAL TIME
            with self.lock:
                # Double-check inside lock (thread safety)
                if len(self.players) >= self.max_players:
                    return False, "Game is full"
                
                if player_id in self.players:
                    return False, "Player ID already exists"
                
                # Create player info with cell status tracking
                player_info = {
                    "player_id": player_id,
                    "name": player_name,
                    "score": 0,
                    "join_time": time.time(),
                    "moves": [],
                    "board": self.get_initial_board(),
                    "cell_status": self.get_initial_cell_status(),  # NEW: Track correct/incorrect/empty
                    "filled_cells": 0,
                    "correct_answers": 0,
                    "wrong_answers": 0
                }
                
                # Add player
                self.players[player_id] = player_info
                
                # Start game if this is the first player - SIMPLIFIED
                if len(self.players) == 1 and self.game_state == "waiting":
                    self.game_state = "playing"
                    self.game_start_time = time.time()
                    logging.info("Game started!")
            
            # Log outside of lock
            logging.info(f"Player {player_name} ({player_id}) joined. Total players: {len(self.players)}")
            return True, "Player added successfully"
            
        except Exception as e:
            logging.error(f"Error in add_player: {e}")
            return False, f"Error adding player: {str(e)}"
    
    def get_initial_cell_status(self):
        """Initialize cell status matrix"""
        # Status: 'given' (original puzzle), 'correct' (correct answer), 'incorrect' (wrong answer), 'empty'
        status = [['empty' for _ in range(9)] for _ in range(9)]
        
        # Mark given numbers as 'given'
        for i in range(9):
            for j in range(9):
                if self.current_puzzle[i][j] != 0:
                    status[i][j] = 'given'
        
        return status
    
    def remove_player(self, player_id):
        """Remove a player from the game"""
        try:
            with self.lock:
                if player_id in self.players:
                    player_name = self.players[player_id]["name"]
                    del self.players[player_id]
                    logging.info(f"Player {player_name} ({player_id}) removed. Remaining players: {len(self.players)}")
                    
                    # End game if no players left
                    if len(self.players) == 0:
                        self.game_state = "waiting"
                    
                    return True
                return False
        except Exception as e:
            logging.error(f"Error removing player {player_id}: {e}")
            return False
    
    def get_initial_board(self):
        """Get a copy of the initial puzzle board"""
        if not self.current_puzzle:
            return None
        
        # Return a deep copy of the puzzle
        return [row[:] for row in self.current_puzzle]
    
    def submit_answer(self, player_id, row, col, value):
        """Process a player's answer submission - UPDATED FOR NEW BEHAVIOR"""
        try:
            with self.lock:
                if player_id not in self.players:
                    return False, "Player not found", {}
                
                if self.game_state != "playing":
                    return False, "Game not in progress", {}
                
                player = self.players[player_id]
                
                # Validate coordinates
                if not (0 <= row < 9 and 0 <= col < 9):
                    return False, "Invalid coordinates", {}
                
                # Check if cell is modifiable (cannot modify given numbers)
                if self.current_puzzle[row][col] != 0:
                    return False, "Cannot modify given numbers", {}
                
                # NEW: Check if cell is already correct (locked)
                if player["cell_status"][row][col] == 'correct':
                    return False, "Cannot modify correct answers", {}
                
                # Check if value is valid (1-9 or 0 for clear)
                if not (0 <= value <= 9):
                    return False, "Invalid value", {}
                
                # Handle clearing cell
                if value == 0:
                    old_status = player["cell_status"][row][col]
                    if old_status == 'incorrect':
                        player["board"][row][col] = 0
                        player["cell_status"][row][col] = 'empty'
                        player["filled_cells"] -= 1
                    elif old_status == 'empty':
                        # Already empty, no change
                        pass
                    # Note: 'correct' cells cannot be cleared (blocked above)
                    
                    result = {
                        "correct": True,  # Clearing is always "successful"
                        "score_change": 0,
                        "new_score": player["score"],
                        "game_complete": False,
                        "cell_status": player["cell_status"],
                        "board": player["board"]
                    }
                    
                    # Record move
                    move = {
                        "timestamp": time.time(),
                        "row": row,
                        "col": col,
                        "value": value,
                        "correct": True,
                        "score_change": 0
                    }
                    player["moves"].append(move)
                    
                    return True, "Cell cleared", result
                
                # Check if correct answer
                is_correct = (value == self.solution[row][col])
                
                # Update player's board and status
                old_status = player["cell_status"][row][col]
                player["board"][row][col] = value
                
                # Calculate score change
                score_change = 0
                if is_correct:
                    score_change = 10
                    player["correct_answers"] += 1
                    player["cell_status"][row][col] = 'correct'  # Lock this cell
                    if old_status == 'empty':
                        player["filled_cells"] += 1
                    # If was incorrect before, still count as filled
                else:
                    score_change = -10
                    player["wrong_answers"] += 1
                    player["cell_status"][row][col] = 'incorrect'  # Mark as incorrect but keep value
                    if old_status == 'empty':
                        player["filled_cells"] += 1
                    # Keep the wrong value displayed in red
                
                # Update score
                player["score"] += score_change
                
                # Record move
                move = {
                    "timestamp": time.time(),
                    "row": row,
                    "col": col,
                    "value": value,
                    "correct": is_correct,
                    "score_change": score_change
                }
                player["moves"].append(move)
                
                # Check if game is complete
                if self.check_game_completion():
                    self.game_state = "finished"
                    logging.info("Game completed!")
                
                result = {
                    "correct": is_correct,
                    "score_change": score_change,
                    "new_score": player["score"],
                    "game_complete": self.game_state == "finished",
                    # "cell_status": "correct" if is_correct else "incorrect"
                    "cell_status": player["cell_status"]
                }
                
                return True, "Answer processed", result
                
        except Exception as e:
            logging.error(f"Error in submit_answer: {e}")
            return False, f"Error processing answer: {str(e)}", {}
    
    def get_player_board_with_status(self, player_id):
        """Get player's board with cell status information"""
        try:
            with self.lock:
                if player_id not in self.players:
                    return None, None
                
                player = self.players[player_id]
                return player["board"], player["cell_status"]
        except Exception as e:
            logging.error(f"Error getting player board: {e}")
            return None, None
    
    def check_game_completion(self):
        """Check if any player has completed the puzzle"""
        try:
            for player in self.players.values():
                if self.is_board_complete(player["board"]):
                    return True
            return False
        except:
            return False
    
    def is_board_complete(self, board):
        """Check if a board is completely and correctly filled"""
        try:
            for i in range(9):
                for j in range(9):
                    if board[i][j] != self.solution[i][j]:
                        return False
            return True
        except:
            return False
    
    def get_scores(self):
        """Get all player scores"""
        try:
            with self.lock:
                scores = {}
                for player_id, player in self.players.items():
                    scores[player_id] = {
                        "name": player["name"],
                        "score": player["score"],
                        "correct_answers": player["correct_answers"],
                        "wrong_answers": player["wrong_answers"]
                    }
                return scores
        except Exception as e:
            logging.error(f"Error getting scores: {e}")
            return {}
    
    def get_player_progress(self):
        """Get progress information for all players"""
        try:
            with self.lock:
                progress = {}
                total_empty_cells = sum(1 for i in range(9) for j in range(9) if self.current_puzzle[i][j] == 0)
                
                for player_id, player in self.players.items():
                    progress[player_id] = {
                        "name": player["name"],
                        "filled_cells": player["filled_cells"],
                        "total_empty_cells": total_empty_cells,
                        "completion_percentage": (player["filled_cells"] / total_empty_cells * 100) if total_empty_cells > 0 else 0
                    }
                
                return progress
        except Exception as e:
            logging.error(f"Error getting progress: {e}")
            return {}
    
    def get_game_state(self):
        """Get current game state"""
        try:
            with self.lock:
                state = {
                    "game_state": self.game_state,
                    "players_count": len(self.players),
                    "max_players": self.max_players,
                    "game_duration": time.time() - self.game_start_time if self.game_start_time else 0
                }
                
                if self.game_state == "finished":
                    state["winner"] = self.get_winner()
                
                return state
        except Exception as e:
            logging.error(f"Error getting game state: {e}")
            return {
                "game_state": "error",
                "players_count": 0,
                "max_players": self.max_players,
                "game_duration": 0
            }
    
    def get_winner(self):
        """Get the winner of the game"""
        try:
            if not self.players:
                return None
            
            # Sort players by score (descending)
            sorted_players = sorted(
                self.players.values(),
                key=lambda p: p["score"],
                reverse=True
            )
            
            winner = sorted_players[0]
            return {
                "player_id": winner["player_id"],
                "name": winner["name"],
                "score": winner["score"],
                "correct_answers": winner["correct_answers"],
                "wrong_answers": winner["wrong_answers"]
            }
        except:
            return None
    
    def is_game_complete(self):
        """Check if the game is complete"""
        return self.game_state == "finished"
    
    def get_puzzle(self):
        """Get the current puzzle"""
        return self.current_puzzle
    
    def get_solution(self):
        """Get the solution (for debugging/admin purposes)"""
        return self.solution
    
    def reset_game(self):
        """Reset the game with a new puzzle"""
        try:
            with self.lock:
                # Generate new puzzle
                if not self.generate_new_puzzle():
                    return False
                
                # Reset all players
                for player in self.players.values():
                    player["score"] = 0
                    player["moves"] = []
                    player["board"] = self.get_initial_board()
                    player["cell_status"] = self.get_initial_cell_status()
                    player["filled_cells"] = 0
                    player["correct_answers"] = 0
                    player["wrong_answers"] = 0
                
                # Reset game state
                self.game_state = "playing" if self.players else "waiting"
                self.game_start_time = time.time() if self.players else None
                
                logging.info("Game reset with new puzzle")
                return True
        except Exception as e:
            logging.error(f"Error resetting game: {e}")
            return False