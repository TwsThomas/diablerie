from constants import DISPLAY_SIZE, blocks, colors, screen, state, LEFT_MARGIN, TOP_MARGIN, TILE_SIZE, LEVEL_ROWS, LEVEL_COLS, RIGHT_MARGIN, BOTTOM_MARGIN
from typing import Tuple, Dict, Any
from utils import debug, warning, error
from screen import display_block, display_img, get_grid_or_margin_cell, show_grid_border
import pygame
import os


def handle_keyboard(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            os._exit(0)  # Exit the program
        elif event.key == pygame.K_g:
            show_grid_border()
        elif event.key == pygame.K_b or event.key == pygame.K_LESS:
            all_blocks = list(blocks.keys())
            next_block_type = all_blocks[(all_blocks.index(state.current_block) + 1) % len(all_blocks)]
            state.current_block = next_block_type
            display_block(1,1, state.current_block)

def handle_mouse(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
        pos = event.pos
        cell = get_grid_or_margin_cell(pos)
        if "margin" in cell:
            debug(f"Clicked on margin: {cell}")
        elif isinstance(cell, tuple):
            row, col = cell
            display_block(row, col, state.current_block)
        else:
            error(f"Invalid cell: {cell}")
    if event.type == pygame.MOUSEMOTION and event.buttons[0]:  # hover
        pos = event.pos
        pygame.draw.circle(screen, colors["click_hover"], pos, 2)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        # Left mouse button released
        pos = event.pos
        pygame.draw.circle(screen, colors["click_end"], pos, 4)
    if event.type == pygame.MOUSEWHEEL:
        pos = pygame.mouse.get_pos()
        if event.x < 0 or event.x > 0:
            # Draw a horizontal line at the current position, not in margins
            pygame.draw.line(
                screen,
                colors["horizontal_line"],
                (LEFT_MARGIN, pos[1]),
                (DISPLAY_SIZE[0] - RIGHT_MARGIN, pos[1]),
                3,
            )
        elif event.y > 0 or event.y < 0:
            # Draw a vertical line at the left side of the screen, not in margins
            pygame.draw.line(
                screen,
                colors["vertical_line"],
                (pos[0], TOP_MARGIN),
                (pos[0], DISPLAY_SIZE[1] - BOTTOM_MARGIN),
                2,
            )
    # shift is pressed and right mouse button is clicked
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        pos = event.pos
        display_img(pos, blocks["spike"])
        debug(f"Right Click at {pos}")
        # draw gold star shape at the position
        star_points = [
            (pos[0], pos[1] - 10),
            (pos[0] + 3, pos[1] - 3),
            (pos[0] + 10, pos[1]),
            (pos[0] + 3, pos[1] + 3),
            (pos[0], pos[1] + 10),
            (pos[0] - 3, pos[1] + 3),
            (pos[0] - 10, pos[1]),
            (pos[0] - 3, pos[1] - 3),
        ]
        pygame.draw.polygon(screen, colors["star"], star_points)
