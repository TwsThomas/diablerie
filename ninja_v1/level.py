# --- Level grid logic ---
import pygame
from typing import List, Optional

from constants import LEVEL_ROWS, LEVEL_COLS, colors, blocks, TILE_SIZE, LEFT_MARGIN, TOP_MARGIN
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

    print(f"Created base level with {rows} rows and {cols} columns")
    return grid


def save_level(grid, filename="new_level.lvl"):
    """Save the grid to a file as text (one row per line, comma-separated)."""
    with open(filename, "w") as f:
        for row in grid:
            f.write(",".join(cell if cell else "." for cell in row) + "\n")
    print(f"Level saved to {filename}")


def load_level(filename="new_level.lvl"):
    """Load the grid from a file."""
    grid = []
    with open(filename, "r") as f:
        for line in f:
            row = [cell if cell != "." else None for cell in line.strip().split(",")]
            grid.append(row)
    print(f"Level loaded from {filename}, {len(grid)} rows")
    return grid


def display_grid(grid: List[List[Optional[str]]]) -> None:
    """Display the grid with display_block for each cell."""
    print(f"Displaying grid: {len(grid)} rows, {len(grid[0]) if grid else 0} columns")
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            cell = grid[row][col]
            display_block(row, col, cell)

