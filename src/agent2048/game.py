# Import necessary libraries
import pygame  # For game graphics and input handling
import random  # For generating random tile positions and values
#from agent import Agent2048  # Commented out alternative agent implementation
from agent import HeuristicAgent  # Import the AI agent with minimax algorithm
#from agen_Weights_MiniMax import HeuristicAgent  # Commented out alternative agent implementation

# Initialize Pygame
pygame.init()

# -------------------------------------------------------------------------
# GAME CONSTANTS AND CONFIGURATION
# -------------------------------------------------------------------------

# Define display dimensions and grid parameters
width, height = 800, 800  # Window size in pixels
grid_size = 4  # 4x4 grid for standard 2048 game
background_color = (255, 255, 255)  # White background
grid_color = (187, 173, 160)  # Grayish color for grid background

# Dictionary mapping tile values to their colors (RGB format)
# Colors are based on the original 2048 game design
TILE_COLORS = {
    0: (205, 193, 180),     # Empty tile - light gray
    2: (238, 228, 218),     # 2 tile - off-white
    4: (237, 224, 200),     # 4 tile - light beige
    8: (242, 177, 121),     # 8 tile - light orange
    16: (245, 149, 99),     # 16 tile - orange
    32: (246, 124, 95),     # 32 tile - darker orange
    64: (246, 94, 59),      # 64 tile - red
    128: (237, 207, 114),   # 128 tile - light yellow
    256: (237, 204, 97),    # 256 tile - yellow
    512: (237, 200, 80),    # 512 tile - darker yellow
    1024: (237, 197, 63),   # 1024 tile - gold
    2048: (237, 194, 46)    # 2048 tile - bright gold
}

# Calculate tile size based on window dimensions and grid size
tile_size = width // grid_size  # Each tile's width/height in pixels
tile_padding = 8  # Padding between tiles for visual separation

# Set up the game window
window = pygame.display.set_mode((width, height))  # Create display surface
pygame.display.set_caption("2048")  # Set window title

# -------------------------------------------------------------------------
# HELPER FUNCTIONS FOR DRAWING AND UI
# -------------------------------------------------------------------------

def get_font(size):
    """
    Returns a font object with the specified size.
    
    :param size: Font size in points
    :return: Pygame Font object
    """
    return pygame.font.Font(None, size)  # Use default pygame font with specified size

def create_grid():
    """
    Creates an empty 4x4 grid filled with zeros.
    
    :return: 2D list representing the empty game board
    """
    return [[0 for _ in range(grid_size)] for _ in range(grid_size)]

def draw_tile(x, y, value):
    """
    Draws a single tile on the game board.
    
    :param x: Column index (0-3)
    :param y: Row index (0-3)
    :param value: Tile value (0, 2, 4, 8, etc.)
    """
    # Calculate tile position with padding applied
    tile_x = x * tile_size + tile_padding  # X position with padding
    tile_y = y * tile_size + tile_padding  # Y position with padding
    tile_rect_size = tile_size - (2 * tile_padding)  # Size of tile after padding
    
    # Create rectangle for the tile with rounded corners
    tile_rect = pygame.Rect(tile_x, tile_y, tile_rect_size, tile_rect_size)
    pygame.draw.rect(window, TILE_COLORS[value], tile_rect, border_radius=5)
    
    # Draw the number on the tile (if not empty)
    if value != 0:
        font = get_font(50)  # Size for the number text
        text_surface = font.render(str(value), True, (0, 0, 0))  # Render with black color
        text_rect = text_surface.get_rect(center=tile_rect.center)  # Center text in tile
        window.blit(text_surface, text_rect)  # Draw text on screen

def draw_grid(grid):
    """
    Draws the entire game grid with all tiles.
    
    :param grid: 2D list representing the current game state
    """
    # Iterate through each cell in the grid
    for y in range(grid_size):
        for x in range(grid_size):
            # Draw each individual tile
            draw_tile(x, y, grid[y][x])

