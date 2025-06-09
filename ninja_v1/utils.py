import os
import sys
import random
import math
from typing import Any, Optional, Callable

import pygame
from data.scripts.anim_loader import AnimationManager  # Handles loading and managing animations
from data.scripts.text import Font  # Custom bitmap font rendering

from constants import *

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

# Ensure the mixer is initialized before loading sounds
if not pygame.mixer.get_init():
    pygame.mixer.init()
# === Load all sound effects ===
sounds = {sound.split('/')[-1].split('.')[0] : pygame.mixer.Sound('data/sfx/' + sound) for sound in os.listdir('data/sfx')}
sounds['block_land'].set_volume(0.5)
sounds['coin'].set_volume(0.3)
sounds['chest_open'].set_volume(0.8)
sounds['coin_end'] = pygame.mixer.Sound('data/sfx/coin.wav')
sounds['coin_end'].set_volume(0.35)
sounds['warning'] = sounds['coin']

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


def debug(*args: Any) -> None:
    print("DEBUG:", *args)
    # Add the debug message to the list
    msg = " ".join(map(str, args))
    state.debug_lines.append(msg)
    # Limit the number of lines to avoid overflow
    if len(state.debug_lines) > 30:
        state.debug_lines = state.debug_lines[-30:]
    # Draw all debug lines on the left, stacked vertically
    font = pygame.font.SysFont("Arial", 10)
    for i, line in enumerate(state.debug_lines):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, TOP_MARGIN + 10 + i * 14))


def warning(*args: Any) -> None:
    """ Prints a warning message to the console and adds it to the debug lines. """
    msg = "WARNING: " + " ".join(map(str, args))
    print(msg)
    state.debug_lines.append(msg)
    if len(state.debug_lines) > 20:
        state.debug_lines = state.debug_lines[-20:]
    # Draw the warning message on the left
    font = pygame.font.SysFont("Arial", 10)
    text = font.render(msg, True, (255, 255, 0))  # Yellow for warnings
    # play a sound effect for warnings
    sounds['warning'].play()
    screen.blit(text, (10, TOP_MARGIN + 10 + len(state.debug_lines) * 14))


def error(*args: Any) -> None:
    """ Prints an error message to the console and adds it to the debug lines. """
    msg = "ERROR: " + " ".join(map(str, args))
    print(msg, file=sys.stderr)
    state.debug_lines.append(msg)
    if len(state.debug_lines) > 20:
        state.debug_lines = state.debug_lines[-20:]
    # Draw the error message on the left
    font = pygame.font.SysFont("Arial", 10)
    text = font.render(msg, True, (255, 0, 0))  # Red for errors
    # play a sound effect for errors
    sounds['warning'].play()
    screen.blit(text, (10, TOP_MARGIN + 10 + len(state.debug_lines) * 14))



def pygame_filename_input(prompt: str = "Enter filename:", default: str = "") -> str:
    """Display a simple filename input box using Pygame only. Returns the entered filename or None if cancelled."""
    font = pygame.font.SysFont("Arial", 24)
    input_box = pygame.Rect(DISPLAY_SIZE[0] // 2 - 150, DISPLAY_SIZE[1] // 2 - 25, 300, 50)
    color_inactive = colors['console_border']
    color_active = colors['star']
    color = color_inactive
    active = True
    text = default
    done = False
    clock = pygame.time.Clock()
    result = None
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    result = text.strip() if text.strip() else None
                    done = True
                elif event.key == pygame.K_ESCAPE:
                    result = None
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 32 and event.unicode.isprintable():
                        text += event.unicode
        # Draw background overlay
        overlay = pygame.Surface(DISPLAY_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 10))
        screen.blit(overlay, (0, 0))
        # Draw input box
        pygame.draw.rect(screen, color, input_box, 2)
        prompt_surf = font.render(prompt, True, colors['debug_text'])
        screen.blit(prompt_surf, (input_box.x + 10, input_box.y - 30))
        txt_surface = font.render(text, True, colors['debug_text'])
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()
        clock.tick(30)

    # display success message
    if result is not None:
        success_surf = font.render(f"Filename '{result}' saved successfully!", True, colors['gold'])
        screen.blit(success_surf, (DISPLAY_SIZE[0] // 2 - success_surf.get_width() // 2, DISPLAY_SIZE[1] // 2 + 50))
        pygame.display.flip()
        pygame.time.delay(1000)  # Show for 1 second
        pygame.quit()
        os._exit(0)
    else:
        warning("Filename input cancelled or empty.")

    return result