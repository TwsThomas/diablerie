def draw_sparkles(surface, pos, count=8, color=(255, 255, 0), min_radius=2, max_radius=8):
    """Draw a burst of yellow sparkles at the given position."""
    return

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