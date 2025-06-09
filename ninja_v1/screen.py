from constants import *
import pygame
from utils import debug, warning

def display_block(row, col, block_type: str = "block"):
    img = blocks.get(block_type)
    if img:
        display_img((LEFT_MARGIN + col * TILE_SIZE, row * TILE_SIZE), img)
    else:
        warning(f"Warning: No image found for cell '{block_type}' at ({row}, {col})")

def display_img(pos, img):
    screen.blit(img, pos)

