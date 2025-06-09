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
            handle_mouse(event)
            handle_keyboard(event)

        pygame.display.update()
        clock.tick(FPS)


# fill the screen with the background color
screen.fill(colors["background"])
# fill the margins with the margin color
pygame.draw.rect(screen, colors["left_margin"], (0, 0, LEFT_MARGIN, DISPLAY_SIZE[1]))
pygame.draw.rect(screen, colors["bottom_margin"], (0, DISPLAY_SIZE[1] - BOTTOM_MARGIN, DISPLAY_SIZE[0], BOTTOM_MARGIN))
pygame.draw.rect(screen, colors["right_margin"], (DISPLAY_SIZE[0] - RIGHT_MARGIN, 0, RIGHT_MARGIN, DISPLAY_SIZE[1]))
pygame.draw.rect(screen, colors["top_margin"], (0, 0, DISPLAY_SIZE[0], TOP_MARGIN))

# write top text 
font = pygame.font.Font(None, 24)
text = font.render("Diablerie_v1         " \
"g : show_grid, < : change_block" \
"s : save_level", True, colors["tile"])
screen.blit(text, (LEFT_MARGIN + 10, 10))


level = create_base_level()
save_level(level, "level/level.json")

state.level = load_level("level/a.json")
display_grid()
main()
