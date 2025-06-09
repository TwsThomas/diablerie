import os
import sys
import random
import math

import pygame
from pygame.locals import *

pygame.init()
pygame.display.set_caption("Diablerie")
pygame.mouse.set_visible(True)

from constants import *
from utils import *
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
            handle_mouse(event)

        pygame.display.update()
        clock.tick(FPS)



screen.fill(colors["background"])

grid = create_base_level()
save_level(grid, "level.txt")
grid = load_level("level.txt")
display_grid(grid)
main()
