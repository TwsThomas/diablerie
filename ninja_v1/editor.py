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

def add_h_line(pos, event):
    """Add a horizontal line at the specified position."""
    if event.x < 0 or event.x > 0:  # Horizontal scroll
        # Draw a horizontal line at the current position, not in margins
        pygame.draw.line(
            screen,
            colors["horizontal_line"],
            (LEFT_MARGIN, pos[1]),
            (DISPLAY_SIZE[0] - RIGHT_MARGIN, pos[1]),
            2,
        )
        state.level.horizontal_lines.append(pos[1])
        debug(f"Added horizontal line at {pos[1]}")
    else:
        warning("Invalid mouse event for adding horizontal line")

def add_v_line(pos):
    """Add a vertical line at the specified position."""
    # Draw a vertical line at the current position, not in margins
    pygame.draw.line(
        screen,
        colors["vertical_line"],
        (pos[0], TOP_MARGIN),
        (pos[0], DISPLAY_SIZE[1] - BOTTOM_MARGIN),
        2,
    )
    state.level.vertical_lines.append(pos[0])
    debug(f"Added vertical line at {pos[0]}")

def remove_block(row, col):
    """Remove the block at the specified row and column."""
    if 0 <= row < len(state.level.grid) and 0 <= col < len(state.level.grid[0]):
        state.level.grid[row][col] = None
        display_block(row, col, None)
    else:
        error(f"Invalid position ({row}, {col}) for removing block")