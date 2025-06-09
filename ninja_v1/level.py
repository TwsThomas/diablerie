# --- Level grid logic ---
import pygame

from constants import LEVEL_ROWS, LEVEL_COLS, colors, blocks, TILE_SIZE, LEFT_MARGIN
from utils import debug, warning, error
from screen import display_block, display_img

def create_base_level(rows = LEVEL_ROWS, cols = LEVEL_COLS):
    """Create a grid with specified rows and columns."""
    grid = []
    for row in range(rows):
        if row == rows - 5:
            grid.append(["spike"] * cols)
        elif row >= rows - 4:
            grid.append(["block"] * cols)
        else:
            grid.append([None] * cols)
    return grid


def save_level(grid, filename="new_level.lvl"):
    """Save the grid to a file as text (one row per line, comma-separated)."""
    with open(filename, "w") as f:
        for row in grid:
            f.write(",".join(cell if cell else "." for cell in row) + "\n")


def load_level(filename="new_level.lvl"):
    """Load the grid from a file."""
    grid = []
    with open(filename, "r") as f:
        for line in f:
            row = [cell if cell != "." else None for cell in line.strip().split(",")]
            grid.append(row)
    return grid


def display_grid(grid):
    """Display the grid on the screen, offset by margins."""
    print(f"Displaying grid: {len(grid)} rows, {len(grid[0]) if grid else 0} columns")
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            cell = grid[row][col]
            display_block(row, col, cell)
                pass
            else:
                display_block(row, col, cell)
                
def show_grid_border(grid):
    """Display the grid border, offset by margins."""
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            pygame.draw.rect(
                pygame.display.get_surface(),
                colors['grey'],
                (LEFT_MARGIN + col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                1
            )