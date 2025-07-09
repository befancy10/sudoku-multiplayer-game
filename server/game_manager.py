import threading
import time
import logging
from sudoku_generator import SudokuGenerator

class GameManager:
    def __init__(self, max_players=4, debug_mode=True):
        self.max_players = max_players
        self.players = {}  # player_id: player_info
        self.current_puzzle = None
        self.solution = None
        self.game_state = "waiting"  # waiting, playing, finished
        self.game_start_time = None
        self.completed_players = []  # Track completion order
        
        # DEBUG MODE - NEW
        self.debug_mode = debug_mode
        
        # THREAD SAFETY - Remove complex locking that might hang
        self.lock = threading.RLock()  # Use RLock instead of Lock
        
        # Generate initial puzzle
        self.generate_new_puzzle()
        
        logging.info("Game Manager initialized")
    
    # Generate a new sudoku puzzle 
    def generate_new_puzzle(self):
        # Almost complete puzzle with only 1 empty cell (for debugging only)
        logging.info("DEBUG MODE: Generating 1-cell puzzle for testing")
        self.current_puzzle = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 0, 0, 0, 0]  # Only cell [8,8] is empty (should be 9)
        ]
            
        # Complete solution
        self.solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]  # Answer is 9
        ]
        
        logging.info("Mock puzzle loaded")
        return True
        
        # try:
        #     # TRY generator first, fallback to mock if it hangs
        #     generator = SudokuGenerator()
        #     self.current_puzzle, self.solution = generator.generate_puzzle()
        #     logging.info("New puzzle generated")
        #     return True
        # except Exception as e:
        #     logging.warning(f"Puzzle generation failed, using mock puzzle: {e}")
        #     # FALLBACK: Use mock puzzle
        #     self.current_puzzle = [
        #         [5, 3, 0, 0, 7, 0, 0, 0, 0],
        #         [6, 0, 0, 1, 9, 5, 0, 0, 0],
        #         [0, 9, 8, 0, 0, 0, 0, 6, 0],
        #         [8, 0, 0, 0, 6, 0, 0, 0, 3],
        #         [4, 0, 0, 8, 0, 3, 0, 0, 1],
        #         [7, 0, 0, 0, 2, 0, 0, 0, 6],
        #         [0, 6, 0, 0, 0, 0, 2, 8, 0],
        #         [0, 0, 0, 4, 1, 9, 0, 0, 5],
        #         [0, 0, 0, 0, 8, 0, 0, 7, 9]
        #     ]
            
        #     self.solution = [
        #         [5, 3, 4, 6, 7, 8, 9, 1, 2],
        #         [6, 7, 2, 1, 9, 5, 3, 4, 8],
        #         [1, 9, 8, 3, 4, 2, 5, 6, 7],
        #         [8, 5, 9, 7, 6, 1, 4, 2, 3],
        #         [4, 2, 6, 8, 5, 3, 7, 9, 1],
        #         [7, 1, 3, 9, 2, 4, 8, 5, 6],
        #         [9, 6, 1, 5, 3, 7, 2, 8, 4],
        #         [2, 8, 7, 4, 1, 9, 6, 3, 5],
        #         [3, 4, 5, 2, 8, 6, 1, 7, 9]
        #     ]
        #     logging.info("Mock puzzle loaded")
        #     return True
    
    # Add a new player to the game
    def add_player(self, player_id, player_name):
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
                
                # Create player info with individual completion tracking
                player_info = {
                    "player_id": player_id,
                    "name": player_name,
                    "score": 0,
                    "join_time": time.time(),
                    "moves": [],
                    "board": self.get_initial_board(),
                    "cell_status": self.get_initial_cell_status(),
                    "filled_cells": 0,
                    "correct_answers": 0,
                    "wrong_answers": 0,
                    # Individual completion tracking
                    "player_status": "playing",  # playing, completed, spectating
                    "completion_time": None,  # When player completed the puzzle
                    "completion_duration": None,  # How long it took to complete
                    "completion_rank": None  # Rank in completion order
                }
                
                # Add player
                self.players[player_id] = player_info
                
                # Start game if this is the first player - SIMPLIFIED
                if len(self.players) == 1 and self.game_state == "waiting":
                    self.game_state = "playing"
                    self.game_start_time = time.time()
                    logging.info("Game started!")
                    
                    if self.debug_mode:
                        print(f" DEBUG: Game started with {player_name}")
                        print("   Quick completion test: Click cell [8,8] and enter '9'")
            
            # Log outside of lock
            logging.info(f"Player {player_name} ({player_id}) joined. Total players: {len(self.players)}")
            return True, "Player added successfully"
            
        except Exception as e:
            logging.error(f"Error in add_player: {e}")
            return False, f"Error adding player: {str(e)}"
    
    # Calculate current ranking based on priority: score → completion time 
    def calculate_current_ranking(self):
        try:
            # Get all players and sort by ranking criteria
            all_players = list(self.players.values())
            
            # ranking priority order:
            # 1. Score (higher score first)
            # 2. Completion time (faster completion first) - only for completed players
            # 3. Completion status as secondary factor
            def ranking_key(player):
                score = player["score"]
                completion_time = player["completion_duration"] if player["completion_duration"] else float('inf')
                status = player["player_status"]
                
                # Primary sort: Score (higher first, so negate it)
                # Secondary sort: 
                #   - For completed players: completion time (faster first)
                #   - For playing players: inf (so they come after completed with same score)
                if status == "completed":
                    return (-score, completion_time)  # Higher score first, then faster time
                else:
                    return (-score, float('inf'))  # Higher score first, playing players after completed with same score
            
            # Sort players by ranking criteria
            sorted_players = sorted(all_players, key=ranking_key)
            
            # Create ranking list
            current_ranking = []
            for rank, player in enumerate(sorted_players, 1):
                ranking_info = {
                    "rank": rank,
                    "player_id": player["player_id"],
                    "name": player["name"],
                    "status": player["player_status"],
                    "score": player["score"],
                    "completion_time": player["completion_duration"],
                    "completion_rank": player["completion_rank"]  # Original completion order
                }
                current_ranking.append(ranking_info)
            
            return current_ranking
            
        except Exception as e:
            logging.error(f"Error calculating ranking: {e}")
            return []
    
    # Format ranking for announcement
    def format_ranking_announcement(self, current_ranking, announcement_type="temporary"):
        try:
            if not current_ranking:
                return "No players to rank"
            
            # Create ranking text
            ranking_lines = []
            
            for player_info in current_ranking:
                rank = player_info["rank"]
                name = player_info["name"]
                status = player_info["status"]
                score = player_info["score"]
                completion_time = player_info["completion_time"]
                
                if status == "completed":
                    # Format: "Rank 1: Alice (completed, 90 pts, 00:05)"
                    time_str = self.format_duration(completion_time) if completion_time else "00:00"
                    line = f"Rank {rank}: {name} (completed, {score} pts, {time_str})"
                else:
                    # Format: "Rank 2: Bob (playing, 85 pts)"
                    line = f"Rank {rank}: {name} (playing, {score} pts)"
                
                ranking_lines.append(line)
            
            # Join with newlines
            ranking_text = "\n".join(ranking_lines)
            
            if announcement_type == "final":
                return f"Final Ranking:\n{ranking_text}"
            else:
                return f"Current Ranking:\n{ranking_text}"
                
        except Exception as e:
            logging.error(f"Error formatting ranking: {e}")
            return "Error formatting ranking"
    
    # Format duration in seconds to MM:SS format
    def format_duration(self, duration_seconds):
        if duration_seconds is None:
            return "00:00"
        
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    # Announce temporary ranking when a player completes
    def announce_temporary_ranking(self, completed_player_name, rank):
        try:
            current_ranking = self.calculate_current_ranking()
            ranking_announcement = self.format_ranking_announcement(current_ranking, "temporary")
            
            # Log the announcement
            logging.info(f"{completed_player_name} completed the puzzle! Rank: #{rank}")
            logging.info(ranking_announcement)
            
            if self.debug_mode:
                print(f"DEBUG: {completed_player_name} COMPLETED!")
                print(f"TEMPORARY RANKING:")
                for line in ranking_announcement.split('\n')[1:]:  # Skip "Current Ranking:" header
                    print(f"   {line}")
            
            return ranking_announcement
            
        except Exception as e:
            logging.error(f"Error announcing temporary ranking: {e}")
            return ""
    
    # Announce final ranking when all players complete
    def announce_final_ranking(self):
        try:
            final_ranking = self.calculate_current_ranking()
            ranking_announcement = self.format_ranking_announcement(final_ranking, "final")
            
            # Log the final announcement
            logging.info("Game finished! All players completed.")
            logging.info(ranking_announcement)
            
            if self.debug_mode:
                print(f"DEBUG: GAME FINISHED! All players completed!")
                print(f"FINAL RANKING:")
                for line in ranking_announcement.split('\n')[1:]:  # Skip "Final Ranking:" header
                    print(f"   {line}")
            
            return ranking_announcement
            
        except Exception as e:
            logging.error(f"Error announcing final ranking: {e}")
            return ""
    
    # Initialize cell status matrix
    def get_initial_cell_status(self):
        # Status: 'given' (original puzzle), 'correct' (correct answer), 'incorrect' (wrong answer), 'empty'
        status = [['empty' for _ in range(9)] for _ in range(9)]
        
        # Mark given numbers as 'given'
        for i in range(9):
            for j in range(9):
                if self.current_puzzle[i][j] != 0:
                    status[i][j] = 'given'
        
        return status
    
    # Remove a player from the game
    def remove_player(self, player_id):
        try:
            with self.lock:
                if player_id in self.players:
                    player_name = self.players[player_id]["name"]
                    del self.players[player_id]
                    
                    # Remove from completed players if they were completed
                    self.completed_players = [p for p in self.completed_players if p["player_id"] != player_id]
                    
                    logging.info(f"Player {player_name} ({player_id}) removed. Remaining players: {len(self.players)}")
                    
                    # End game if no players left
                    if len(self.players) == 0:
                        self.game_state = "waiting"
                        self.completed_players = []
                    else:
                        # Check if all remaining players are completed
                        self.check_all_players_completion()
                    
                    return True
                return False
        except Exception as e:
            logging.error(f"Error removing player {player_id}: {e}")
            return False
    
    # Get a copy of the initial puzzle board
    def get_initial_board(self):
        if not self.current_puzzle:
            return None
        
        # Return a deep copy of the puzzle
        return [row[:] for row in self.current_puzzle]
    
    # Process a player's answer submission with ranking announcements
    def submit_answer(self, player_id, row, col, value):
        try:
            with self.lock:
                if player_id not in self.players:
                    return False, "Player not found", {}
                
                if self.game_state not in ["playing"]:
                    return False, "Game not in progress", {}
                
                player = self.players[player_id]
                
                # DEBUG LOGGING
                if self.debug_mode:
                    print(f"🐛 DEBUG: {player['name']} submitting [{row},{col}] = {value}")
                    print(f"   Current status: {player['player_status']}")
                    print(f"   Correct answer: {self.solution[row][col]}")
                
                # Check if player is already completed
                if player["player_status"] == "completed":
                    debug_msg = "You have already completed the puzzle. You can only spectate now."
                    if self.debug_mode:
                        print(f"🐛 DEBUG: Blocking completed player: {debug_msg}")
                    return False, debug_msg, {}
                
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
                        # Don't change filled_cells for clearing incorrect answers
                        # because incorrect answers were never counted as "filled"
                    elif old_status == 'correct':
                        # If clearing a correct answer, decrease filled_cells
                        player["board"][row][col] = 0
                        player["cell_status"][row][col] = 'empty'
                        player["filled_cells"] -= 1
                    elif old_status == 'empty':
                        # Already empty, no change
                        pass
                    
                    result = {
                        "correct": True,  # Clearing is always "successful"
                        "score_change": 0,
                        "new_score": player["score"],
                        "player_completed": False,
                        "game_complete": self.game_state == "finished",
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
                
                # DEBUG LOGGING
                if self.debug_mode:
                    print(f"🐛 DEBUG: Answer check: {value} == {self.solution[row][col]} ? {is_correct}")
                
                # Update player's board and status with proper filled_cells tracking
                old_status = player["cell_status"][row][col]
                player["board"][row][col] = value
                
                # Calculate score change
                score_change = 0
                if is_correct:
                    score_change = 10
                    player["correct_answers"] += 1
                    player["cell_status"][row][col] = 'correct'  # Lock this cell
                    
                    # Only increment filled_cells for CORRECT answers
                    if old_status != 'correct':  # Only if it wasn't already correct
                        player["filled_cells"] += 1
                else:
                    score_change = -10
                    player["wrong_answers"] += 1
                    player["cell_status"][row][col] = 'incorrect'  # Mark as incorrect but keep value
                    
                    # Progress should only reflect correct answers
                
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
                
                # Check if THIS PLAYER completed the puzzle
                player_completed = self.is_board_complete(player["board"])
                
                # DEBUG LOGGING
                if self.debug_mode:
                    print(f"🐛 DEBUG: Board complete check: {player_completed}")
                
                if player_completed and player["player_status"] == "playing":
                    # Mark player as completed
                    completion_time = time.time()
                    player["player_status"] = "completed"
                    player["completion_time"] = completion_time
                    player["completion_duration"] = completion_time - self.game_start_time
                    player["completion_rank"] = len(self.completed_players) + 1
                    
                    # Add to completed players list
                    self.completed_players.append({
                        "player_id": player_id,
                        "name": player["name"],
                        "completion_time": completion_time,
                        "completion_duration": player["completion_duration"],
                        "score": player["score"],
                        "rank": player["completion_rank"]
                    })
                    
                    # Announce temporary ranking
                    self.announce_temporary_ranking(player["name"], player["completion_rank"])
                    
                    # Check if ALL players have completed
                    all_completed = self.check_all_players_completion()
                    
                    # Announce final ranking if game finished
                    if all_completed:
                        self.announce_final_ranking()
                
                result = {
                    "correct": is_correct,
                    "score_change": score_change,
                    "new_score": player["score"],
                    "player_completed": player_completed,
                    "game_complete": self.game_state == "finished",
                    "cell_status": player["cell_status"],
                    "board": player["board"]
                }
                
                return True, "Answer processed", result
                
        except Exception as e:
            logging.error(f"Error in submit_answer: {e}")
            return False, f"Error processing answer: {str(e)}", {}
    
    # Check if all players have completed the puzzle - RETURNS BOOLEAN
    def check_all_players_completion(self):
        try:
            if not self.players:
                return False
            
            # Count completed players
            completed_count = sum(1 for player in self.players.values() if player["player_status"] == "completed")
            total_players = len(self.players)
            
            # DEBUG LOGGING
            if self.debug_mode:
                print(f" DEBUG: Completion check: {completed_count}/{total_players} completed")
            
            # Game is finished only when ALL players have completed
            if completed_count == total_players and total_players > 0:
                self.game_state = "finished"
                return True  # All completed
            
            return False  # Not all completed yet
                
        except Exception as e:
            logging.error(f"Error checking all players completion: {e}")
            return False
    
    # Get player's board with cell status information
    def get_player_board_with_status(self, player_id):
        try:
            with self.lock:
                if player_id not in self.players:
                    return None, None
                
                player = self.players[player_id]
                return player["board"], player["cell_status"]
        except Exception as e:
            logging.error(f"Error getting player board: {e}")
            return None, None
    
    # Check if a board is completely and correctly filled
    def is_board_complete(self, board):
        try:
            for i in range(9):
                for j in range(9):
                    if board[i][j] != self.solution[i][j]:
                        return False
            return True
        except:
            return False
    
    # Get all player scores with completion info
    def get_scores(self):
        try:
            with self.lock:
                scores = {}
                for player_id, player in self.players.items():
                    scores[player_id] = {
                        "name": player["name"],
                        "score": player["score"],
                        "correct_answers": player["correct_answers"],
                        "wrong_answers": player["wrong_answers"],
                        # Completion tracking
                        "player_status": player["player_status"],
                        "completion_time": player["completion_time"],
                        "completion_duration": player["completion_duration"],
                        "completion_rank": player["completion_rank"]
                    }
                return scores
        except Exception as e:
            logging.error(f"Error getting scores: {e}")
            return {}
    
    # Get progress information for all players
    def get_player_progress(self):
        try:
            with self.lock:
                progress = {}
                total_empty_cells = sum(1 for i in range(9) for j in range(9) if self.current_puzzle[i][j] == 0)
                
                for player_id, player in self.players.items():
                    progress[player_id] = {
                        "name": player["name"],
                        "filled_cells": player["filled_cells"],
                        "total_empty_cells": total_empty_cells,
                        "completion_percentage": (player["filled_cells"] / total_empty_cells * 100) if total_empty_cells > 0 else 0,
                        # Status info
                        "player_status": player["player_status"],
                        "completion_rank": player["completion_rank"]
                    }
                
                return progress
        except Exception as e:
            logging.error(f"Error getting progress: {e}")
            return {}
    
    # Get current ranking information for clients
    def get_current_ranking_info(self):
        try:
            current_ranking = self.calculate_current_ranking()
            ranking_text = self.format_ranking_announcement(current_ranking, "current")
            
            return {
                "ranking": current_ranking,
                "ranking_text": ranking_text
            }
        except Exception as e:
            logging.error(f"Error getting ranking info: {e}")
            return {"ranking": [], "ranking_text": ""}
    
    # Get current game state
    def get_game_state(self):
        try:
            with self.lock:
                completed_count = sum(1 for player in self.players.values() if player["player_status"] == "completed")
                
                state = {
                    "game_state": self.game_state,
                    "players_count": len(self.players),
                    "max_players": self.max_players,
                    "game_duration": time.time() - self.game_start_time if self.game_start_time else 0,
                    # Completion tracking
                    "completed_players": completed_count,
                    "remaining_players": len(self.players) - completed_count,
                    "completion_order": self.completed_players,
                    # Current ranking
                    "current_ranking": self.get_current_ranking_info()
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
                "game_duration": 0,
                "completed_players": 0,
                "remaining_players": 0,
                "current_ranking": {"ranking": [], "ranking_text": ""}
            }
    
    # Get the winner based on final ranking
    def get_winner(self):
        try:
            final_ranking = self.calculate_current_ranking()
            if final_ranking:
                winner_info = final_ranking[0]  # First in final ranking
                return {
                    "player_id": winner_info["player_id"],
                    "name": winner_info["name"],
                    "score": winner_info["score"],
                    "completion_time": winner_info["completion_time"],
                    "completion_rank": winner_info["completion_rank"],
                    "final_rank": 1
                }
            return None
        except:
            return None
    
    # Check if the game is complete
    def is_game_complete(self):
        return self.game_state == "finished"
    
    # Get the current puzzle
    def get_puzzle(self):
        return self.current_puzzle
    
    # Get the solution (for debugging/admin purposes)
    # def get_solution(self):
    #     return self.solution
    
    # Reset the game with a new puzzle
    def reset_game(self):
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
                    # Reset completion status
                    player["player_status"] = "playing"
                    player["completion_time"] = None
                    player["completion_duration"] = None
                    player["completion_rank"] = None
                
                # Reset game state
                self.game_state = "playing" if self.players else "waiting"
                self.game_start_time = time.time() if self.players else None
                self.completed_players = []
                
                logging.info("Game reset with new puzzle")
                return True
        except Exception as e:
            logging.error(f"Error resetting game: {e}")
            return False