def draw_game_over(score):
    """
    Displays the game over screen with final score and restart instructions.
    
    :param score: Final score of the game
    """
    # Create semi-transparent overlay for the game over screen
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)  # Surface with alpha channel
    overlay.fill((255, 255, 255, 128))  # Semi-transparent white
    window.blit(overlay, (0, 0))  # Draw overlay on game window
    
    # Draw "GAME OVER" text
    game_over_font = get_font(100)  # Large font for game over text
    game_over_text = game_over_font.render("GAME OVER!", True, (0, 0, 0))  # Black text
    game_over_rect = game_over_text.get_rect(center=(width//2, height//2 - 100))  # Position text
    window.blit(game_over_text, game_over_rect)  # Draw text
    
    # Display final score
    score_font = get_font(70)  # Medium font for score text
    score_text = score_font.render(f"YOUR SCORE: {score}", True, (0, 0, 0))  # Black text
    score_rect = score_text.get_rect(center=(width//2, height//2 + 50))  # Position below game over
    window.blit(score_text, score_rect)  # Draw text
    
    # Show restart instructions
    restart_font = get_font(50)  # Smaller font for instructions
    restart_text = restart_font.render("Press SPACE to restart", True, (0, 0, 0))  # Black text
    restart_rect = restart_text.get_rect(center=(width//2, height//2 + 150))  # Position at bottom
    window.blit(restart_text, restart_rect)  # Draw text

# -------------------------------------------------------------------------
# GAME MECHANICS AND LOGIC FUNCTIONS
# -------------------------------------------------------------------------

def initialize_board(grid):
    """
    Initialize the game board with two tiles of value 2 at random positions.
    
    :param grid: 2D list representing the empty game board
    :return: Updated grid with two initial tiles
    """
    # Find all empty cells on the board
    empty_cells = [(x, y) for y in range(grid_size) 
                   for x in range(grid_size) if grid[y][x] == 0]
    
    # Place two '2' tiles at random empty positions
    if len(empty_cells) >= 2:
        # Select first random position
        first_pos = random.choice(empty_cells)
        empty_cells.remove(first_pos)  # Remove to avoid selecting twice
        
        # Select second random position from remaining cells
        second_pos = random.choice(empty_cells)
        
        # Place '2' values at both selected positions
        # Note: y comes first in grid[y][x] because the outer list represents rows
        grid[first_pos[1]][first_pos[0]] = 2
        grid[second_pos[1]][second_pos[0]] = 2
    
    return grid

def move_left(grid):
    """
    Move all tiles to the left and merge tiles with the same value.
    This is the primary move function that other moves are derived from.
    
    :param grid: 2D list representing the current game board
    :return: Updated grid after moving left
    """
    # Create a deep copy of the grid to modify (avoid changing original)
    new_grid = [row[:] for row in grid]
    
    # Process each row in the grid
    for y in range(grid_size):
        # Extract non-zero tiles from the row (remove empty spaces)
        row = [tile for tile in new_grid[y] if tile != 0]
        
        # Merge adjacent tiles with same value
        merged_row = []
        i = 0
        while i < len(row):
            if i < len(row) - 1 and row[i] == row[i+1]:
                # If current tile matches next tile, merge them (double value)
                merged_row.append(row[i] * 2)
                i += 2  # Skip the next tile since we merged it
            else:
                # If no merge, keep the tile as is
                merged_row.append(row[i])
                i += 1
        
        # Add zeros to fill the remaining space in the row
        merged_row = merged_row + [0] * (grid_size - len(merged_row))
        
        # Update the row in the new grid
        new_grid[y] = merged_row
    
    return new_grid

def move_right(grid):
    """
    Move all tiles to the right and merge tiles with the same value.
    
    :param grid: 2D list representing the current game board
    :return: Updated grid after moving right
    """
    # Create a deep copy of the grid to modify
    new_grid = [row[:] for row in grid]
    
    # Process each row in the grid
    for y in range(grid_size):
        # Extract non-zero tiles from the row (remove empty spaces)
        row = [tile for tile in new_grid[y] if tile != 0]
        
        # Merge adjacent tiles with same value (right to left)
        merged_row = []
        i = len(row) - 1  # Start from rightmost tile
        while i >= 0:
            if i > 0 and row[i] == row[i-1]:
                # If current tile matches previous tile, merge them
                merged_row.insert(0, row[i] * 2)  # Insert at beginning to maintain order
                i -= 2  # Skip the previous tile since we merged it
            else:
                # If no merge, keep the tile as is
                merged_row.insert(0, row[i])
                i -= 1
        
        # Add zeros to fill the remaining space (at the beginning for right move)
        merged_row = [0] * (grid_size - len(merged_row)) + merged_row
        
        # Update the row in the new grid
        new_grid[y] = merged_row
    
    return new_grid

def move_up(grid):
    """
    Move all tiles up and merge tiles with the same value.
    Uses transposition to reuse the left move logic.
    
    :param grid: 2D list representing the current game board
    :return: Updated grid after moving up
    """
    # Transpose the grid (rows become columns)
    # This allows reusing the left move logic for vertical movement
    transposed = list(map(list, zip(*grid)))
    
    # Apply left move logic to the transposed grid
    moved = move_left(transposed)
    
    # Transpose back to get the original orientation
    return list(map(list, zip(*moved)))

def move_down(grid):
    """
    Move all tiles down and merge tiles with the same value.
    Uses transposition to reuse the right move logic.
    
    :param grid: 2D list representing the current game board
    :return: Updated grid after moving down
    """
    # Transpose the grid (rows become columns)
    # This allows reusing the right move logic for vertical movement
    transposed = list(map(list, zip(*grid)))
    
    # Apply right move logic to the transposed grid
    moved = move_right(transposed)
    
    # Transpose back to get the original orientation
    return list(map(list, zip(*moved)))

def check_game_over(grid):
    """
    Check if the game is over by looking for possible moves.
    Game is over when there are no empty cells and no adjacent tiles can be merged.
    
    :param grid: 2D list representing the current game board
    :return: Boolean indicating if the game is over (True = game over)
    """
    # Check if there are any empty cells
    if any(0 in row for row in grid):
        return False  # Game not over if empty cells exist
    
    # Check horizontal adjacency (can tiles be merged horizontally?)
    for y in range(grid_size):
        for x in range(grid_size - 1):
            if grid[y][x] == grid[y][x+1]:
                return False  # Game not over if adjacent tiles can be merged
    
    # Check vertical adjacency (can tiles be merged vertically?)
    for x in range(grid_size):
        for y in range(grid_size - 1):
            if grid[y][x] == grid[y+1][x]:
                return False  # Game not over if adjacent tiles can be merged
    
    # No moves possible - game over
    return True

def calculate_score(grid):
    """
    Calculate the total score by summing all tile values on the board.
    
    :param grid: 2D list representing the current game board
    :return: Total score (sum of all tiles)
    """
    return sum(sum(row) for row in grid)

def add_new_tile(grid):
    """
    Add a new tile (2 or 4) to a random empty cell after each move.
    The probability is 90% for a 2 tile and 10% for a 4 tile.
    
    :param grid: 2D list representing the current game board
    :return: Updated grid with a new tile
    """
    # Find all empty cells
    empty_cells = [(x, y) for y in range(grid_size) 
                    for x in range(grid_size) if grid[y][x] == 0]
    
    # If there are empty cells, add a new tile
    if empty_cells:
        # Choose a random empty cell
        new_tile_pos = random.choice(empty_cells)
        
        # Generate a 2 (90% probability) or a 4 (10% probability)
        new_value = 2 if random.random() < 0.9 else 4
        
        # Place the new tile on the board
        grid[new_tile_pos[1]][new_tile_pos[0]] = new_value
    
    return grid

# -------------------------------------------------------------------------
# MAIN GAME FUNCTION
# -------------------------------------------------------------------------

def main():
    """
    Main game function that handles the game loop, user input, and AI mode.
    """
    # Create initial empty game grid
    game_grid = create_grid()

    # Initialize the game grid with two '2' tiles
    game_grid = initialize_board(game_grid)
    
    # Create the AI agent for automated gameplay
    agent = HeuristicAgent()
    
    # Game state variables
    running = True  # Controls the main game loop
    game_over = False  # Tracks if the game has ended
    ai_mode = False  # Toggle between manual play and AI control
    ai_delay = 50  # Milliseconds delay between AI moves (for visualization)
    last_ai_move_time = 0  # Timestamp of the last AI move
    
    # Main game loop
    while running:
        current_time = pygame.time.get_ticks()  # Current time for AI move timing
        
        # Event handling - process user input
        for event in pygame.event.get():
            # Handle window close event
            if event.type == pygame.QUIT:
                pygame.quit()
                import os
                os._exit(0)  # Force immediate termination
            
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if game_over:
                    # If game is over, check for restart
                    if event.key == pygame.K_SPACE:
                        # Create new game
                        game_grid = create_grid()
                        game_grid = initialize_board(game_grid)
                        game_over = False
                else:
                    # Toggle AI mode with 'a' key
                    if event.key == pygame.K_a:
                        ai_mode = not ai_mode
                        print(f"AI mode: {'ON' if ai_mode else 'OFF'}")
                        
                        # Display current board state when AI mode is activated
                        if ai_mode:
                            agent.print_board_state(game_grid)
                    
                    # Handle manual game moves (when AI mode is off)
                    if not ai_mode:
                        move_made = False
                        
                        # Process arrow key inputs for moves
                        if event.key == pygame.K_LEFT:
                            game_grid = move_left(game_grid)
                            move_made = True
                        elif event.key == pygame.K_RIGHT:
                            game_grid = move_right(game_grid)
                            move_made = True
                        elif event.key == pygame.K_UP:
                            game_grid = move_up(game_grid)
                            move_made = True
                        elif event.key == pygame.K_DOWN:
                            game_grid = move_down(game_grid)
                            move_made = True
                        
                        # Add a new tile if a move was made
                        if move_made:
                            add_new_tile(game_grid)
                            
                            # Check if the game is over after move
                            if check_game_over(game_grid):
                                game_over = True
        
        # AI move handling (when AI mode is active)
        if ai_mode and not game_over and current_time - last_ai_move_time >= ai_delay:
            # Get the AI agent's decision based on current board state
            move = agent.make_decision(game_grid)
            
            # Apply the chosen move if one was returned
            if move:
                # Output the AI's choice
                print(f"AI chooses: {move}")
                
                # Execute the selected move
                if move == "left":
                    game_grid = move_left(game_grid)
                elif move == "right":
                    game_grid = move_right(game_grid)
                elif move == "up":
                    game_grid = move_up(game_grid)
                elif move == "down":
                    game_grid = move_down(game_grid)
                
                # Add a new tile after the move
                add_new_tile(game_grid)
                
                # Display updated board state
                agent.print_board_state(game_grid)
                
                # Check if the game is over after AI move
                if check_game_over(game_grid):
                    game_over = True
                    print("Game Over!")
                    print(f"Final Score: {calculate_score(game_grid)}")
            
            # Update timing for the next AI move
            last_ai_move_time = current_time

        # Rendering code - draw the game state
        # Clear the screen with background color
        window.fill(background_color)

        # Draw the current game grid
        draw_grid(game_grid)

        # If game over, draw the game over screen
        if game_over:
            draw_game_over(calculate_score(game_grid))

        # Update the display to show the new frame
        pygame.display.update()
    
    # Clean up resources when the game loop exits
    pygame.quit()

# Entry point - run the game if script is executed directly
if __name__ == "__main__":
    main()