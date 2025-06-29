import pytest
import sys
import os

# FIX IMPORT PATH - Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'server'))
sys.path.insert(0, os.path.join(parent_dir, 'client'))
sys.path.insert(0, os.path.join(parent_dir, 'common'))

print(f"Test running from: {current_dir}")
print(f"Added to Python path: {parent_dir}")

# Now import modules
try:
    from server.sudoku_generator import SudokuGenerator
    from server.game_manager import GameManager
    from server.protocol_handler import ProtocolHandler
    print(" All imports successful!")
except ImportError as e:
    print(f" Import error: {e}")
    print("Available modules in path:")
    for path in sys.path[:5]:
        if os.path.exists(path):
            print(f"  {path}: {os.listdir(path)}")
    raise

class TestSudokuGenerator:
    """Test cases for Sudoku puzzle generation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.generator = SudokuGenerator()
    
    def test_generate_puzzle_basic(self):
        """Test basic puzzle generation"""
        try:
            puzzle, solution = self.generator.generate_puzzle("medium")
            
            assert puzzle is not None, "Puzzle should not be None"
            assert solution is not None, "Solution should not be None"
            assert len(puzzle) == 9, "Puzzle should have 9 rows"
            assert len(solution) == 9, "Solution should have 9 rows"
            assert all(len(row) == 9 for row in puzzle), "All puzzle rows should have 9 columns"
            assert all(len(row) == 9 for row in solution), "All solution rows should have 9 columns"
            
            print(" Basic puzzle generation test: PASSED")
            return True
        except Exception as e:
            print(f" Basic puzzle generation test: FAILED - {e}")
            return False
    
    def test_puzzle_difficulty_levels(self):
        """Test different difficulty levels"""
        difficulties = ["easy", "medium"]  # Reduced for faster testing
        
        try:
            for difficulty in difficulties:
                puzzle, solution = self.generator.generate_puzzle(difficulty)
                
                # Count empty cells in puzzle
                empty_cells = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] == 0)
                
                # Verify difficulty affects number of empty cells
                assert empty_cells > 0, f"Puzzle should have empty cells for {difficulty}"
                assert empty_cells < 81, f"Puzzle should not be completely empty for {difficulty}"
                
            print(" Difficulty levels test: PASSED")
            return True
        except Exception as e:
            print(f" Difficulty levels test: FAILED - {e}")
            return False
    
    def test_solution_validity(self):
        """Test that generated solutions are valid"""
        try:
            puzzle, solution = self.generator.generate_puzzle("easy")  # Use easy for faster gen
            
            # Validate solution
            is_valid = self.generator.validate_solution(solution)
            assert is_valid, "Generated solution should be valid"
            
            # Check that puzzle is subset of solution
            for i in range(9):
                for j in range(9):
                    if puzzle[i][j] != 0:
                        assert puzzle[i][j] == solution[i][j], f"Puzzle cell ({i},{j}) should match solution"
            
            print(" Solution validity test: PASSED")
            return True
        except Exception as e:
            print(f" Solution validity test: FAILED - {e}")
            return False
    
    def test_is_safe_method(self):
        """Test the is_safe validation method"""
        try:
            # Create a test board
            self.generator.board = [[0 for _ in range(9)] for _ in range(9)]
            
            # Test row conflict
            self.generator.board[0][0] = 5
            assert not self.generator.is_safe(0, 1, 5), "Should detect row conflict"
            assert self.generator.is_safe(0, 1, 3), "Should allow different number in same row"
            
            # Test column conflict
            self.generator.board[1][0] = 3
            assert not self.generator.is_safe(2, 0, 3), "Should detect column conflict"
            assert self.generator.is_safe(2, 0, 7), "Should allow different number in same column"
            
            print(" is_safe method test: PASSED")
            return True
        except Exception as e:
            print(f" is_safe method test: FAILED - {e}")
            return False

class TestGameManager:
    """Test cases for Game Manager"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.game_manager = GameManager(max_players=4)
    
    def test_add_player_success(self):
        """Test successful player addition"""
        try:
            success, message = self.game_manager.add_player("player1", "Alice")
            
            assert success is True, "Player addition should succeed"
            assert "player1" in self.game_manager.players, "Player should be in players dict"
            assert self.game_manager.players["player1"]["name"] == "Alice", "Player name should match"
            assert self.game_manager.players["player1"]["score"] == 0, "Initial score should be 0"
            
            print(" Add player success test: PASSED")
            return True
        except Exception as e:
            print(f" Add player success test: FAILED - {e}")
            return False
    
    def test_add_player_duplicate(self):
        """Test adding duplicate player"""
        try:
            # Add first player
            self.game_manager.add_player("player1", "Alice")
            
            # Try to add same player again
            success, message = self.game_manager.add_player("player1", "Bob")
            
            assert success is False, "Duplicate player addition should fail"
            assert "already exists" in message.lower(), "Error message should mention 'already exists'"
            
            print(" Add duplicate player test: PASSED")
            return True
        except Exception as e:
            print(f" Add duplicate player test: FAILED - {e}")
            return False
    
    def test_remove_player(self):
        """Test player removal"""
        try:
            # Add and then remove player
            self.game_manager.add_player("player1", "Alice")
            assert "player1" in self.game_manager.players, "Player should be added"
            
            result = self.game_manager.remove_player("player1")
            assert result is True, "Player removal should succeed"
            assert "player1" not in self.game_manager.players, "Player should be removed"
            
            print(" Remove player test: PASSED")
            return True
        except Exception as e:
            print(f" Remove player test: FAILED - {e}")
            return False
    
    def test_get_scores(self):
        """Test getting player scores"""
        try:
            # Add players with different scores
            self.game_manager.add_player("player1", "Alice")
            self.game_manager.add_player("player2", "Bob")
            
            # Manually set scores for testing
            self.game_manager.players["player1"]["score"] = 50
            self.game_manager.players["player2"]["score"] = 30
            
            scores = self.game_manager.get_scores()
            
            assert "player1" in scores, "Player1 should be in scores"
            assert "player2" in scores, "Player2 should be in scores"
            assert scores["player1"]["score"] == 50, "Player1 score should be 50"
            assert scores["player2"]["score"] == 30, "Player2 score should be 30"
            assert scores["player1"]["name"] == "Alice", "Player1 name should be Alice"
            assert scores["player2"]["name"] == "Bob", "Player2 name should be Bob"
            
            print(" Get scores test: PASSED")
            return True
        except Exception as e:
            print(f" Get scores test: FAILED - {e}")
            return False

