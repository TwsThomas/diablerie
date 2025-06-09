from constants import DISPLAY_SIZE, blocks, colors, screen
from utils import debug, warning, error
from screen import display_img
from level import show_grid_border
import pygame
import os


def handle_keyboard(event, grid, state=None):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            os._exit(0)  # Exit the program
        elif event.key == pygame.K_g:
            # display grid border
            show_grid_border(grid)


def handle_mouse(event, grid, state=None):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
        pos = event.pos
        pygame.draw.circle(screen, colors["click_start"], pos, 7)
        display_img(pos, blocks["block"])

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
            # Draw a horizontal line at the current position
            pygame.draw.line(
                screen,
                colors["horizontal_line"],
                (0, pos[1]),
                (DISPLAY_SIZE[0], pos[1]),
                3,
            )
        elif event.y > 0 or event.y < 0:
            # Draw a vertical line at the left side of the screen
            pygame.draw.line(
                screen,
                colors["vertical_line"],
                (pos[0], 0),
                (pos[0], DISPLAY_SIZE[1]),
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
