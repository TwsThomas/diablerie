from constants import (
    DISPLAY_SIZE,
    blocks,
    colors,
    screen,
    state,
    LEFT_MARGIN,
    TOP_MARGIN,
    TILE_SIZE,
    LEVEL_ROWS,
    LEVEL_COLS,
    RIGHT_MARGIN,
    BOTTOM_MARGIN,
)
from typing import Tuple, Dict, Any
from editor import add_block, add_h_line, add_v_line, remove_block
from utils import debug, warning, error, pygame_filename_input
from screen import display_block, display_img, get_grid_or_margin_cell, show_grid_border, show_lines
from level import save_level
import pygame
import os


def handle_keyboard(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
            debug("Exiting the game...")
            pygame.quit()
            os._exit(0)  # Exit the program
        elif event.key == pygame.K_g:
            show_grid_border(colors["background"] if state.show_grid else None)
            state.show_grid = not state.show_grid
        elif event.key == pygame.K_l:
            show_lines(colors["background"] if state.show_lines else None)
            state.show_lines = not state.show_lines

        elif event.key == pygame.K_b or event.key == pygame.K_LESS:
            all_blocks = list(blocks.keys())
            next_block_type = all_blocks[
                (all_blocks.index(state.current_block) + 1) % len(all_blocks)
            ]
            state.current_block = next_block_type
            display_block(1, 1, state.current_block)

        elif event.key == pygame.K_s:
            name = pygame_filename_input("Sauvegarder :", default="")
            filename = f"level/{name}.json" if name else "level/no_name.json"
            save_level(state.level, filename)
            debug(f"Level saved to {filename}")


def handle_mouse(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
        pos = event.pos
        cell = get_grid_or_margin_cell(pos)
        if "margin" in cell:
            debug(f"Clicked on margin: {cell}")
        elif isinstance(cell, tuple):
            row, col = cell
            add_block(row, col, state.current_block)
            pygame.draw.circle(screen, colors["click"], pos, 1)
        else:
            error(f"Invalid cell: {cell}")
    if event.type == pygame.MOUSEMOTION and event.buttons[0]:  # hover
        pos = event.pos
        cell = get_grid_or_margin_cell(pos)
        if "margin" in cell:
            debug(f"Clicked on margin: {cell}")
        elif isinstance(cell, tuple):
            row, col = cell
            add_block(row, col, state.current_block)
        else:
            error(f"Invalid cell: {cell}")
        pygame.draw.circle(screen, colors["click_hover"], pos, 1)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        # Left mouse button released
        pos = event.pos
        pygame.draw.circle(screen, colors["click_end"], pos, 2)

    if event.type == pygame.MOUSEWHEEL:  # Mouse wheel scrolled
        pos = pygame.mouse.get_pos()
        if event.x < 0 or event.x > 0:
            add_h_line(pos, event)
        elif event.y > 0 or event.y < 0:
            add_v_line(pos)

    # right mouse button is clicked
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        pos = event.pos
        cell = get_grid_or_margin_cell(pos)
        if "margin" in cell:
            debug(f"Right Click on margin: {cell}")
        elif isinstance(cell, tuple):
            row, col = cell
            remove_block(row, col)
        else:
            error(f"Invalid cell: {cell}")

        # draw gold small star shape at the position
        star_points = [
            (pos[0], pos[1] - 5),
            (pos[0] + 2, pos[1] - 2),
            (pos[0] + 5, pos[1]),
            (pos[0] + 2, pos[1] + 2),
            (pos[0], pos[1] + 5),
            (pos[0] - 2, pos[1] + 2),
            (pos[0] - 5, pos[1]),
            (pos[0] - 2, pos[1] - 2),
        ]
        pygame.draw.polygon(screen, colors["star"], star_points)