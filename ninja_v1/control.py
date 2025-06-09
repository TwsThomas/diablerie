from constants import DISPLAY_SIZE, blocks, colors, screen, state, LEFT_MARGIN, TOP_MARGIN, TILE_SIZE, LEVEL_ROWS, LEVEL_COLS, RIGHT_MARGIN, BOTTOM_MARGIN
from typing import Tuple, Dict, Any
from editor import add_block
from utils import debug, warning, error
from screen import display_block, display_img, get_grid_or_margin_cell, show_grid_border
from level import save_level
import pygame
import os

def handle_keyboard(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            os._exit(0)  # Exit the program
        elif event.key == pygame.K_g:
            if not state.show_grid:
                show_grid_border(colors["grey"])
                state.show_grid = True
            else:
                show_grid_border(colors["background"])
                state.show_grid = False
        elif event.key == pygame.K_b or event.key == pygame.K_LESS:
            all_blocks = list(blocks.keys())
            next_block_type = all_blocks[(all_blocks.index(state.current_block) + 1) % len(all_blocks)]
            state.current_block = next_block_type
            display_block(1,1, state.current_block)

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
        else:
            error(f"Invalid cell: {cell}")
    if event.type == pygame.MOUSEMOTION and event.buttons[0]:  # hover
        pos = event.pos
        pygame.draw.circle(screen, colors["click_hover"], pos, 1)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        # Left mouse button released
        pos = event.pos
        pygame.draw.circle(screen, colors["click_end"], pos, 2)
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

def pygame_filename_input(prompt: str = "Enter filename:", default: str = "") -> str:
    """Display a simple filename input box using Pygame only. Returns the entered filename or None if cancelled."""
    font = pygame.font.SysFont("Arial", 24)
    input_box = pygame.Rect(DISPLAY_SIZE[0] // 2 - 150, DISPLAY_SIZE[1] // 2 - 25, 300, 50)
    color_inactive = colors['console_border']
    color_active = colors['star']
    color = color_inactive
    active = True
    text = default
    done = False
    clock = pygame.time.Clock()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text.strip() if text.strip() else None
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 32 and event.unicode.isprintable():
                        text += event.unicode
        # Draw background overlay
        overlay = pygame.Surface(DISPLAY_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 10))
        screen.blit(overlay, (0, 0))
        # Draw input box
        pygame.draw.rect(screen, color, input_box, 2)
        prompt_surf = font.render(prompt, True, colors['debug_text'])
        screen.blit(prompt_surf, (input_box.x + 10, input_box.y - 30))
        txt_surface = font.render(text, True, colors['debug_text'])
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()
        clock.tick(30)
    return None
