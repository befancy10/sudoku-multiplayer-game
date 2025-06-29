import logging

class ProtocolHandler:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        
        # Command mapping
        self.commands = {
            "join_game": self.handle_join_game,
            "get_puzzle": self.handle_get_puzzle,
            "submit_answer": self.handle_submit_answer,
            "get_scores": self.handle_get_scores,
            "get_game_state": self.handle_get_game_state,
            "get_player_progress": self.handle_get_player_progress,
            "get_player_board": self.handle_get_player_board,  # NEW: Get board with status
            "leave_game": self.handle_leave_game,
            "reset_game": self.handle_reset_game,
            "get_solution": self.handle_get_solution  # Admin command
        }
    
    def handle_command(self, command_data):
        """Process incoming command and return response"""
        try:
            command = command_data.get("command")
            player_id = command_data.get("player_id")
            data = command_data.get("data", {})
            
            if not command:
                return self.error_response("Missing command")
            
            if command not in self.commands:
                return self.error_response(f"Unknown command: {command}")
            
            # Execute command
            return self.commands[command](player_id, data)
            
        except Exception as e:
            logging.error(f"Error handling command: {e}")
            return self.error_response("Internal server error")
    
    def success_response(self, message="Success", data=None):
        """Create success response"""
        response = {
            "status": "OK",
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    def error_response(self, message="Error", data=None):
        """Create error response"""
        response = {
            "status": "ERROR",
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    def handle_join_game(self, player_id, data):
        """Handle join game request"""
        try:
            if not player_id:
                return self.error_response("Missing player ID")
            
            player_name = data.get("player_name")
            if not player_name:
                return self.error_response("Missing player name")
            
            success, message = self.game_manager.add_player(player_id, player_name)
            
            if success:
                return self.success_response(message, {
                    "player_id": player_id,
                    "player_name": player_name,
                    "game_state": self.game_manager.get_game_state()
                })
            else:
                return self.error_response(message)
                
        except Exception as e:
            logging.error(f"Error in join_game: {e}")
            return self.error_response("Failed to join game")
    
    def handle_get_puzzle(self, player_id, data):
        """Handle get puzzle request"""
        try:
            if not player_id:
                return self.error_response("Missing player ID")
            
            puzzle = self.game_manager.get_puzzle()
            if puzzle is None:
                return self.error_response("No puzzle available")
            
            return self.success_response("Puzzle retrieved", {
                "puzzle": puzzle
            })
            
        except Exception as e:
            logging.error(f"Error in get_puzzle: {e}")
            return self.error_response("Failed to get puzzle")
    
    def handle_get_player_board(self, player_id, data):
        """Handle get player board with status - NEW COMMAND"""
        try:
            if not player_id:
                return self.error_response("Missing player ID")
            
            board, cell_status = self.game_manager.get_player_board_with_status(player_id)
            
            if board is None:
                return self.error_response("Player not found")
            
            return self.success_response("Player board retrieved", {
                "board": board,
                "cell_status": cell_status
            })
            
        except Exception as e:
            logging.error(f"Error in get_player_board: {e}")
            return self.error_response("Failed to get player board")
    
    def handle_submit_answer(self, player_id, data):
        """Handle submit answer request - UPDATED"""
        try:
            if not player_id:
                return self.error_response("Missing player ID")
            
            # Validate required data
            required_fields = ["row", "col", "value"]
            for field in required_fields:
                if field not in data:
                    return self.error_response(f"Missing field: {field}")
            
            row = data["row"]
            col = data["col"]
            value = data["value"]
            
            # Validate data types
            try:
                row = int(row)
                col = int(col)
                value = int(value)
            except (ValueError, TypeError):
                return self.error_response("Invalid data types")
            
            # Submit answer
            success, message, result = self.game_manager.submit_answer(
                player_id, row, col, value
            )
            
            if success:
                # Add updated board and status to response
                board, cell_status = self.game_manager.get_player_board_with_status(player_id)
                result["board"] = board
                result["cell_status"] = cell_status
                
                return self.success_response(message, result)
            else:
                return self.error_response(message, result)
                
        except Exception as e:
            logging.error(f"Error in submit_answer: {e}")
            return self.error_response("Failed to submit answer")
    
    def handle_get_scores(self, player_id, data):
        """Handle get scores request"""
        try:
            scores = self.game_manager.get_scores()
            return self.success_response("Scores retrieved", {
                "scores": scores
            })
            
        except Exception as e:
            logging.error(f"Error in get_scores: {e}")
            return self.error_response("Failed to get scores")
    
    def handle_get_game_state(self, player_id, data):
        """Handle get game state request"""
        try:
            game_state = self.game_manager.get_game_state()
            return self.success_response("Game state retrieved", game_state)
            
        except Exception as e:
            logging.error(f"Error in get_game_state: {e}")
            return self.error_response("Failed to get game state")
    
    def handle_get_player_progress(self, player_id, data):
        """Handle get player progress request"""
        try:
            progress = self.game_manager.get_player_progress()
            return self.success_response("Player progress retrieved", {
                "progress": progress
            })
            
        except Exception as e:
            logging.error(f"Error in get_player_progress: {e}")
            return self.error_response("Failed to get player progress")
    
    def handle_leave_game(self, player_id, data):
        """Handle leave game request"""
        try:
            if not player_id:
                return self.error_response("Missing player ID")
            
            success = self.game_manager.remove_player(player_id)
            
            if success:
                return self.success_response("Left game successfully")
            else:
                return self.error_response("Player not found")
                
        except Exception as e:
            logging.error(f"Error in leave_game: {e}")
            return self.error_response("Failed to leave game")
    
    def handle_reset_game(self, player_id, data):
        """Handle reset game request (admin command)"""
        try:
            # This could be restricted to admin users
            success = self.game_manager.reset_game()
            
            if success:
                return self.success_response("Game reset successfully", {
                    "new_puzzle": self.game_manager.get_puzzle()
                })
            else:
                return self.error_response("Failed to reset game")
                
        except Exception as e:
            logging.error(f"Error in reset_game: {e}")
            return self.error_response("Failed to reset game")
    
    def handle_get_solution(self, player_id, data):
        """Handle get solution request (admin/debug command)"""
        try:
            # This should be restricted in production
            solution = self.game_manager.get_solution()
            
            if solution:
                return self.success_response("Solution retrieved", {
                    "solution": solution
                })
            else:
                return self.error_response("No solution available")
                
        except Exception as e:
            logging.error(f"Error in get_solution: {e}")
            return self.error_response("Failed to get solution")
    
    def validate_player_exists(self, player_id):
        """Validate that player exists in the game"""
        return player_id in self.game_manager.players
    
    def get_command_list(self):
        """Get list of available commands"""
        return list(self.commands.keys())