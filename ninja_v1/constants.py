
import pygame
import os

# Macbook : 2560 × 1600
TILE_SIZE = 32
LEVEL_ROWS = 15
LEVEL_COLS = 40
DISPLAY_SIZE = (TILE_SIZE * LEVEL_COLS, TILE_SIZE * LEVEL_ROWS)
FPS = 60

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
    "grey": (100, 100, 100),
}
