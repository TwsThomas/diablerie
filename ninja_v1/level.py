# --- Level grid logic ---
import pygame


LEVEL_ROWS = 15
LEVEL_COLS = 40
LEVEL_FILE = "level.txt"


def create_level():
    """Create a 15x40 grid: bottom 3 rows are 'block', rest are None."""
    grid = []
    for row in range(LEVEL_ROWS):
        if row >= LEVEL_ROWS - 3:
            grid.append(["block"] * LEVEL_COLS)
        else:
            grid.append([None] * LEVEL_COLS)
    return grid


def save_level(grid, filename=LEVEL_FILE):
    """Save the grid to a file as text (one row per line, comma-separated)."""
    with open(filename, "w") as f:
        for row in grid:
            f.write(",".join(cell if cell else "." for cell in row) + "\n")


def load_level(filename=LEVEL_FILE):
    """Load the grid from a file."""
    grid = []
    with open(filename, "r") as f:
        for line in f:
            row = [cell if cell != "." else None for cell in line.strip().split(",")]
            grid.append(row)
    return grid


def display_grid(screen, grid):
    """Display the grid on the screen."""
    for row in range(LEVEL_ROWS):
        for col in range(LEVEL_COLS):
            cell = grid[row][col]
            if cell == "block":
                pygame.draw.rect(screen, (100, 100, 100), (col * 20, row * 20, 20, 20))
            elif cell is None:
                pygame.draw.rect(screen, (0, 0, 0), (col * 20, row * 20, 20, 20), 1)