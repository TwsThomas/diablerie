import pygame
import os
from typing import Optional, Tuple, Dict, Any

# Macbook : 2560 × 1600
TILE_SIZE: int = 32
LEVEL_ROWS: int = 15
LEVEL_COLS: int = 30
# Margins for display
LEFT_MARGIN: int = 120
BOTTOM_MARGIN: int = 50
TOP_MARGIN: int = 50
RIGHT_MARGIN: int = 50
# Update DISPLAY_SIZE to account for all margins
DISPLAY_SIZE: Tuple[int, int] = (
    TILE_SIZE * LEVEL_COLS + LEFT_MARGIN + RIGHT_MARGIN,
    TILE_SIZE * LEVEL_ROWS + TOP_MARGIN + BOTTOM_MARGIN
)
FPS: int = 60

os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
pygame.display.set_mode(DISPLAY_SIZE, pygame.NOFRAME | pygame.RESIZABLE)

screen: pygame.Surface = pygame.display.set_mode(DISPLAY_SIZE)
clock: pygame.time.Clock = pygame.time.Clock()
blocks: Dict[str, pygame.Surface] = {
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

# cf https://htmlcolorcodes.com/fr/
colors: Dict[str, Tuple[int, int, int]] = {
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
    "left_margin": (30, 30, 30),
    "right_margin": (30, 40, 30),
    "top_margin": (40, 30, 30),
    "bottom_margin": (30, 30, 40),
    "grey": (100, 100, 100),
}

class State:
    def __init__(self):
        self.current_block: Optional[str] = 'block'  # Current block type to place
        self.grid: list[list[Optional[str]]] = []  # The grid of blocks
        self.mouse_pos: Tuple[int, int] = (0, 0)  # Current mouse position
        self.selected_cell: Optional[Tuple[int, int]] = None  # Cell currently selected by mouse
        self.console_visible: bool = False  # Whether the console is visible
        self.console_text: str = ""  # Text in the console
        self.debug_lines: list[str] = []
        self.level: None
        self.show_grid = False


state = State()  # Global state object to hold current game state