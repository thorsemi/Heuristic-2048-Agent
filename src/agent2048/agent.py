#from agent import Agent2048
import copy 
import random
class HeuristicAgent():
    """Agent that uses heuristics to evaluate board states"""
    
    def __init__(self, grid_size=4):
        self.grid_size = grid_size
        self.moves = ["up", "down", "left", "right"]
    
    def print_board_state(self, grid):
        """Print the current board state in a readable format"""
        print("Current Board State:")
        print(f"DEBUG: self.grid_size = {self.grid_size} (Type: {type(self.grid_size)})")
        print("-" * (self.grid_size * 6))
        for row in grid:
            row_str = "|"
            for cell in row:
                # Format each cell to have width 5
                row_str += f" {cell:4d} |"
            print(row_str)
            print("-" * (self.grid_size * 6))
        
        # Print some basic statistics about the board
        flat_grid = [cell for row in grid for cell in row]
        print(f"Highest tile: {max(flat_grid)}")
        print(f"Empty cells: {flat_grid.count(0)}")

    def get_valid_moves(self, grid):
        """Return a list of valid moves for the current grid"""
        valid_moves = []
        for move in self.moves:
            if self.move_is_valid(grid, move):
                valid_moves.append(move)
        return valid_moves
    
    def get_empty_cells(self, grid):
        """Return a list of empty cell positions as (x, y) tuples"""
        empty_cells = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if grid[y][x] == 0:
                    empty_cells.append((x, y))
        return empty_cells
    
    def move_is_valid(self, grid, move):
        """Check if a move is valid (changes the board state)"""
        # Create a copy of the grid to test the move
        test_grid = copy.deepcopy(grid)
        
        # Apply the move to the test grid
        if move == "left":
            new_grid = self.move_left(test_grid)
        elif move == "right":
            new_grid = self.move_right(test_grid)
        elif move == "up":
            new_grid = self.move_up(test_grid)
        elif move == "down":
            new_grid = self.move_down(test_grid)
        else:
            return False
        
        # Check if the grid changed
        return new_grid != grid
    def evaluate_grid(self, grid):
        """
        Evaluate a board state based on multiple heuristics
        Returns a score where higher is better
        """
        # 1. Number of empty cells (more is better)
        empty_count = sum(row.count(0) for row in grid)
        
        # 2. Total score on the board
        score = sum(sum(row) for row in grid)
        
        # 3. Monotonicity - prefer boards where values increase/decrease monotonically
        monotonicity_score = self._calculate_monotonicity(grid)
        
        # 4. Smoothness - prefer boards where adjacent tiles have similar values
        smoothness = self._calculate_smoothness(grid)
        
        # 5. Highest tile in corner bonus
        corner_bonus = self._highest_tile_in_preferred_corner(grid)
        
        closeness =self._highest_tiles_closeness(grid)
        merge = self._merge_opportunities(grid)
        
        # Weighting for the heuristics
        weights = {
            'empty': 17.9,
            'score':14.8,
            'monotonicity': 7.9,
            'smoothness': 4.9,
            'corner': 16.9,
            'closeness':17.3,
            'merge':14.8
        }

        # Calculate final score
        final_score = (
            weights['empty'] * empty_count +
            weights['score'] * score +
            weights['monotonicity'] * monotonicity_score +
            weights['smoothness'] * smoothness +
            weights['corner'] * corner_bonus +
            weights['closeness'] * closeness +
            weights['merge'] * merge
            
            
)

        
        return final_score
    
    def _calculate_monotonicity(self, grid):
        """Calculate how monotonic the grid is (values increasing or decreasing)"""
        monotonicity_score = 0
        
        # Check rows
        for row in grid:
            # Check left to right
            increasing = decreasing = 0
            for i in range(1, len(row)):
                if row[i-1] <= row[i]:
                    # Non-decreasing
                    increasing += 1
                if row[i-1] >= row[i]:
                    # Non-increasing
                    decreasing += 1
            
            monotonicity_score += max(increasing, decreasing)
        
        # Check columns
        for col in range(self.grid_size):
            # Create column array
            column = [grid[row][col] for row in range(self.grid_size)]
            
            # Check top to bottom
            increasing = decreasing = 0
            for i in range(1, len(column)):
                if column[i-1] <= column[i]:
                    # Non-decreasing
                    increasing += 1
                if column[i-1] >= column[i]:
                    # Non-increasing
                    decreasing += 1
            
            monotonicity_score += max(increasing, decreasing)
        
        return monotonicity_score
    
    def _calculate_smoothness(self, grid):
        """Calculate how smooth the grid is (adjacent tiles having similar values)"""
        smoothness = 0
        
        # Calculate the sum of differences between adjacent tiles
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if grid[row][col] != 0:
                    # Check right neighbor
                    if col < self.grid_size - 1 and grid[row][col+1] != 0:
                        smoothness -= abs(grid[row][col] - grid[row][col+1])
                    
                    # Check below neighbor
                    if row < self.grid_size - 1 and grid[row+1][col] != 0:
                        smoothness -= abs(grid[row][col] - grid[row+1][col])
        
        return smoothness
    
    def _highest_tile_in_corner(self, grid):
        """Check if the highest tile is in a corner"""
        flat_grid = [cell for row in grid for cell in row]
        max_value = max(flat_grid)
        
        # Check corners
        corners = [
            grid[0][0], grid[0][self.grid_size-1],
            grid[self.grid_size-1][0], grid[self.grid_size-1][self.grid_size-1]
        ]
        
        return 1 if max_value in corners else 0
    
    def _highest_tiles_closeness(self, grid):
        """Encourage the highest tiles to stay close together"""
        flat_grid = [(value, x, y) for y, row in enumerate(grid) for x, value in enumerate(row) if value != 0]
        
        if len(flat_grid) < 2:
            return 0  # Not enough tiles to evaluate closeness
        
        # Sort tiles by value (descending)
        flat_grid.sort(reverse=True, key=lambda x: x[0])
        
        top_tiles = flat_grid[:3]  # Get top 3 highest tiles
        
        closeness_score = 0
        for i in range(len(top_tiles)):
            for j in range(i + 1, len(top_tiles)):
                _, x1, y1 = top_tiles[i]
                _, x2, y2 = top_tiles[j]
                
                # If tiles are adjacent, increase score
                if abs(x1 - x2) + abs(y1 - y2) == 1:
                    closeness_score += 1
        
        return closeness_score
    
    def _highest_tile_in_preferred_corner(self, grid, preferred_corner=(3, 3)):
        """Encourage the highest tiles to stay in one preferred corner (default: bottom-right)"""
        
        # Unpack the preferred corner position
        corner_x, corner_y = preferred_corner
    
        # Find the maximum tile value
        max_tile = max(max(row) for row in grid)
        
        # Calculate score based on how many large values are near the corner
        closeness_score = 0
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if grid[y][x] > 0:
                    # Distance from preferred corner (Manhattan distance)
                    distance = abs(x - corner_x) + abs(y - corner_y)
                    
                    # Reward higher values being closer to the chosen corner
                    closeness_score += (grid[y][x] / (distance + 1))  # +1 to avoid division by zero
        
        # Bonus if the max tile is exactly in the preferred corner
        if grid[corner_y][corner_x] == max_tile:
            closeness_score *= 1.5  # Boost score if max tile is in the right spot
    
        return closeness_score

    def _merge_opportunities(self, grid):
         """Encourage merging of adjacent equal tiles"""
         merge_score = 0
         
         for y in range(self.grid_size):
             for x in range(self.grid_size):
                 if grid[y][x] > 0:
                     # Check right neighbor
                     if x < self.grid_size - 1 and grid[y][x] == grid[y][x + 1]:
                         merge_score += grid[y][x]  # Reward merging bigger numbers more
                     
                     # Check below neighbor
                     if y < self.grid_size - 1 and grid[y][x] == grid[y + 1][x]:
                         merge_score += grid[y][x]
         
         return merge_score
     
    def make_decision(self, grid):
        """"Make a simple decision - always move right if possible, otherwise random"""
        valid_moves = self.get_valid_moves(grid)

        if not valid_moves:
            return None  #no valid movements

        best_move = None
        best_score = float('-inf')

        for move in valid_moves:
            test_grid = copy.deepcopy(grid)  # Clone board to test movement

            if move == "left":
                new_grid = self.move_left(test_grid)
            elif move == "right":
                new_grid = self.move_right(test_grid)
            elif move == "up":
                new_grid = self.move_up(test_grid)
            elif move == "down":
                new_grid = self.move_down(test_grid)

            score = self.evaluate_grid(new_grid)  # Evaluate the board after the move
            print(f"Movement: {move}, Score Evaluated: {score}")
            score = self.expectimax(new_grid, depth=3, player_turn=False)  # Call Expectimax with depth 3
            print(f"Movement: {move}, Score expected: {score}")

            if score > best_score:
                best_score = score
                best_move = move

        return best_move
    
    # Move functions
    def move_left(self, grid):
        """Move all tiles to the left and merge tiles with the same value"""
        new_grid = [row[:] for row in grid]
        
        for y in range(self.grid_size):
            row = [tile for tile in new_grid[y] if tile != 0]
            
            merged_row = []
            i = 0
            while i < len(row):
                if i < len(row) - 1 and row[i] == row[i+1]:
                    merged_row.append(row[i] * 2)
                    i += 2
                else:
                    merged_row.append(row[i])
                    i += 1
            
            merged_row = merged_row + [0] * (self.grid_size - len(merged_row))
            new_grid[y] = merged_row
        
        return new_grid
    
    def move_right(self, grid):
        """Move all tiles to the right and merge tiles with the same value"""
        new_grid = [row[:] for row in grid]
        
        for y in range(self.grid_size):
            row = [tile for tile in new_grid[y] if tile != 0]
            
            merged_row = []
            i = len(row) - 1
            while i >= 0:
                if i > 0 and row[i] == row[i-1]:
                    merged_row.insert(0, row[i] * 2)
                    i -= 2
                else:
                    merged_row.insert(0, row[i])
                    i -= 1
            
            merged_row = [0] * (self.grid_size - len(merged_row)) + merged_row
            new_grid[y] = merged_row
        
        return new_grid
    
    def move_up(self, grid):
        """Move all tiles up and merge tiles with the same value"""
        transposed = list(map(list, zip(*grid)))
        moved = self.move_left(transposed)
        return list(map(list, zip(*moved)))
    
    def move_down(self, grid):
        """Move all tiles down and merge tiles with the same value"""
        transposed = list(map(list, zip(*grid)))
        moved = self.move_right(transposed)
        return list(map(list, zip(*moved)))
    
    def expectimax(self, grid, depth, player_turn):
        """Implements Expectimax Algorithm """
        if depth == 0 or not self.get_valid_moves(grid):
            return self.evaluate_grid(
                grid)  # Evaluate the board if it reaches the depth limit or there are no more moves

        if player_turn:  # MAX - IA's turn
            best_score = float('-inf')
            for move in self.get_valid_moves(grid):
                test_grid = copy.deepcopy(grid)

                if move == "left":
                    new_grid = self.move_left(test_grid)
                elif move == "right":
                    new_grid = self.move_right(test_grid)
                elif move == "up":
                    new_grid = self.move_up(test_grid)
                elif move == "down":
                    new_grid = self.move_down(test_grid)

                score = self.expectimax(new_grid, depth - 1, False)  # game's turn
                best_score = max(best_score, score)

            return best_score  # Devuelve la mejor puntuación posible para la IA

        else:  # "Games" turn's  (new tile placed)
            empty_cells = self.get_empty_cells(grid)
            if not empty_cells:
                return self.evaluate_grid(grid)  # If there are no empty spaces, evaluate directly

            total_score = 0
            for cell in empty_cells:
                for value in [2, 4]:  # new tiles might be  2 o 4
                    test_grid = copy.deepcopy(grid)
                    test_grid[cell[1]][cell[0]] = value  #place new tile

                    probability = 0.9 if value == 2 else 0.1  # 90% chances being a  2, 10% - 4
                    total_score += probability * self.expectimax(test_grid, depth - 1, True)  #  back IA turn

            return total_score / len(empty_cells)  # Averaging the scores