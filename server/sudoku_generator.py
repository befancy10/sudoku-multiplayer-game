import random
import copy

class SudokuGenerator:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
    
    def generate_puzzle(self, difficulty="medium"):
        """Generate a sudoku puzzle with given difficulty"""
        # Generate a complete valid sudoku board
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fill_board()
        
        # Create solution copy
        solution = copy.deepcopy(self.board)
        
        # Remove numbers to create puzzle
        puzzle = self.create_puzzle(solution, difficulty)
        
        return puzzle, solution
    
    def fill_board(self):
        """Fill the board with a valid complete sudoku solution"""
        # Fill diagonal 3x3 boxes first (they don't affect each other)
        for box in range(0, 9, 3):
            self.fill_box(box, box)
        
        # Fill remaining cells
        self.solve_board(0, 3)
        
        return True
    
    def fill_box(self, row, col):
        """Fill a 3x3 box with random valid numbers"""
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for i in range(3):
            for j in range(3):
                self.board[row + i][col + j] = numbers[i * 3 + j]
    
    def solve_board(self, row, col):
        """Solve the board using backtracking"""
        # Move to next row if we've reached the end of current row
        if col == 9:
            row += 1
            col = 0
        
        # Board is complete
        if row == 9:
            return True
        
        # Skip if cell is already filled
        if self.board[row][col] != 0:
            return self.solve_board(row, col + 1)
        
        # Try numbers 1-9 in random order
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for num in numbers:
            if self.is_safe(row, col, num):
                self.board[row][col] = num
                
                if self.solve_board(row, col + 1):
                    return True
                
                # Backtrack
                self.board[row][col] = 0
        
        return False
    
    def is_safe(self, row, col, num):
        """Check if it's safe to place num at position (row, col)"""
        # Check row
        for j in range(9):
            if self.board[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if self.board[i][col] == num:
                return False
        
        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        
        for i in range(3):
            for j in range(3):
                if self.board[start_row + i][start_col + j] == num:
                    return False
        
        return True
    
    def create_puzzle(self, solution, difficulty="medium"):
        """Create puzzle by removing numbers from complete solution"""
        puzzle = copy.deepcopy(solution)
        
        # Define difficulty levels (number of cells to remove)
        difficulty_levels = {
            "easy": 35,      # Remove 35 numbers (46 given)
            "medium": 45,    # Remove 45 numbers (36 given)
            "hard": 55,      # Remove 55 numbers (26 given)
            "expert": 65     # Remove 65 numbers (16 given)
        }
        
        cells_to_remove = difficulty_levels.get(difficulty, 45)
        
        # Get all cell positions
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        removed = 0
        for row, col in positions:
            if removed >= cells_to_remove:
                break
            
            # Temporarily remove the number
            backup = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check if puzzle still has unique solution
            if self.has_unique_solution(copy.deepcopy(puzzle)):
                removed += 1
            else:
                # Restore the number if removing it makes puzzle invalid
                puzzle[row][col] = backup
        
        return puzzle
    
    def has_unique_solution(self, puzzle):
        """Check if puzzle has exactly one solution"""
        solutions = []
        self.count_solutions(puzzle, solutions, 0, 0)
        return len(solutions) == 1
    
    def count_solutions(self, puzzle, solutions, row, col):
        """Count number of solutions for the puzzle"""
        # Limit to 2 solutions for efficiency
        if len(solutions) >= 2:
            return
        
        # Move to next row
        if col == 9:
            row += 1
            col = 0
        
        # Found a solution
        if row == 9:
            solutions.append(copy.deepcopy(puzzle))
            return
        
        # Skip filled cells
        if puzzle[row][col] != 0:
            self.count_solutions(puzzle, solutions, row, col + 1)
            return
        
        # Try numbers 1-9
        for num in range(1, 10):
            if self.is_valid_move(puzzle, row, col, num):
                puzzle[row][col] = num
                self.count_solutions(puzzle, solutions, row, col + 1)
                puzzle[row][col] = 0
                
                # Early termination if multiple solutions found
                if len(solutions) >= 2:
                    return
    
    def is_valid_move(self, board, row, col, num):
        """Check if placing num at (row, col) is valid"""
        # Check row
        for j in range(9):
            if board[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if board[i][col] == num:
                return False
        
        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        
        return True
    
    def validate_solution(self, board):
        """Validate if a board is a valid complete sudoku solution"""
        # Check all rows
        for row in range(9):
            if not self.is_valid_unit([board[row][col] for col in range(9)]):
                return False
        
        # Check all columns
        for col in range(9):
            if not self.is_valid_unit([board[row][col] for row in range(9)]):
                return False
        
        # Check all 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(board[box_row + i][box_col + j])
                if not self.is_valid_unit(box):
                    return False
        
        return True
    
    def is_valid_unit(self, unit):
        """Check if a unit (row, column, or box) contains all numbers 1-9"""
        return sorted(unit) == list(range(1, 10))
    
    def print_board(self, board):
        """Print board in a readable format (for debugging)"""
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("------+-------+------")
            
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("| ", end="")
                
                if board[i][j] == 0:
                    print(". ", end="")
                else:
                    print(str(board[i][j]) + " ", end="")
            
            print()

# Example usage and testing
if __name__ == "__main__":
    generator = SudokuGenerator()
    puzzle, solution = generator.generate_puzzle("medium")
    
    print("Generated Puzzle:")
    generator.print_board(puzzle)
    print("\nSolution:")
    generator.print_board(solution)
    print(f"\nSolution is valid: {generator.validate_solution(solution)}")