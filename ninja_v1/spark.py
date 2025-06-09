import random
import math
import pygame
from typing import List, Optional
from constants import *
from utils import debug

def draw_sparkles(surface: pygame.Surface, pos: tuple[int, int], count: int = 8, color: tuple[int, int, int] = (255, 255, 0), min_radius: int = 2, max_radius: int = 8) -> None:
    """Draw a burst of yellow sparkles at the given position."""
    for i in range(count):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(min_radius, max_radius)
        x = int(pos[0] + math.cos(angle) * radius)
        y = int(pos[1] + math.sin(angle) * radius)
        pygame.draw.circle(surface, color, (x, y), 1)

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