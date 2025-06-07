import os
import sys
import random
import math

import pygame
from pygame.locals import *

# === Game-specific imports (custom scripts) ===
from data.scripts.entity import Entity  # Base class for all entities (player, items, etc.)
from data.scripts.anim_loader import AnimationManager  # Handles loading and managing animations
from data.scripts.text import Font  # Custom bitmap font rendering

# === Constants and Globals ===
TILE_SIZE = 16
DISPLAY_SIZE = (192, 256)
WINDOW_TILE_SIZE = (int(DISPLAY_SIZE[0] // 16), int(DISPLAY_SIZE[1] // 16))

def setup_pygame():
    pygame.init()
    pygame.display.set_caption('Cavyn')
    pygame.mouse.set_visible(False)
setup_pygame()

# === Utility function to load images with transparency ===
def load_img(path):
    # Ensure display is set before loading images
    if not pygame.display.get_init() or not pygame.display.get_surface():
        pygame.display.set_mode((1, 1))
    img = pygame.image.load(path).convert()
    img.set_colorkey((0, 0, 0))  # Black is transparent
    return img

# === Load all game images ===
tile_img = load_img('data/images/tile.png')
chest_img = load_img('data/images/chest.png')
ghost_chest_img = load_img('data/images/ghost_chest.png')
opened_chest_img = load_img('data/images/opened_chest.png')
placed_tile_img = load_img('data/images/placed_tile.png')
edge_tile_img = load_img('data/images/edge_tile.png')
coin_icon = load_img('data/images/coin_icon.png')
item_slot_img = load_img('data/images/item_slot.png')
item_slot_flash_img = load_img('data/images/item_slot_flash.png')
border_img = load_img('data/images/border.png')
border_img_light = border_img.copy()
border_img_light.set_alpha(100)  # Lighter border for UI effect
white_font = Font('data/fonts/small_font.png', (251, 245, 239))  # White font
black_font = Font('data/fonts/small_font.png', (0, 0, 1))  # Black font (for shadow)

# === Load all sound effects ===
sounds = {sound.split('/')[-1].split('.')[0] : pygame.mixer.Sound('data/sfx/' + sound) for sound in os.listdir('data/sfx')}
sounds['block_land'].set_volume(0.5)
sounds['coin'].set_volume(0.6)
sounds['chest_open'].set_volume(0.8)
sounds['coin_end'] = pygame.mixer.Sound('data/sfx/coin.wav')
sounds['coin_end'].set_volume(0.35)

# === Item icons for UI ===
item_icons = {
    'cube': load_img('data/images/cube_icon.png'),
    'warp': load_img('data/images/warp_icon.png'),
    'jump': load_img('data/images/jump_icon.png'),
}

animation_manager = AnimationManager()  # Handles all animations

# === Utility function to normalize a value towards zero by a given amount ===
def normalize(val, amt):
    if val > amt:
        val -= amt
    elif val < -amt:
        val += amt
    else:
        val = 0
    return val

# === Item entity (collectibles, powerups, coins, etc.) ===
class Item(Entity):
    def __init__(self, *args, velocity=[0, 0]):
        super().__init__(*args)
        self.velocity = velocity  # [x, y] velocity
        self.time = 0  # Lifetime counter

    def update(self, tiles):
        self.time += 1
        self.velocity[1] = min(self.velocity[1] + 0.2, 3)  # Gravity
        self.velocity[0] = normalize(self.velocity[0], 0.05)  # Friction
        self.move(self.velocity, tiles)

# === Player entity ===
class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.velocity = [0, 0]  # [x, y] velocity
        self.right = False  # Moving right
        self.left = False   # Moving left
        self.speed = 1.4    # Horizontal speed
        self.jumps = 20      # Remaining jumps
        self.jumps_max = 20  # Max jumps (double jump)
        self.jumping = False
        self.jump_rot = 0   # Rotation for jump animation
        self.air_time = 0   # Frames in air

    def attempt_jump(self, sparks, player):
        # Try to jump if jumps remain
        if self.jumps:
            if self.jumps == self.jumps_max:
                self.velocity[1] = -5  # Full jump
            else:
                self.velocity[1] = -4  # Weaker jump (double jump)
                # Add sparks for double jump effect
                for i in range(24):
                    physics_on = random.choice([False, False, True])
                    direction = 1
                    if i % 2:
                        direction = -1
                    sparks.append([[player.center[0] + random.random() * 14 - 7, player.center[1]], [direction * (random.random() * 0.05 + 0.05) + (random.random() * 4 - 2) * physics_on, random.random() * 0.05 + random.random() * 2 * physics_on], random.random() * 3 + 3, 0.04 - 0.02 * physics_on, (6, 4, 1), physics_on, 0.05 * physics_on])
            self.jumps -= 1
            self.jumping = True
            self.jump_rot = 0

    def update(self, tiles, dead):
        super().update(1 / 60)
        self.air_time += 1
        if self.jumping:
            self.jump_rot += 16
            if self.jump_rot >= 360:
                self.jump_rot = 0
                self.jumping = False
            if self.flip[0]:
                self.rotation = -self.jump_rot
            else:
                self.rotation = self.jump_rot
            self.scale[1] = 0.7  # Squash for jump
        else:
            self.scale[1] = 1

        self.velocity[1] = min(self.velocity[1] + 0.3, 4)  # Gravity
        motion = self.velocity.copy()
        if not dead:
            if self.right:
                motion[0] += self.speed
            if self.left:
                motion[0] -= self.speed
            if motion[0] > 0:
                self.flip[0] = True
            if motion[0] < 0:
                self.flip[0] = False

        if self.air_time > 3:
            self.set_action('jump')
        elif motion[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        collisions = self.move(motion, tiles)
        if collisions['bottom']:
            self.jumps = self.jumps_max
            self.jumping = False
            self.rotation = 0
            self.velocity[1] = 0
            self.air_time = 0

# === Find all tiles near a given position (for collision, etc.) ===
def lookup_nearby(tiles, pos):
    rects = []
    for offset in [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, 1), (0, -1), (1, -1), (1, 0), (1, 1)]:
        lookup_pos = (pos[0] // TILE_SIZE + offset[0], pos[1] // TILE_SIZE + offset[1])
        if lookup_pos in tiles:
            rects.append(pygame.Rect(lookup_pos[0] * TILE_SIZE, lookup_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return rects

# === Cache for glowing effect images ===
GLOW_CACHE = {}

def glow_img(size, color):
    # Returns a cached glowing circle surface for effects
    if (size, color) not in GLOW_CACHE:
        surf = pygame.Surface((size * 2 + 2, size * 2 + 2))
        pygame.draw.circle(surf, color, (surf.get_width() // 2, surf.get_height() // 2), size)
        surf.set_colorkey((0, 0, 0))
        GLOW_CACHE[(size, color)] = surf
    return GLOW_CACHE[(size, color)]


def init_game_state():
    class GameState:
        def __init__(self):
            self.clock: pygame.time.Clock = pygame.time.Clock()
            self.display: pygame.Surface = pygame.Surface(DISPLAY_SIZE)
            self.screen: pygame.Surface = pygame.display.set_mode((DISPLAY_SIZE[0] * 3, DISPLAY_SIZE[1] * 3), 0, 32)
            self.animation_manager: AnimationManager = animation_manager
            self.player: Player = Player(animation_manager, (DISPLAY_SIZE[0] // 2 - 5, -20), (8, 16), 'player')
            self.dead: bool = False
            self.tiles: dict = {}
            self.tile_drops: list = []
            self.bg_particles: list = []
            self.sparks: list = []
            self.game_timer: int = 0
            self.height: float = 0
            self.target_height: float = 0
            self.coins: int = 0
            self.end_coin_count: int = 0
            self.current_item: str = None
            self.master_clock: int = 0
            self.last_place: int = 0
            self.item_used: bool = False
            self.items: list = []
            self.stack_heights: list = [WINDOW_TILE_SIZE[1] - 1 for _ in range(WINDOW_TILE_SIZE[0] - 2)]
            self.stack_heights[0] -= 1
            self.stack_heights[-1] -= 1
            self.tile_drop_rects: list = []
            self.tile_rects: list = []
            self.base_row: int = 0
            # Initial tile setup
            for i in range(WINDOW_TILE_SIZE[0] - 2):
                self.tiles[(i + 1, WINDOW_TILE_SIZE[1] - 1)] = 'tile'
            self.tiles[(1, WINDOW_TILE_SIZE[1] - 2)] = 'tile'
            self.tiles[(WINDOW_TILE_SIZE[0] - 2, WINDOW_TILE_SIZE[1] - 2)] = 'tile'
            # Music
            pygame.mixer.music.load('data/music.wav')
            pygame.mixer.music.play(-1)

        def update_bg_particles(self):
            display = self.display
            parallax = random.random()
            for _ in range(2):
                self.bg_particles.append([[random.random() * DISPLAY_SIZE[0], DISPLAY_SIZE[1] - self.height * parallax], parallax, random.randint(1, 8), random.random() * 1 + 1, random.choice([(0, 0, 0), (22, 19, 40)])])
            for i, p in sorted(enumerate(self.bg_particles), reverse=True):
                size = p[2]
                if p[-1] != (0, 0, 0):
                    size = size * 5 + 4
                p[2] -= 0.01
                p[0][1] -= p[3]
                if size < 1:
                    display.set_at((int(p[0][0]), int(p[0][1] + self.height * p[1])), (0, 0, 0))
                else:
                    if p[-1] != (0, 0, 0):
                        pygame.draw.circle(display, p[-1], p[0], int(size), 4)
                    else:
                        pygame.draw.circle(display, p[-1], p[0], int(size))
                if size < 0:
                    self.bg_particles.pop(i)

        def handle_tile_drops(self):
            if self.master_clock > 180:
                self.game_timer += 1
                if self.game_timer > 10 + 25 * (20000 - min(20000, self.master_clock)) / 20000:
                    self.game_timer = 0
                    minimum = min(self.stack_heights)
                    options = []
                    for i, stack in enumerate(self.stack_heights):
                        if i != self.last_place:
                            offset = stack - minimum
                            for j in range(int(offset ** (2.2 - min(20000, self.master_clock) / 10000)) + 1):
                                options.append(i)
                    tile_type = 'tile'
                    if random.randint(1, 10) == 1:
                        tile_type = 'chest'
                    c = random.choice(options)
                    self.last_place = c
                    self.tile_drops.append([(c + 1) * TILE_SIZE, -self.height - TILE_SIZE, tile_type])
            tile_drop_rects = []
            for i, tile in sorted(enumerate(self.tile_drops), reverse=True):
                tile[1] += 1.4
                pos = [tile[0] + TILE_SIZE // 2, tile[1] + TILE_SIZE]
                r = pygame.Rect(tile[0], tile[1], TILE_SIZE, TILE_SIZE)
                tile_drop_rects.append(r)
                if r.colliderect(self.player.rect):
                    if not self.dead:
                        sounds['death'].play()
                        self.player.velocity = [1.3, -6]
                        for i in range(380):
                            angle = random.random() * math.pi
                            speed = random.random() * 1.5
                            physics_on = random.choice([False, True, True])
                            self.sparks.append([self.player.center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 2, 2), physics_on, 0.1 * physics_on])
                    self.dead = True
                check_pos = (int(pos[0] // TILE_SIZE), int(math.floor(pos[1] / TILE_SIZE)))
                if check_pos in self.tiles:
                    self.tile_drops.pop(i)
                    place_pos = (check_pos[0], check_pos[1] - 1)
                    self.stack_heights[place_pos[0] - 1] = place_pos[1]
                    self.tiles[place_pos] = tile[2]
                    sounds['block_land'].play()
                    if self.tiles[check_pos] == 'chest':
                        self.tiles[check_pos] = 'tile'
                        sounds['chest_destroy'].play()
                        for i in range(100):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 2.5
                            self.sparks.append([[place_pos[0] * TILE_SIZE + TILE_SIZE // 2, place_pos[1] * TILE_SIZE + TILE_SIZE // 2], [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.09, (12, 8, 2), False, 0.1])
                    continue
                if random.randint(1, 4) == 1:
                    side = random.choice([1, -1])
                    self.sparks.append([[tile[0] + TILE_SIZE * (side == 1), tile[1]], [random.random() * 0.1 - 0.05, random.random() * 0.5], random.random() * 5 + 3, 0.15, (4, 2, 12), False, 0])
                self.display.blit(tile_img, (tile[0], tile[1] + self.height))
                if tile[2] == 'chest':
                    self.display.blit(ghost_chest_img, (tile[0], tile[1] + self.height - TILE_SIZE))
            self.tile_drop_rects = tile_drop_rects

        def draw_tiles(self):
            self.tile_rects = []
            for tile in self.tiles:
                self.display.blit(tile_img, (TILE_SIZE * tile[0], TILE_SIZE * tile[1] + int(self.height)))
                if self.tiles[tile] == 'placed_tile':
                    self.display.blit(placed_tile_img, (TILE_SIZE * tile[0], TILE_SIZE * tile[1] + int(self.height)))
                if self.tiles[tile] == 'chest':
                    self.display.blit(chest_img, (TILE_SIZE * tile[0], TILE_SIZE * (tile[1] - 1) + int(self.height)))
                    chest_r = pygame.Rect(TILE_SIZE * tile[0] + 2, TILE_SIZE * (tile[1] - 1) + 6, TILE_SIZE - 4, TILE_SIZE - 6)
                    if random.randint(1, 20) == 1:
                        self.sparks.append([[tile[0] * TILE_SIZE + 2 + 12 * random.random(), (tile[1] - 1) * TILE_SIZE + 4 + 8 * random.random()], [0, random.random() * 0.25 - 0.5], random.random() * 4 + 2, 0.023, (12, 8, 2), True, 0.002])
                    if chest_r.colliderect(self.player.rect):
                        sounds['chest_open'].play()
                        for i in range(50):
                            self.sparks.append([[tile[0] * TILE_SIZE + 8, (tile[1] - 1) * TILE_SIZE + 8], [random.random() * 2 - 1, random.random() - 2], random.random() * 3 + 3, 0.01, (12, 8, 2), True, 0.05])
                        self.tiles[tile] = 'opened_chest'
                        self.player.jumps += 1
                        self.player.attempt_jump(self.sparks, self.player)
                        self.player.velocity[1] = -3.5
                        if random.randint(1, 5) < 3:
                            self.items.append(Item(animation_manager, (tile[0] * TILE_SIZE + 5, (tile[1] - 1) * TILE_SIZE + 5), (6, 6), random.choice(['warp', 'cube', 'jump']), velocity=[random.random() * 5 - 2.5, random.random() * 2 - 5]))
                        else:
                            for i in range(random.randint(2, 6)):
                                self.items.append(Item(animation_manager, (tile[0] * TILE_SIZE + 5, (tile[1] - 1) * TILE_SIZE + 5), (6, 6), 'coin', velocity=[random.random() * 5 - 2.5, random.random() * 2 - 7]))
                elif self.tiles[tile] == 'opened_chest':
                    self.display.blit(opened_chest_img, (TILE_SIZE * tile[0], TILE_SIZE * (tile[1] - 1) + int(self.height)))
            base_row = max(self.tiles, key=lambda x: x[1])[1] - 1
            filled = True
            for i in range(WINDOW_TILE_SIZE[0] - 2):
                if (i + 1, base_row) not in self.tiles:
                    filled = False
            if filled:
                self.target_height = math.floor(self.height / TILE_SIZE) * TILE_SIZE + TILE_SIZE
            if self.height != self.target_height:
                self.height += (self.target_height - self.height) / 10
                if abs(self.target_height - self.height) < 0.2:
                    self.height = self.target_height
                    for i in range(WINDOW_TILE_SIZE[0] - 2):
                        del self.tiles[(i + 1, base_row + 1)]
            for i in range(WINDOW_TILE_SIZE[1] + 2):
                pos_y = (-self.height // 16) - 1 + i
                self.display.blit(edge_tile_img, (0, TILE_SIZE * pos_y + int(self.height)))
                self.display.blit(edge_tile_img, (TILE_SIZE * (WINDOW_TILE_SIZE[0] - 1), TILE_SIZE * pos_y + int(self.height)))
            self.tile_rects.append(pygame.Rect(0, self.player.pos[1] - 300, TILE_SIZE, 600))
            self.tile_rects.append(pygame.Rect(TILE_SIZE * (WINDOW_TILE_SIZE[0] - 1), self.player.pos[1] - 300, TILE_SIZE, 600))
            self.base_row = base_row

        def draw_items(self):
            for i, item in sorted(enumerate(self.items), reverse=True):
                lookup_pos = (int(item.center[0] // TILE_SIZE), int(item.center[1] // TILE_SIZE))
                if lookup_pos in self.tiles:
                    self.items.pop(i)
                    continue
                item.update(self.tile_rects + lookup_nearby(self.tiles, item.center))
                if item.time > 30:
                    if item.rect.colliderect(self.player.rect):
                        if item.type == 'coin':
                            sounds['coin'].play()
                            self.coins += 1
                            for j in range(25):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 0.4
                                physics_on = random.choice([False, False, False, False, True])
                                self.sparks.append([item.center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                        else:
                            sounds['collect_item'].play()
                            for j in range(50):
                                self.sparks.append([item.center.copy(), [random.random() * 0.3 - 0.15, random.random() * 6 - 3], random.random() * 4 + 3, 0.01, (12, 8, 2), False, 0])
                            self.current_item = item.type
                        self.items.pop(i)
                        continue
                r1 = int(9 + math.sin(self.master_clock / 30) * 3)
                r2 = int(5 + math.sin(self.master_clock / 40) * 2)
                self.display.blit(glow_img(r1, (12, 8, 2)), (item.center[0] - r1 - 1, item.center[1] + self.height - r1 - 2), special_flags=BLEND_RGBA_ADD)
                self.display.blit(glow_img(r2, (24, 16, 3)), (item.center[0] - r2 - 1, item.center[1] + self.height - r2 - 2), special_flags=BLEND_RGBA_ADD)
                item.render(self.display, (0, -self.height))

        def update_player(self):
            if not self.dead:
                self.player.update(self.tile_drop_rects + self.tile_rects + lookup_nearby(self.tiles, self.player.center), self.dead)
            else:
                self.player.opacity = 80
                self.player.update([], self.dead)
                self.player.rotation -= 16
            self.player.render(self.display, (0, -int(self.height)))

        def update_sparks(self):
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

        def draw_ui(self):
            self.display.blit(border_img_light, (0, -math.sin(self.master_clock / 30) * 4 - 7))
            self.display.blit(border_img, (0, -math.sin(self.master_clock / 40) * 7 - 14))
            self.display.blit(pygame.transform.flip(border_img_light, False, True), (0, DISPLAY_SIZE[1] + math.sin(self.master_clock / 40) * 3 + 9 - border_img.get_height()))
            self.display.blit(pygame.transform.flip(border_img, False, True), (0, DISPLAY_SIZE[1] + math.sin(self.master_clock / 30) * 3 + 16 - border_img.get_height()))
            if not self.dead:
                self.display.blit(coin_icon, (4, 4))
                black_font.render(str(self.coins), self.display, (13, 6))
                white_font.render(str(self.coins), self.display, (12, 5))
                self.display.blit(item_slot_img, (DISPLAY_SIZE[0] - 20, 4))
                if self.current_item:
                    if (self.master_clock % 50 < 12) or (abs(self.master_clock % 50 - 20) < 3):
                        self.display.blit(item_slot_flash_img, (DISPLAY_SIZE[0] - 20, 4))
                    self.display.blit(item_icons[self.current_item], (DISPLAY_SIZE[0] - 15, 9))
                    if not self.item_used:
                        if (self.master_clock % 100 < 80) or (abs(self.master_clock % 100 - 90) < 3):
                            black_font.render('press E/X to use', self.display, (DISPLAY_SIZE[0] - white_font.width('press E/X to use') - 23, 10))
                            white_font.render('press E/X to use', self.display, (DISPLAY_SIZE[0] - white_font.width('press E/X to use') - 24, 9))
            else:
                black_font.render('game over', self.display, (DISPLAY_SIZE[0] // 2 - white_font.width('game over') // 2 + 1, 51))
                white_font.render('game over', self.display, (DISPLAY_SIZE[0] // 2 - white_font.width('game over') // 2, 50))
                coin_count_width = white_font.width(str(self.end_coin_count))
                self.display.blit(coin_icon, (DISPLAY_SIZE[0] // 2 - (coin_count_width + 4 + coin_icon.get_width()) // 2, 63))
                black_font.render(str(self.end_coin_count), self.display, ((DISPLAY_SIZE[0] + 5 + coin_icon.get_width()) // 2 - coin_count_width // 2, 65))
                white_font.render(str(self.end_coin_count), self.display, ((DISPLAY_SIZE[0] + 4 + coin_icon.get_width()) // 2 - coin_count_width // 2, 64))
                if self.master_clock % 3 == 0:
                    if self.end_coin_count != self.coins:
                        sounds['coin_end'].play()
                    self.end_coin_count = min(self.end_coin_count + 1, self.coins)
                if (self.master_clock % 100 < 80) or (abs(self.master_clock % 100 - 90) < 3):
                    black_font.render('press R to restart', self.display, (DISPLAY_SIZE[0] // 2 - white_font.width('press R to restart') // 2 + 1, 79))
                    white_font.render('press R to restart', self.display, (DISPLAY_SIZE[0] // 2 - white_font.width('press R to restart') // 2, 78))

        def handle_events(self):
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key in [K_RIGHT, K_d]:
                        self.player.right = True
                    if event.key in [K_LEFT, K_a]:
                        self.player.left = True
                    if event.key in [K_UP, K_w, K_SPACE]:
                        if not self.dead:
                            if self.player.jumps:
                                sounds['jump'].play()
                        self.player.attempt_jump(self.sparks, self.player)
                    if event.key in [K_e, K_x]:
                        if not self.dead:
                            if self.current_item:
                                self.item_used = True
                            if self.current_item == 'warp':
                                sounds['warp'].play()
                                max_point = min(enumerate(self.stack_heights), key=lambda x: x[1])
                                for i in range(60):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 3
                                    physics_on = random.choice([False, True])
                                    self.sparks.append([self.player.center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                                self.player.pos[0] = (max_point[0] + 1) * TILE_SIZE + 4
                                self.player.pos[1] = (max_point[1] - 1) * TILE_SIZE
                                for i in range(60):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 1.75
                                    physics_on = random.choice([False, True, True])
                                    self.sparks.append([self.player.center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                            if self.current_item == 'jump':
                                sounds['super_jump'].play()
                                self.player.jumps += 1
                                self.player.attempt_jump(self.sparks, self.player)
                                self.player.velocity[1] = -8
                                for i in range(60):
                                    angle = random.random() * math.pi / 2 + math.pi / 4
                                    if random.randint(1, 5) == 1:
                                        angle = -math.pi / 2
                                    speed = random.random() * 3
                                    physics_on = random.choice([False, True])
                                    self.sparks.append([self.player.center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                            if self.current_item == 'cube':
                                sounds['block_land'].play()
                                place_pos = (int(self.player.center[0] // TILE_SIZE), int(self.player.pos[1] // TILE_SIZE) + 1)
                                self.stack_heights[place_pos[0] - 1] = place_pos[1]
                                for i in range(place_pos[1], self.base_row + 2):
                                    self.tiles[(place_pos[0], i)] = 'placed_tile'
                                    for j in range(8):
                                        self.sparks.append([[place_pos[0] * TILE_SIZE + TILE_SIZE, i * TILE_SIZE + j * 2], [random.random() * 0.5, random.random() * 0.5 - 0.25], random.random() * 4 + 4, 0.02, (12, 8, 2), False, 0])
                                        self.sparks.append([[place_pos[0] * TILE_SIZE, i * TILE_SIZE + j * 2], [-random.random() * 0.5, random.random() * 0.5 - 0.25], random.random() * 4 + 4, 0.02, (12, 8, 2), False, 0])
                            self.current_item = None
                    if event.key == K_r:
                        if self.dead:
                            new_state = init_game_state()
                            for k in self.__dict__.keys():
                                setattr(self, k, getattr(new_state, k))
                            continue
                if event.type == KEYUP:
                    if event.key in [K_RIGHT, K_d]:
                        self.player.right = False
                    if event.key in [K_LEFT, K_a]:
                        self.player.left = False

    return GameState()


# === Main entry point ===
def main():
    setup_pygame()
    state = init_game_state()
    while True:
        display = state.display
        display.fill((22, 19, 40))
        state.master_clock += 1
        state.update_bg_particles()
        state.handle_tile_drops()
        state.draw_tiles()
        state.draw_items()
        state.update_player()
        state.update_sparks()
        state.draw_ui()
        state.handle_events()
        state.screen.blit(pygame.transform.scale(display, state.screen.get_size()), (0, 0))
        pygame.display.update()
        state.clock.tick(60) # Cap at 60 FPS


main()