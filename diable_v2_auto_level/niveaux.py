import pygame
import random

WIDTH, HEIGHT = 800, 400

def first_niveaux(n):

    if n == 1:
        platforms = [
            pygame.Rect(0, 360, WIDTH, 40),
            pygame.Rect(200, 280, 100, 20),
            pygame.Rect(400, 200, 100, 20),
            pygame.Rect(600, 250, 100, 20)
        ]
        enemies = [pygame.Rect(500, 320, 40, 40)]
        enemy_direction = [2]
        coins = [
            {"pos": (220, 240), "collected": False},
            {"pos": (420, 160), "collected": False},
            {"pos": (620, 210), "collected": False}
        ]
    elif n == 2:
        platforms = [
            pygame.Rect(0, 360, WIDTH, 40),
            pygame.Rect(150, 300, 80, 20),
            pygame.Rect(350, 250, 80, 20),
            pygame.Rect(550, 200, 80, 20)
        ]
        enemies = [pygame.Rect(400, 320, 40, 40), pygame.Rect(600, 320, 40, 40)]
        enemy_direction = [2, -2]
        coins = [
            {"pos": (170, 260), "collected": False},
            {"pos": (370, 210), "collected": False},
            {"pos": (570, 160), "collected": False}
        ]

    return platforms, enemies, enemy_direction, coins

def generer_niveau(n):

    if n < 3: # first level are hardcoded
        return first_niveaux(n)
    
    hauteur_base = 360
    ecart = max(120 - n * 5, 60)  # les plateformes se rapprochent à mesure que n augmente

    # Génération des plateformes
    platforms = [pygame.Rect(0, hauteur_base, WIDTH, 40)]
    for i in range(1, 5):
        x = i * 150 + random.randint(-20, 20)
        y = hauteur_base - i * 40 - random.randint(0, 30)
        platforms.append(pygame.Rect(x, y, 100, 20))

    # Génération des ennemis (+1 ennemi tous les 2 niveaux)
    enemies = []
    enemy_direction = []
    for i in range(n // 2 + 1):
        x = 250 + i * 200
        enemy = pygame.Rect(x, 320, 40, 40)
        enemies.append(enemy)
        enemy_direction.append(random.choice([-2, 2]))

    # Génération des pièces
    coins = []
    for plat in platforms[1:]:
        x = plat.x + plat.width // 2
        y = plat.y - 20
        coins.append({"pos": (x, y), "collected": False})

    return platforms, enemies, enemy_direction, coins
