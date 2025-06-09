import os
import sys
import random
import math

import pygame
from pygame.locals import *
from typing import Optional, Any, Callable, Dict, List, Tuple


pygame.init()
pygame.display.set_caption("Diablerie")
pygame.mouse.set_visible(True)

from constants import *
from utils import *
from control import handle_keyboard, handle_mouse
from spark import draw_sparkles
from level import load_level, save_level, display_grid, create_base_level
from screen import display_img

from data.scripts.entity import (
    Entity,
)  # Base class for all entities (e.g. player, items, enemies)


def main():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            handle_mouse(event, grid, state=None)
            handle_keyboard(event, grid, state=None)

        pygame.display.update()
        clock.tick(FPS)


# fill the screen with the background color
screen.fill(colors["background"])
# fill the margins with the margin color
pygame.draw.rect(screen, colors["left_margin"], (0, 0, LEFT_MARGIN, DISPLAY_SIZE[1]))
pygame.draw.rect(screen, colors["bottom_margin"], (0, DISPLAY_SIZE[1] - BOTTOM_MARGIN, DISPLAY_SIZE[0], BOTTOM_MARGIN))


grid = create_base_level()
save_level(grid, "level.txt")
grid = load_level("level.txt")
display_grid(grid)
main()
