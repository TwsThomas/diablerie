# this is very spaghetti because it was written in under 8 hours

# === Standard library imports ===
import os
import sys
import random
import math

# === Pygame imports ===
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
        self.jumps = 2      # Remaining jumps
        self.jumps_max = 2  # Max jumps (double jump)
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

# === Main entry point ===
def main():
    setup_pygame()
    state = init_game_state()
    run_game_loop(state)


def init_game_state():
    # All game state variables in a dict for easy passing
    state = {}
    state['clock'] = pygame.time.Clock()
    state['display'] = pygame.Surface(DISPLAY_SIZE)
    state['screen'] = pygame.display.set_mode((DISPLAY_SIZE[0] * 3, DISPLAY_SIZE[1] * 3), 0, 32)
    state['animation_manager'] = animation_manager
    state['player'] = Player(animation_manager, (DISPLAY_SIZE[0] // 2 - 5, -20), (8, 16), 'player')
    state['dead'] = False
    state['tiles'] = {}
    state['tile_drops'] = []
    state['bg_particles'] = []
    state['sparks'] = []
    state['game_timer'] = 0
    state['height'] = 0
    state['target_height'] = 0
    state['coins'] = 0
    state['end_coin_count'] = 0
    state['current_item'] = None
    state['master_clock'] = 0
    state['last_place'] = 0
    state['item_used'] = False
    state['items'] = []
    state['stack_heights'] = [WINDOW_TILE_SIZE[1] - 1 for _ in range(WINDOW_TILE_SIZE[0] - 2)]
    state['stack_heights'][0] -= 1
    state['stack_heights'][-1] -= 1
    state['tile_drop_rects'] = []  # Initialize as empty list for safety
    state['tile_rects'] = []  # Ensure always present
    state['base_row'] = 0      # Ensure always present
    # Initial tile setup
    for i in range(WINDOW_TILE_SIZE[0] - 2):
        state['tiles'][(i + 1, WINDOW_TILE_SIZE[1] - 1)] = 'tile'
    state['tiles'][(1, WINDOW_TILE_SIZE[1] - 2)] = 'tile'
    state['tiles'][(WINDOW_TILE_SIZE[0] - 2, WINDOW_TILE_SIZE[1] - 2)] = 'tile'
    # Music
    pygame.mixer.music.load('data/music.wav')
    pygame.mixer.music.play(-1)
    return state

def run_game_loop(state):
    while True:
        handle_frame(state)

def handle_frame(state):
    display = state['display']
    display.fill((22, 19, 40))
    state['master_clock'] += 1
    update_bg_particles(state)
    handle_tile_drops(state)
    draw_tiles(state)
    draw_items(state)
    update_player(state)
    update_sparks(state)
    draw_ui(state)
    handle_events(state)
    state['screen'].blit(pygame.transform.scale(display, state['screen'].get_size()), (0, 0))
    pygame.display.update()
    state['clock'].tick(60)

def update_bg_particles(state):
    display = state['display']
    parallax = random.random()
    for _ in range(2):
        state['bg_particles'].append([[random.random() * DISPLAY_SIZE[0], DISPLAY_SIZE[1] - state['height'] * parallax], parallax, random.randint(1, 8), random.random() * 1 + 1, random.choice([(0, 0, 0), (22, 19, 40)])])
    for i, p in sorted(enumerate(state['bg_particles']), reverse=True):
        size = p[2]
        if p[-1] != (0, 0, 0):
            size = size * 5 + 4
        p[2] -= 0.01
        p[0][1] -= p[3]
        if size < 1:
            display.set_at((int(p[0][0]), int(p[0][1] + state['height'] * p[1])), (0, 0, 0))
        else:
            if p[-1] != (0, 0, 0):
                pygame.draw.circle(display, p[-1], p[0], int(size), 4)
            else:
                pygame.draw.circle(display, p[-1], p[0], int(size))
        if size < 0:
            state['bg_particles'].pop(i)

def handle_tile_drops(state):
    if state['master_clock'] > 180:
        state['game_timer'] += 1
        if state['game_timer'] > 10 + 25 * (20000 - min(20000, state['master_clock'])) / 20000:
            state['game_timer'] = 0
            minimum = min(state['stack_heights'])
            options = []
            for i, stack in enumerate(state['stack_heights']):
                if i != state['last_place']:
                    offset = stack - minimum
                    for j in range(int(offset ** (2.2 - min(20000, state['master_clock']) / 10000)) + 1):
                        options.append(i)

            tile_type = 'tile'
            if random.randint(1, 10) == 1:
                tile_type = 'chest'
            c = random.choice(options)
            state['last_place'] = c
            state['tile_drops'].append([(c + 1) * TILE_SIZE, -state['height'] - TILE_SIZE, tile_type])

    # === Update and draw falling tiles ===
    tile_drop_rects = []
    for i, tile in sorted(enumerate(state['tile_drops']), reverse=True):
        tile[1] += 1.4  # Gravity
        pos = [tile[0] + TILE_SIZE // 2, tile[1] + TILE_SIZE]
        r = pygame.Rect(tile[0], tile[1], TILE_SIZE, TILE_SIZE)
        tile_drop_rects.append(r)

        # === Player dies if hit by falling tile ===
        if r.colliderect(state['player'].rect):
            if not state['dead']:
                sounds['death'].play()
                state['player'].velocity = [1.3, -6]
                for i in range(380):
                    angle = random.random() * math.pi
                    speed = random.random() * 1.5
                    physics_on = random.choice([False, True, True])
                    state['sparks'].append([state['player'].center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 2, 2), physics_on, 0.1 * physics_on])
            state['dead'] = True

        check_pos = (int(pos[0] // TILE_SIZE), int(math.floor(pos[1] / TILE_SIZE)))
        if check_pos in state['tiles']:
            state['tile_drops'].pop(i)
            place_pos = (check_pos[0], check_pos[1] - 1)
            state['stack_heights'][place_pos[0] - 1] = place_pos[1]
            state['tiles'][place_pos] = tile[2]
            sounds['block_land'].play()
            if state['tiles'][check_pos] == 'chest':
                state['tiles'][check_pos] = 'tile'
                sounds['chest_destroy'].play()
                for i in range(100):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 2.5
                    state['sparks'].append([[place_pos[0] * TILE_SIZE + TILE_SIZE // 2, place_pos[1] * TILE_SIZE + TILE_SIZE // 2], [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.09, (12, 8, 2), False, 0.1])
            continue
        if random.randint(1, 4) == 1:
            side = random.choice([1, -1])
            state['sparks'].append([[tile[0] + TILE_SIZE * (side == 1), tile[1]], [random.random() * 0.1 - 0.05, random.random() * 0.5], random.random() * 5 + 3, 0.15, (4, 2, 12), False, 0])
        state['display'].blit(tile_img, (tile[0], tile[1] + state['height']))
        if tile[2] == 'chest':
            state['display'].blit(ghost_chest_img, (tile[0], tile[1] + state['height'] - TILE_SIZE))

    state['tile_drop_rects'] = tile_drop_rects

def draw_tiles(state):
    # === Draw all placed tiles and chests ===
    state['tile_rects'] = []
    for tile in state['tiles']:
        state['display'].blit(tile_img, (TILE_SIZE * tile[0], TILE_SIZE * tile[1] + int(state['height'])))
        if state['tiles'][tile] == 'placed_tile':
            state['display'].blit(placed_tile_img, (TILE_SIZE * tile[0], TILE_SIZE * tile[1] + int(state['height'])))
        if state['tiles'][tile] == 'chest':
            state['display'].blit(chest_img, (TILE_SIZE * tile[0], TILE_SIZE * (tile[1] - 1) + int(state['height'])))
            chest_r = pygame.Rect(TILE_SIZE * tile[0] + 2, TILE_SIZE * (tile[1] - 1) + 6, TILE_SIZE - 4, TILE_SIZE - 6)
            if random.randint(1, 20) == 1:
                state['sparks'].append([[tile[0] * TILE_SIZE + 2 + 12 * random.random(), (tile[1] - 1) * TILE_SIZE + 4 + 8 * random.random()], [0, random.random() * 0.25 - 0.5], random.random() * 4 + 2, 0.023, (12, 8, 2), True, 0.002])
            if chest_r.colliderect(state['player'].rect):
                sounds['chest_open'].play()
                for i in range(50):
                    state['sparks'].append([[tile[0] * TILE_SIZE + 8, (tile[1] - 1) * TILE_SIZE + 8], [random.random() * 2 - 1, random.random() - 2], random.random() * 3 + 3, 0.01, (12, 8, 2), True, 0.05])
                state['tiles'][tile] = 'opened_chest'
                state['player'].jumps += 1
                state['player'].attempt_jump(state['sparks'], state['player'])
                state['player'].velocity[1] = -3.5
                if random.randint(1, 5) < 3:
                    state['items'].append(Item(animation_manager, (tile[0] * TILE_SIZE + 5, (tile[1] - 1) * TILE_SIZE + 5), (6, 6), random.choice(['warp', 'cube', 'jump']), velocity=[random.random() * 5 - 2.5, random.random() * 2 - 5]))
                else:
                    for i in range(random.randint(2, 6)):
                        state['items'].append(Item(animation_manager, (tile[0] * TILE_SIZE + 5, (tile[1] - 1) * TILE_SIZE + 5), (6, 6), 'coin', velocity=[random.random() * 5 - 2.5, random.random() * 2 - 7]))
        elif state['tiles'][tile] == 'opened_chest':
            state['display'].blit(opened_chest_img, (TILE_SIZE * tile[0], TILE_SIZE * (tile[1] - 1) + int(state['height'])))

    # === Check if row is filled to clear and scroll up ===
    base_row = max(state['tiles'], key=lambda x: x[1])[1] - 1
    filled = True
    for i in range(WINDOW_TILE_SIZE[0] - 2):
        if (i + 1, base_row) not in state['tiles']:
            filled = False
    if filled:
        state['target_height'] = math.floor(state['height'] / TILE_SIZE) * TILE_SIZE + TILE_SIZE

    if state['height'] != state['target_height']:
        state['height'] += (state['target_height'] - state['height']) / 10
        if abs(state['target_height'] - state['height']) < 0.2:
            state['height'] = state['target_height']
            for i in range(WINDOW_TILE_SIZE[0] - 2):
                del state['tiles'][(i + 1, base_row + 1)]

    # === Draw edge tiles (left/right borders) ===
    for i in range(WINDOW_TILE_SIZE[1] + 2):
        pos_y = (-state['height'] // 16) - 1 + i
        state['display'].blit(edge_tile_img, (0, TILE_SIZE * pos_y + int(state['height'])))
        state['display'].blit(edge_tile_img, (TILE_SIZE * (WINDOW_TILE_SIZE[0] - 1), TILE_SIZE * pos_y + int(state['height'])))

    state['tile_rects'].append(pygame.Rect(0, state['player'].pos[1] - 300, TILE_SIZE, 600))
    state['tile_rects'].append(pygame.Rect(TILE_SIZE * (WINDOW_TILE_SIZE[0] - 1), state['player'].pos[1] - 300, TILE_SIZE, 600))
    state['base_row'] = base_row

def draw_items(state):
    # === Update and draw all items ===
    for i, item in sorted(enumerate(state['items']), reverse=True):
        lookup_pos = (int(item.center[0] // TILE_SIZE), int(item.center[1] // TILE_SIZE))
        if lookup_pos in state['tiles']:
            state['items'].pop(i)
            continue
        item.update(state['tile_rects'] + lookup_nearby(state['tiles'], item.center))
        if item.time > 30:
            if item.rect.colliderect(state['player'].rect):
                if item.type == 'coin':
                    sounds['coin'].play()
                    state['coins'] += 1
                    for j in range(25):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 0.4
                        physics_on = random.choice([False, False, False, False, True])
                        state['sparks'].append([item.center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                else:
                    sounds['collect_item'].play()
                    for j in range(50):
                        state['sparks'].append([item.center.copy(), [random.random() * 0.3 - 0.15, random.random() * 6 - 3], random.random() * 4 + 3, 0.01, (12, 8, 2), False, 0])
                    state['current_item'] = item.type
                state['items'].pop(i)
                continue
        r1 = int(9 + math.sin(state['master_clock'] / 30) * 3)
        r2 = int(5 + math.sin(state['master_clock'] / 40) * 2)
        state['display'].blit(glow_img(r1, (12, 8, 2)), (item.center[0] - r1 - 1, item.center[1] + state['height'] - r1 - 2), special_flags=BLEND_RGBA_ADD)
        state['display'].blit(glow_img(r2, (24, 16, 3)), (item.center[0] - r2 - 1, item.center[1] + state['height'] - r2 - 2), special_flags=BLEND_RGBA_ADD)
        item.render(state['display'], (0, -state['height']))

def update_player(state):
    # === Update player ===
    if not state['dead']:
        state['player'].update(state['tile_drop_rects'] + state['tile_rects'] + lookup_nearby(state['tiles'], state['player'].center), state['dead'])
    else:
        state['player'].opacity = 80
        state['player'].update([], state['dead'])
        state['player'].rotation -= 16
    state['player'].render(state['display'], (0, -int(state['height'])))

def update_sparks(state):
    # === Update and draw all sparks (particles) ===
    for i, spark in sorted(enumerate(state['sparks']), reverse=True):
        # pos, vel, size, decay, color, physics, gravity, dead
        if len(spark) < 8:
            spark.append(False)
        if not spark[-1]:
            spark[1][1] = min(spark[1][1] + spark[-2], 3)
        spark[0][0] += spark[1][0]
        if spark[5]:
            if ((int(spark[0][0] // TILE_SIZE), int(spark[0][1] // TILE_SIZE)) in state['tiles']) or (spark[0][0] < TILE_SIZE) or (spark[0][0] > DISPLAY_SIZE[0] - TILE_SIZE):
                spark[0][0] -= spark[1][0]
                spark[1][0] *= -0.7
        spark[0][1] += spark[1][1]
        if spark[5]:
            if (int(spark[0][0] // TILE_SIZE), int(spark[0][1] // TILE_SIZE)) in state['tiles']:
                spark[0][1] -= spark[1][1]
                spark[1][1] *= -0.7
                if abs(spark[1][1]) < 0.1:
                    spark[1][1] = 0
                    spark[-1] = True
        #if spark[-2]:
        #    spark[1][0] = normalize(spark[1][0], 0.03)
        spark[2] -= spark[3]
        if spark[2] <= 1:
            state['sparks'].pop(i)
        else:
            state['display'].blit(glow_img(int(spark[2] * 1.5 + 2), (int(spark[4][0] / 2), int(spark[4][1] / 2), int(spark[4][2] / 2))), (spark[0][0] - spark[2] * 2, spark[0][1] + state['height'] - spark[2] * 2), special_flags=BLEND_RGBA_ADD)
            state['display'].blit(glow_img(int(spark[2]), spark[4]), (spark[0][0] - spark[2], spark[0][1] + state['height'] - spark[2]), special_flags=BLEND_RGBA_ADD)

def draw_ui(state):
    # === Draw UI borders ===
    state['display'].blit(border_img_light, (0, -math.sin(state['master_clock'] / 30) * 4 - 7))
    state['display'].blit(border_img, (0, -math.sin(state['master_clock'] / 40) * 7 - 14))
    state['display'].blit(pygame.transform.flip(border_img_light, False, True), (0, DISPLAY_SIZE[1] + math.sin(state['master_clock'] / 40) * 3 + 9 - border_img.get_height()))
    state['display'].blit(pygame.transform.flip(border_img, False, True), (0, DISPLAY_SIZE[1] + math.sin(state['master_clock'] / 30) * 3 + 16 - border_img.get_height()))

    # === UI: coin counter, item slot, game over screen ===
    if not state['dead']:
        state['display'].blit(coin_icon, (4, 4))
        black_font.render(str(state['coins']), state['display'], (13, 6))
        white_font.render(str(state['coins']), state['display'], (12, 5))

        state['display'].blit(item_slot_img, (DISPLAY_SIZE[0] - 20, 4))
        if state['current_item']:
            if (state['master_clock'] % 50 < 12) or (abs(state['master_clock'] % 50 - 20) < 3):
                state['display'].blit(item_slot_flash_img, (DISPLAY_SIZE[0] - 20, 4))
            state['display'].blit(item_icons[state['current_item']], (DISPLAY_SIZE[0] - 15, 9))
            if not state['item_used']:
                if (state['master_clock'] % 100 < 80) or (abs(state['master_clock'] % 100 - 90) < 3):
                    black_font.render('press E/X to use', state['display'], (DISPLAY_SIZE[0] - white_font.width('press E/X to use') - 23, 10))
                    white_font.render('press E/X to use', state['display'], (DISPLAY_SIZE[0] - white_font.width('press E/X to use') - 24, 9))
    else:
        black_font.render('game over', state['display'], (DISPLAY_SIZE[0] // 2 - white_font.width('game over') // 2 + 1, 51))
        white_font.render('game over', state['display'], (DISPLAY_SIZE[0] // 2 - white_font.width('game over') // 2, 50))
        coin_count_width = white_font.width(str(state['end_coin_count']))
        state['display'].blit(coin_icon, (DISPLAY_SIZE[0] // 2 - (coin_count_width + 4 + coin_icon.get_width()) // 2, 63))
        black_font.render(str(state['end_coin_count']), state['display'], ((DISPLAY_SIZE[0] + 5 + coin_icon.get_width()) // 2 - coin_count_width // 2, 65))
        white_font.render(str(state['end_coin_count']), state['display'], ((DISPLAY_SIZE[0] + 4 + coin_icon.get_width()) // 2 - coin_count_width // 2, 64))
        if state['master_clock'] % 3 == 0:
            if state['end_coin_count'] != state['coins']:
                sounds['coin_end'].play()
            state['end_coin_count'] = min(state['end_coin_count'] + 1, state['coins'])
        if (state['master_clock'] % 100 < 80) or (abs(state['master_clock'] % 100 - 90) < 3):
            black_font.render('press R to restart', state['display'], (DISPLAY_SIZE[0] // 2 - white_font.width('press R to restart') // 2 + 1, 79))
            white_font.render('press R to restart', state['display'], (DISPLAY_SIZE[0] // 2 - white_font.width('press R to restart') // 2, 78))

def handle_events(state):
    # === Handle all events (keyboard, quit, etc.) ===
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key in [K_RIGHT, K_d]:
                state['player'].right = True
            if event.key in [K_LEFT, K_a]:
                state['player'].left = True
            if event.key in [K_UP, K_w, K_SPACE]:
                if not state['dead']:
                    if state['player'].jumps:
                        sounds['jump'].play()
                    state['player'].attempt_jump(state['sparks'], state['player'])
            if event.key in [K_e, K_x]:
                if not state['dead']:
                    if state['current_item']:
                        state['item_used'] = True
                    if state['current_item'] == 'warp':
                        sounds['warp'].play()
                        max_point = min(enumerate(state['stack_heights']), key=lambda x: x[1])
                        for i in range(60):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 3
                            physics_on = random.choice([False, True])
                            state['sparks'].append([state['player'].center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                        state['player'].pos[0] = (max_point[0] + 1) * TILE_SIZE + 4
                        state['player'].pos[1] = (max_point[1] - 1) * TILE_SIZE
                        for i in range(60):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 1.75
                            physics_on = random.choice([False, True, True])
                            state['sparks'].append([state['player'].center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                    if state['current_item'] == 'jump':
                        sounds['super_jump'].play()
                        state['player'].jumps += 1
                        state['player'].attempt_jump(state['sparks'], state['player'])
                        state['player'].velocity[1] = -8
                        for i in range(60):
                            angle = random.random() * math.pi / 2 + math.pi / 4
                            if random.randint(1, 5) == 1:
                                angle = -math.pi / 2
                            speed = random.random() * 3
                            physics_on = random.choice([False, True])
                            state['sparks'].append([state['player'].center.copy(), [math.cos(angle) * speed, math.sin(angle) * speed], random.random() * 3 + 3, 0.02, (12, 8, 2), physics_on, 0.1 * physics_on])
                    if state['current_item'] == 'cube':
                        sounds['block_land'].play()
                        place_pos = (int(state['player'].center[0] // TILE_SIZE), int(state['player'].pos[1] // TILE_SIZE) + 1)
                        state['stack_heights'][place_pos[0] - 1] = place_pos[1]
                        for i in range(place_pos[1], state['base_row'] + 2):
                            state['tiles'][(place_pos[0], i)] = 'placed_tile'
                            for j in range(8):
                                state['sparks'].append([[place_pos[0] * TILE_SIZE + TILE_SIZE, i * TILE_SIZE + j * 2], [random.random() * 0.5, random.random() * 0.5 - 0.25], random.random() * 4 + 4, 0.02, (12, 8, 2), False, 0])
                                state['sparks'].append([[place_pos[0] * TILE_SIZE, i * TILE_SIZE + j * 2], [-random.random() * 0.5, random.random() * 0.5 - 0.25], random.random() * 4 + 4, 0.02, (12, 8, 2), False, 0])
                    state['current_item'] = None
            if event.key == K_r:
                if state['dead']:
                    # === Reset all game state for restart ===
                    new_state = init_game_state()
                    for k in state.keys():
                        state[k] = new_state[k]
                    continue
        if event.type == KEYUP:
            if event.key in [K_RIGHT, K_d]:
                state['player'].right = False
            if event.key in [K_LEFT, K_a]:
                state['player'].left = False


main()