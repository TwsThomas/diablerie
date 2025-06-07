import os
import sys
import random
import math

import pygame
from pygame.locals import *

pygame.init()
pygame.display.set_caption('Diablerie')
pygame.mouse.set_visible(True)

from utils import *
from data.scripts.entity import Entity  # Base class for all entities (player, items, etc.)

TILE_SIZE = 16
DISPLAY_SIZE = (1092, 256)
WINDOW_TILE_SIZE = (int(DISPLAY_SIZE[0] // 16), int(DISPLAY_SIZE[1] // 16)) # 12x16 tiles
FPS = 60

screen = pygame.display.set_mode(DISPLAY_SIZE)
clock = pygame.time.Clock()




def main():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((22, 19, 40))
        pygame.display.update()
main()