import pygame
import sys

# Initialisation
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plateformer Simple")
clock = pygame.time.Clock()

# Couleurs
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
BROWN = (150, 75, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)

# Joueur
player = pygame.Rect(100, 300, 40, 40)
player_dx = 0
player_dy = 0
player_speed = 5
jump_force = -10
gravity = 0.5
grounded = False

# Plateformes
platforms = [
    pygame.Rect(0, 360, WIDTH, 40),
    pygame.Rect(200, 280, 100, 20),
    pygame.Rect(400, 200, 100, 20),
    pygame.Rect(600, 250, 100, 20)
]

# Ennemis
enemies = [
    pygame.Rect(500, 320, 40, 40)
]
enemy_direction = [2]

# Pièces
coins = [
    {"pos": (220, 240), "collected": False},
    {"pos": (420, 160), "collected": False},
    {"pos": (620, 210), "collected": False}
]

score = 0

# Boucle principale
running = True
while running:
    screen.fill((135, 206, 235))  # ciel bleu
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mouvement joueur
    player_dx = 0
    if keys[pygame.K_LEFT]:
        player_dx = -player_speed
    if keys[pygame.K_RIGHT]:
        player_dx = player_speed
    if keys[pygame.K_SPACE] and grounded:
        player_dy = jump_force
        grounded = False

    player.x += player_dx
    player_dy += gravity
    player.y += player_dy

    grounded = False
    for plat in platforms:
        if player.colliderect(plat) and player_dy >= 0:
            if player.bottom >= plat.top and player.bottom <= plat.top + 20:
                player.bottom = plat.top
                player_dy = 0
                grounded = True

    # Collision avec les bords
    if player.left < 0:
        player.left = 0
    if player.right > WIDTH:
        player.right = WIDTH

    # Ennemis
    for i, enemy in enumerate(enemies):
        enemy.x += enemy_direction[i]
        if enemy.left < 400 or enemy.right > 760:
            enemy_direction[i] *= -1
        if player.colliderect(enemy):
            print("💀 Game Over!")
            # restart le jeu
            player.x, player.y = 100, 300
            player_dy = 0
            score = 0
            for coin in coins:
                coin["collected"] = False
            for enemy in enemies:
                enemy.x = 500
                enemy_direction[i] = 2
            continue
            
    # Pièces
    for coin in coins:
        if not coin["collected"]:
            dist = ((player.centerx - coin["pos"][0]) ** 2 + (player.centery - coin["pos"][1]) ** 2) ** 0.5
            if dist < 30:
                coin["collected"] = True
                score += 1

    # Dessin
    for plat in platforms:
        pygame.draw.rect(screen, BROWN if plat.y < 360 else GREEN, plat)

    pygame.draw.rect(screen, RED, player)

    for enemy in enemies:
        pygame.draw.rect(screen, (139, 0, 0), enemy)

    for coin in coins:
        if not coin["collected"]:
            pygame.draw.circle(screen, GOLD, coin["pos"], 8)

    # Score
    font = pygame.font.SysFont(None, 28)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
