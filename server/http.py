import sys
import os.path
import uuid
import json
import logging
from glob import glob
from datetime import datetime

# Import game components
from game_manager import GameManager

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'
        
        # Game integration
        self.game_manager = GameManager(max_players=4)
        
        logging.info("HTTP Server with Game Integration initialized")
    
    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")
        response_headers = ''
        for i in resp:
            response_headers = "{}{}".format(response_headers, i)
        
        # menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
        # response harus berupa bytes
        # message body harus diubah dulu menjadi bytes
        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode()
        response = response_headers.encode() + messagebody
        # response adalah bytes
        return response
    
    # Modifikasi untuk handle JSON commands
    def proses(self, data):
        # Try JSON command first (for game clients)
        if self.is_json_command(data):
            return self.process_game_command(data)
        
        # Original HTTP processing - PRESERVED
        requests = data.split("\r\n")
        
        # print(requests)
        baris = requests[0]
        
        # print(baris)
        all_headers = [n for n in requests[1:] if n != '']
        
        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            if (method == 'GET'):
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            if (method == 'POST'):
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})
    
    # Check if incoming data is JSON command
    def is_json_command(self, data):
        try:
            json.loads(data.strip())
            return True
        except (json.JSONDecodeError, ValueError):
            return False
    
    # Process game JSON commands
    def process_game_command(self, data):
        try:
            command_data = json.loads(data.strip())
            command = command_data.get("command")
            player_id = command_data.get("player_id")
            command_data_inner = command_data.get("data", {})
            
            logging.info(f"Processing game command: {command} from player: {player_id}")
            
            # Hardcoded command routing - TEMPLATE STYLE
            if not command:
                response = self.error_response("Missing command")
            elif command == "join_game":
                response = self.handle_join_game(player_id, command_data_inner)
            elif command == "get_puzzle":
                response = self.handle_get_puzzle(player_id, command_data_inner)
            elif command == "submit_answer":
                response = self.handle_submit_answer(player_id, command_data_inner)
            elif command == "get_scores":
                response = self.handle_get_scores(player_id, command_data_inner)
            elif command == "get_game_state":
                response = self.handle_get_game_state(player_id, command_data_inner)
            elif command == "get_player_progress":
                response = self.handle_get_player_progress(player_id, command_data_inner)
            elif command == "get_player_board":
                response = self.handle_get_player_board(player_id, command_data_inner)
            elif command == "leave_game":
                response = self.handle_leave_game(player_id, command_data_inner)
            elif command == "get_current_ranking":  # NEW COMMAND
                response = self.handle_get_current_ranking(player_id, command_data_inner)
            # elif command == "get_solution":
            #     response = self.handle_get_solution(player_id, command_data_inner)
            else:
                response = self.error_response(f"Unknown command: {command}")
            
            # Return JSON response as bytes
            json_response = json.dumps(response)
            return json_response.encode('utf-8')
            
        except Exception as e:
            logging.error(f"Game command processing error: {e}")
            error_response = {
                "status": "ERROR",
                "message": f"Server error: {str(e)}",
                "data": {}
            }
            return json.dumps(error_response).encode('utf-8')
    
    # Create success response
    def success_response(self, message="Success", data=None):
        response = {
            "status": "OK",
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    # Create error response
    def error_response(self, message="Error", data=None):
        response = {
            "status": "ERROR",
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    # Handle join game request
    def handle_join_game(self, player_id, data):
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
    
    # Handle get puzzle request
    def handle_get_puzzle(self, player_id, data):
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
    
    # Handle get player board with status
    def handle_get_player_board(self, player_id, data):
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
    
    # Handle submit answer request
    def handle_submit_answer(self, player_id, data):
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
    
    # Handle get scores request
    def handle_get_scores(self, player_id, data):
        try:
            scores = self.game_manager.get_scores()
            return self.success_response("Scores retrieved", {
                "scores": scores
            })
            
        except Exception as e:
            logging.error(f"Error in get_scores: {e}")
            return self.error_response("Failed to get scores")
    
    # Handle get game state request
    def handle_get_game_state(self, player_id, data):
        try:
            game_state = self.game_manager.get_game_state()
            return self.success_response("Game state retrieved", game_state)
            
        except Exception as e:
            logging.error(f"Error in get_game_state: {e}")
            return self.error_response("Failed to get game state")
    
    # Handle get player progress request
    def handle_get_player_progress(self, player_id, data):
        try:
            progress = self.game_manager.get_player_progress()
            return self.success_response("Player progress retrieved", {
                "progress": progress
            })
            
        except Exception as e:
            logging.error(f"Error in get_player_progress: {e}")
            return self.error_response("Failed to get player progress")
    
    # Handle get current ranking request
    def handle_get_current_ranking(self, player_id, data):
        try:
            ranking_info = self.game_manager.get_current_ranking_info()
            return self.success_response("Current ranking retrieved", ranking_info)
            
        except Exception as e:
            logging.error(f"Error in get_current_ranking: {e}")
            return self.error_response("Failed to get current ranking")
    
    # Handle leave game request
    def handle_leave_game(self, player_id, data):
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
    
    # def handle_get_solution(self, player_id, data):
    #     """Handle get solution request (admin/debug command)"""
    #     try:
    #         # This should be restricted in production
    #         solution = self.game_manager.get_solution()
            
    #         if solution:
    #             return self.success_response("Solution retrieved", {
    #                 "solution": solution
    #             })
    #         else:
    #             return self.error_response("No solution available")
                
    #     except Exception as e:
    #         logging.error(f"Error in get_solution: {e}")
    #         return self.error_response("Failed to get solution")
    
    # Original template metho
    def http_get(self, object_address, headers):
        files = glob('./*')
        # print(files)
        thedir = './'
        if (object_address == '/'):
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan dengan Sudoku Game', dict())
        if (object_address == '/video'):
            return self.response(302, 'Found', '', dict(location='https://youtu.be/katoxpnTf04'))
        if (object_address == '/santai'):
            return self.response(200, 'OK', 'santai saja', dict())
        
        # Game status endpoint - NEW
        if (object_address == '/game'):
            return self.get_game_status()
        
        object_address = object_address[1:]
        if thedir + object_address not in files:
            return self.response(404, 'Not Found', '', {})
        fp = open(thedir + object_address, 'rb')  # rb => artinya adalah read dalam bentuk binary
        # harus membaca dalam bentuk byte dan BINARY
        isi = fp.read()
        
        fext = os.path.splitext(thedir + object_address)[1]
        content_type = self.types.get(fext, 'application/octet-stream')
        
        headers = {}
        headers['Content-type'] = content_type
        
        return self.response(200, 'OK', isi, headers)
    
    # Original template method
    def http_post(self, object_address, headers):
        headers = {}
        isi = "kosong"
        return self.response(200, 'OK', isi, headers)
    
    # Get simple game status 
    def get_game_status(self):
        try:
            game_state = self.game_manager.get_game_state()
            scores = self.game_manager.get_scores()
            
            status_text = f"""Sudoku Multiplayer Game Status
State: {game_state.get('game_state', 'Unknown')}
Players: {game_state.get('players_count', 0)}/{game_state.get('max_players', 4)}
Duration: {game_state.get('game_duration', 0):.1f}s

Current Scores:
"""
            if not scores:
                status_text += "No players yet"
            else:
                for player_id, info in scores.items():
                    status_text += f"{info['name']}: {info['score']} points\n"
            
            return self.response(200, 'OK', status_text, {'Content-type': 'text/plain'})
            
        except Exception as e:
            logging.error(f"Error getting game status: {e}")
            return self.response(500, 'Internal Server Error', f'Error: {str(e)}', {})


# >>> import os.path
# >>> ext = os.path.splitext('/ak/52.png')
if __name__ == "__main__":
    httpserver = HttpServer()
    d = httpserver.proses('GET testing.txt HTTP/1.0')
    print(d)
    d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
    print(d)
    # d = httpserver.http_get('testing2.txt',{})
    # print(d)
    # d = httpserver.http_get('testing.txt')
    # print(d)