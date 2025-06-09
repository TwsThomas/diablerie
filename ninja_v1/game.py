import os
import sys
import random
import math

import pygame
from pygame.locals import *

pygame.init()
pygame.display.set_caption("Diablerie")
pygame.mouse.set_visible(True)

from utils import *
from spark import draw_sparkles
from level import create_level, load_level, save_level, display_grid
from data.scripts.entity import (
    Entity,
)  # Base class for all entities (e.g. player, items, enemies)

# Macbook : 2560 × 1600
DISPLAY_SIZE = (1092, 256)
FPS = 60
grille = []
debug_lines = []
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
pygame.display.set_mode(DISPLAY_SIZE, pygame.NOFRAME | pygame.RESIZABLE)

screen = pygame.display.set_mode(DISPLAY_SIZE)
clock = pygame.time.Clock()
blocks = {
    "block": pygame.image.load("data/images/tile.png").convert_alpha(),
    "spike": pygame.image.load("img/spike.png").convert_alpha(),
    "door": pygame.image.load("img/door.png").convert_alpha(),
    # "chest": pygame.image.load('img/chest.png').convert_alpha(),
    "orbe": pygame.image.load("img/orbe.png").convert_alpha(),
    "wheel": pygame.image.load("img/wheel.png").convert_alpha(),
}

# resize all image to TILE_SIZE
TILE_SIZE = 32
for key in blocks:
    if key == "spike":
        # rotate the spike image by 180 degrees
        blocks[key] = pygame.transform.rotate(blocks[key], 180)
    blocks[key] = pygame.transform.scale(blocks[key], (TILE_SIZE, TILE_SIZE))

colors = {  # cf https://htmlcolorcodes.com/fr/
    "background": (22, 19, 40),
    "background_dark": (26, 24, 54),
    "tile": (255, 255, 255),
    "horizontal_line": (173, 216, 230),  # pastel blue
    "vertical_line": (255, 140, 0),  # dark orange
    "click_start": (23, 160, 204),
    "click_hover": (34, 218, 140),
    "click_end": (163, 17, 37),
    "star": (255, 215, 0),  # gold color for the star
    "debug_text": (255, 255, 255),
    "console_border": (100, 100, 100),
    "console_background": (30, 30, 30),
}


def debug(*args):
    global debug_lines
    print("DEBUG:", *args)
    # Add the debug message to the list
    msg = " ".join(map(str, args))
    debug_lines.append(msg)
    # Limit the number of lines to avoid overflow
    if len(debug_lines) > 20:
        debug_lines = debug_lines[-20:]
    # Draw all debug lines on the left, stacked vertically
    font = pygame.font.SysFont("Arial", 10)
    for i, line in enumerate(debug_lines):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, 10 + i * 14))


def handle_mouse(event):
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


def display_img(pos, img):
    screen.blit(img, pos)



def main():
    screen.fill(colors["background"])
    grid = load_level("level.txt")
    display_grid(screen, grid)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            handle_mouse(event)

        pygame.display.update()
        clock.tick(FPS)


main()
