import pygame
import os
from typing import List, Optional, Set, Tuple, Dict, Any

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

def load_image(path: str) -> pygame.Surface:
    """Load an image from the given path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file '{path}' does not exist.")
    img = pygame.image.load(path).convert_alpha()
    img.set_colorkey((0, 0, 0))  # Black is transparent
    return img

blocks: Dict[str, pygame.Surface] = {
    "empty": load_image("img/empty.png"),
    "block": load_image("data/images/tile.png"),
    "spike": load_image("img/spike.png"),
    "door": load_image("img/door.png"),
    # "chest": load_image('img/chest.png'),
    # "key": load_image('img/key.png'),
    # "v_button": load_image('img/v_button.png'),
    # "h_button": load_image('img/h_button.png'),
    "orbe": load_image("img/orbe.png"),
    "wheel": load_image("img/wheel.png"),
    "monster": load_image("img/monster.png"),
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
    "click": (23, 160, 204),  # blue color for click
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
    "gold": (255, 215, 0),
}

class Level:
    def __init__(
        self,
        grid: List[List[Optional[str]]] = None,
        vertical_lines: List[Optional[int]] = None,
        horizontal_lines: List[Optional[int]] = None,
        traps: List[Optional[str]] = None,
    ):
        self.grid = grid
        self.traps = traps if traps is not None else []
        self.vertical_lines = vertical_lines if vertical_lines is not None else []
        self.horizontal_lines = horizontal_lines if horizontal_lines is not None else []


class State:
    def __init__(self):
        self.current_block: Optional[str] = 'block'  # Current block type to place in editor
        self.debug_lines: list[str] = []
        self.level: Level = None
        self.show_grid = False
        self.show_lines = False


state = State()  # Global state object to hold current game state