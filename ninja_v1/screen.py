from constants import *
import pygame
from typing import List, Optional, Tuple, Union
from utils import debug, warning

def display_block(row: int, col: int, block_type: str = "block") -> None:
    if block_type is None:
        block_type = "empty"
    img = blocks.get(block_type)
    if img:
        display_img((LEFT_MARGIN + col * TILE_SIZE, TOP_MARGIN + row * TILE_SIZE), img)
    else:
        warning(f"Warning: No image found for cell '{block_type}' at ({row}, {col})")

def display_img(pos: Tuple[int, int], img: pygame.Surface) -> None:
    screen.blit(img, pos)

def show_grid_border(color: Tuple[int, int, int] = None) -> None:
    """Display the grid border, offset by margins."""
    for row in range(len(state.level.grid)):
        for col in range(len(state.level.grid[row])):
            pygame.draw.rect(
                pygame.display.get_surface(),
                colors["grey"] if color is None else color,
                (LEFT_MARGIN + col * TILE_SIZE, TOP_MARGIN + row * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                1
            )

def show_lines(color: Tuple[int, int, int] = None) -> None:
    for h_line in state.level.horizontal_lines:
        pygame.draw.line(
            screen,
            colors["horizontal_line"] if color is None else color,
            (LEFT_MARGIN, h_line),
            (DISPLAY_SIZE[0] - RIGHT_MARGIN, h_line),
            2
        )
    for v_line in state.level.vertical_lines:
        pygame.draw.line(
            screen,
            colors["vertical_line"] if color is None else color,
            (LEFT_MARGIN + v_line, TOP_MARGIN),
            (LEFT_MARGIN + v_line, TOP_MARGIN + LEVEL_ROWS * TILE_SIZE),
            2
        )


def get_grid_or_margin_cell(pixel_pos: Tuple[int, int]) -> Union[Tuple[int, int], str, None]:
    """Get the grid cell coordinates for a given position."""
    x, y = pixel_pos
    if x < LEFT_MARGIN:
        return "left_margin"
    if y < TOP_MARGIN:
        return "top_margin"
    col = (x - LEFT_MARGIN) // TILE_SIZE
    row = (y - TOP_MARGIN) // TILE_SIZE
    if 0 <= row < LEVEL_ROWS and 0 <= col < LEVEL_COLS:
        return (row, col)
    else:
        if x >= LEFT_MARGIN + LEVEL_COLS * TILE_SIZE:
            return "right_margin"
        if y >= TOP_MARGIN + LEVEL_ROWS * TILE_SIZE:
            return "bottom_margin"
    return None