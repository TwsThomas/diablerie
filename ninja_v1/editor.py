from constants import *
from utils import *
from screen import display_block


def add_block(row, col, block_type):
    """Add a block of the specified type at the given row and column."""
    if 0 <= row < len(state.level.grid) and 0 <= col < len(state.level.grid[0]):
        state.level.grid[row][col] = block_type
    else:
        error(f"Invalid position ({row}, {col}) for adding block {block_type}")
    display_block(row, col, block_type)