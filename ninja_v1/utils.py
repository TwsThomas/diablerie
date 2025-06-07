import os
import sys
import random
import math

import pygame
from data.scripts.anim_loader import AnimationManager  # Handles loading and managing animations
from data.scripts.text import Font  # Custom bitmap font rendering

from data.scripts.entity import Entity
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

def reduce_abs(val, amt):
    """ Reduces the absolute value of `val` by `amt`, ensuring it does not exceed the bounds of -amt and amt."""
    if val > amt:
        val -= amt
    elif val < -amt:
        val += amt
    else:
        val = 0
    return val
