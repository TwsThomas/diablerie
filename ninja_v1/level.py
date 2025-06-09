# --- Level grid logic ---
import pygame
from typing import List, Optional
import json

from constants import (
    LEVEL_ROWS,
    LEVEL_COLS,
    colors,
    blocks,
    TILE_SIZE,
    LEFT_MARGIN,
    TOP_MARGIN,
    state,
)
from utils import debug, warning, error
from screen import display_block, display_img


class Level:
    def __init__(
        self,
        grid: List[List[Optional[str]]] = None,
        vertical_lines: List[Optional[int]] = None,
        horizontal_lines: List[Optional[int]] = None,
        traps: List[Optional[str]] = None,
    ):
        self.grid = grid if grid is not None else create_base_level()
        self.traps = traps if traps is not None else []
        self.vertical_lines = vertical_lines if vertical_lines is not None else []
        self.horizontal_lines = horizontal_lines if horizontal_lines is not None else []


def create_base_level(rows=LEVEL_ROWS, cols=LEVEL_COLS) -> Level:
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
    level = Level(grid)
    return level


def save_level(level: Level, filename="new_level.json"):
    """Save the level in json file format."""
    data = {
        "grid": level.grid,
        "traps": level.traps,
        "vertical_lines": level.vertical_lines,
        "horizontal_lines": level.horizontal_lines,
    }
    # create mkdir if it doesn't exist
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def load_level(filename="new_level.json") -> Level:
    """Load a level from a json file."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        grid = data.get("grid", [])
        traps = data.get("traps", [])
        vertical_lines = data.get("vertical_lines", [])
        horizontal_lines = data.get("horizontal_lines", [])
        level = Level(grid, vertical_lines, horizontal_lines, traps)
        print(f"Loaded level from {filename} with {len(level.grid)} rows and {len(level.grid[0]) if level.grid else 0} columns")
        return level
    except FileNotFoundError:
        warning(f"File {filename} not found. Creating a new level.")
        raise FileNotFoundError(
            f"Level file '{filename}' not found. Please create a new level."
        )


def display_grid() -> None:
    """Display the grid with display_block for each cell."""
    print(
        f"Displaying grid: {len(state.level.grid)} rows, {len(state.level.grid[0]) if state.level.grid else 0} columns"
    )
    for row in range(len(state.level.grid)):
        for col in range(len(state.level.grid[row])):
            cell = state.level.grid[row][col]
            display_block(row, col, cell)