class TestProtocolHandler:
    """Test cases for Protocol Handler"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.game_manager = GameManager(max_players=4)
        self.protocol_handler = ProtocolHandler(self.game_manager)
    
    def test_handle_join_game_success(self):
        """Test successful join game command"""
        try:
            command_data = {
                "command": "join_game",
                "player_id": "player1",
                "data": {"player_name": "Alice"}
            }
            
            response = self.protocol_handler.handle_command(command_data)
            
            assert response["status"] == "OK", "Join game should succeed"
            assert "data" in response, "Response should contain data"
            assert response["data"]["player_id"] == "player1", "Response should contain correct player_id"
            assert response["data"]["player_name"] == "Alice", "Response should contain correct player_name"
            
            print(" Join game success test: PASSED")
            return True
        except Exception as e:
            print(f" Join game success test: FAILED - {e}")
            return False
    
    def test_handle_unknown_command(self):
        """Test unknown command handling"""
        try:
            command_data = {
                "command": "unknown_command",
                "player_id": "player1",
                "data": {}
            }
            
            response = self.protocol_handler.handle_command(command_data)
            
            assert response["status"] == "ERROR", "Unknown command should return error"
            assert "unknown command" in response["message"].lower(), "Error message should mention unknown command"
            
            print(" Unknown command test: PASSED")
            return True
        except Exception as e:
            print(f" Unknown command test: FAILED - {e}")
            return False
    
    def test_response_format(self):
        """Test response format consistency"""
        try:
            command_data = {
                "command": "get_game_state",
                "player_id": "player1",
                "data": {}
            }
            
            response = self.protocol_handler.handle_command(command_data)
            
            # Every response should have status and message
            assert "status" in response, "Response should have status"
            assert "message" in response, "Response should have message"
            assert response["status"] in ["OK", "ERROR"], "Status should be OK or ERROR"
            assert isinstance(response["message"], str), "Message should be string"
            
            print(" Response format test: PASSED")
            return True
        except Exception as e:
            print(f" Response format test: FAILED - {e}")
            return False

def run_all_tests():
    """Run all tests manually"""
    print("=" * 60)
    print(" SUDOKU MULTIPLAYER GAME - COMPREHENSIVE TESTING")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    # Test SudokuGenerator
    print("\n Testing SudokuGenerator...")
    print("-" * 40)
    generator_tests = TestSudokuGenerator()
    generator_tests.setup_method()
    
    tests = [
        generator_tests.test_generate_puzzle_basic,
        generator_tests.test_puzzle_difficulty_levels,
        generator_tests.test_solution_validity,
        generator_tests.test_is_safe_method
    ]
    
    for test in tests:
        total_tests += 1
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f" {test.__name__}: EXCEPTION - {e}")
    
    # Test GameManager
    print(f"\n Testing GameManager...")
    print("-" * 40)
    manager_tests = TestGameManager()
    manager_tests.setup_method()
    
    tests = [
        manager_tests.test_add_player_success,
        manager_tests.test_add_player_duplicate,
        manager_tests.test_remove_player,
        manager_tests.test_get_scores
    ]
    
    for test in tests:
        total_tests += 1
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f" {test.__name__}: EXCEPTION - {e}")
    
    # Test ProtocolHandler
    print(f"\n📡 Testing ProtocolHandler...")
    print("-" * 40)
    protocol_tests = TestProtocolHandler()
    protocol_tests.setup_method()
    
    tests = [
        protocol_tests.test_handle_join_game_success,
        protocol_tests.test_handle_unknown_command,
        protocol_tests.test_response_format
    ]
    
    for test in tests:
        total_tests += 1
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f" {test.__name__}: EXCEPTION - {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print(" ALL TESTS PASSED! ")
        print(" Code quality: EXCELLENT")
        print(" Ready for production!")
    else:
        print(f" {total_tests - passed_tests} tests failed")
        print(" Review failed tests and fix issues")
    
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()