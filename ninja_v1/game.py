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
from data.scripts.entity import Entity  # Base class for all entities (e.g. player, items, enemies)

# Macbook : 2560 × 1600
DISPLAY_SIZE = (1092, 256)
FPS = 60
grille = []
debug_lines = []
# Set the environment variable to ensure the window opens at the top left corner
# This is useful for debugging and development purposes
# open the windows top left of the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
# Initialize the display
pygame.display.set_mode(DISPLAY_SIZE, pygame.NOFRAME | pygame.RESIZABLE)
# Set the display size to the defined DISPLAY_SIZE
pygame.display.set_mode(DISPLAY_SIZE, pygame.NOFRAME | pygame.RESIZABLE)


screen = pygame.display.set_mode(DISPLAY_SIZE)
clock = pygame.time.Clock()
blocks = {
    'tile': pygame.image.load('data/images/tile.png').convert_alpha(),
    # "pique": pygame.image.load('data/images/spike.png').convert_alpha(),
    # "porte": pygame.image.load('data/images/door.png').convert_alpha(),
}
colors = { # cf https://htmlcolorcodes.com/fr/
    'background': (22, 19, 40),
    'background_dark': (26, 24, 54),
    'tile': (255, 255, 255),
    'horizontal_line': (173, 216, 230),  # pastel blue
    'vertical_line': (255, 140, 0),  # dark orange
    'click_start': (23, 160, 204),
    'click_hover': (34, 218, 140 ),
    'click_end': (163, 17, 37 ),
    'star': (255, 215, 0),  # gold color for the star
    'debug_text': (255, 255, 255),
    'console_border': (100, 100, 100),
    'console_background': (30, 30, 30),
}


def debug(*args):
    global debug_lines
    print("DEBUG:", *args)
    # Add the debug message to the list
    msg = ' '.join(map(str, args))
    debug_lines.append(msg)
    # Limit the number of lines to avoid overflow
    if len(debug_lines) > 20:
        debug_lines = debug_lines[-20:]
    # Draw all debug lines on the left, stacked vertically
    font = pygame.font.SysFont('Arial', 10)
    for i, line in enumerate(debug_lines):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, 10 + i * 14))

def init_grid():
    pass



def draw_sparkles(surface, pos, count=8, color=(255, 255, 0), min_radius=2, max_radius=8):
    """Draw a burst of yellow sparkles at the given position."""
    return

def handle_mouse(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
        pos = event.pos
        pygame.draw.circle(screen, colors['click_start'], pos, 7)
        draw_sparkles(screen, pos, count=10, color=colors['star'])
    if event.type == pygame.MOUSEMOTION and event.buttons[0]:  # Left mouse button is pressed
        pos = event.pos
        pygame.draw.circle(screen, colors['click_hover'], pos, 2)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        # Left mouse button released
        pos = event.pos
        pygame.draw.circle(screen, colors['click_end'], pos, 4)
        draw_sparkles(screen, pos, count=8, color=colors['star'])
    if event.type == pygame.MOUSEWHEEL:
        pos = pygame.mouse.get_pos()
        if event.x < 0 or event.x > 0:
            # Draw a horizontal line at the current position
            pygame.draw.line(screen, colors['horizontal_line'], (0, pos[1]), (DISPLAY_SIZE[0], pos[1]), 3)
        elif event.y > 0 or event.y < 0:
            # Draw a vertical line at the left side of the screen
            pygame.draw.line(screen, colors['vertical_line'], (pos[0], 0), (pos[0], DISPLAY_SIZE[1]), 2)
    # shift is pressed and right mouse button is clicked
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        pos = event.pos
        debug(f"Right Click at {pos}")
        # draw gold star shape at the position
        star_points = [
            (pos[0], pos[1] - 10),  # Top point
            (pos[0] + 3, pos[1] - 3),  # Right top
            (pos[0] + 10, pos[1]),  # Right middle
            (pos[0] + 3, pos[1] + 3),  # Right bottom
            (pos[0], pos[1] + 10),  # Bottom point
            (pos[0] - 3, pos[1] + 3),  # Left bottom
            (pos[0] - 10, pos[1]),  # Left middle
            (pos[0] - 3, pos[1] - 3)   # Left top
        ]
        pygame.draw.polygon(screen, colors['star'], star_points)
        draw_sparkles(screen, pos, count=12, color=colors['star'])

def sparks(self, pos, vel, size, color, gravity=0.1):
    
    for i, spark in sorted(enumerate(self.sparks), reverse=True):
        if len(spark) < 8:
            spark.append(False)
        if not spark[-1]:
            spark[1][1] = min(spark[1][1] + spark[-2], 3)
        spark[0][0] += spark[1][0]
        if spark[5]:
            if ((int(spark[0][0] // TILE_SIZE), int(spark[0][1] // TILE_SIZE)) in self.tiles) or (spark[0][0] < TILE_SIZE) or (spark[0][0] > DISPLAY_SIZE[0] - TILE_SIZE):
                spark[0][0] -= spark[1][0]
                spark[1][0] *= -0.7
        spark[0][1] += spark[1][1]
        if spark[5]:
            if (int(spark[0][0] // TILE_SIZE), int(spark[0][1] // TILE_SIZE)) in self.tiles:
                spark[0][1] -= spark[1][1]
                spark[1][1] *= -0.7
                if abs(spark[1][1]) < 0.1:
                    spark[1][1] = 0
                    spark[-1] = True
        spark[2] -= spark[3]
        if spark[2] <= 1:
            self.sparks.pop(i)
        else:
            self.display.blit(glow_img(int(spark[2] * 1.5 + 2), (int(spark[4][0] / 2), int(spark[4][1] / 2), int(spark[4][2] / 2))), (spark[0][0] - spark[2] * 2, spark[0][1] + self.height - spark[2] * 2), special_flags=BLEND_RGBA_ADD)
            self.display.blit(glow_img(int(spark[2]), spark[4]), (spark[0][0] - spark[2], spark[0][1] + self.height - spark[2]), special_flags=BLEND_RGBA_ADD)

def glow_img(radius, color):
    """Create a circular glow image (pygame.Surface) with the given radius and color."""
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(255 * (r / radius) ** 2)
        pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
    return surf

def display_img(surf, pos, img, size=None):
    """
    Draw an image (img) onto the surface (surf) at the given position (pos).
    If size is provided, scale the image to that size before blitting.
    """
    if size is not None:
        img = pygame.transform.smoothscale(img, size)
    surf.blit(img, pos)


def main():
    screen.fill(colors['background_dark'])

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            handle_mouse(event)

        pygame.display.update()
        clock.tick(FPS)


main()