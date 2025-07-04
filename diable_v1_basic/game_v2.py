import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plateformer avec Niveaux")
clock = pygame.time.Clock()

# Couleurs
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BROWN = (150, 75, 0)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)

# Joueur
player = pygame.Rect(100, 300, 40, 40)
player_dx = 0
player_dy = 0
player_speed = 5
jump_force = -10
gravity = 0.5
grounded = False

# Niveaux
niveau = 1
score = 0
etat_jeu = "menu"

def charger_niveau(n):
    global platforms, enemies, enemy_direction, coins, score, player
    player.x, player.y = 100, 300
    score = 0

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

def afficher_menu():
    screen.fill(BLUE)
    titre = font.render("Plateformer - Appuie sur ESPACE pour jouer", True, WHITE)
    screen.blit(titre, (WIDTH // 2 - titre.get_width() // 2, HEIGHT // 2 - 30))
    pygame.display.flip()

def afficher_victoire():
    screen.fill(BLUE)
    msg = font.render("🎉 Bravo ! Tu as terminé les niveaux !", True, WHITE)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 20))
    pygame.display.flip()

font = pygame.font.SysFont(None, 28)

# Boucle principale
while True:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if etat_jeu == "menu":
        afficher_menu()
        if keys[pygame.K_SPACE]:
            charger_niveau(1)
            etat_jeu = "jeu"
        clock.tick(60)
        continue

    if etat_jeu == "fin":
        afficher_victoire()
        if keys[pygame.K_r]:
            niveau = 1
            etat_jeu = "menu"
        clock.tick(60)
        continue

    # === MISE À JOUR DU JEU ===
    if keys[pygame.K_LEFT]:
        player_dx = -player_speed
    elif keys[pygame.K_RIGHT]:
        player_dx = player_speed
    else:
        player_dx = 0

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

    # Ennemis
    for i, enemy in enumerate(enemies):
        enemy.x += enemy_direction[i]
        if enemy.left < 100 or enemy.right > WIDTH - 100:
            enemy_direction[i] *= -1
        if player.colliderect(enemy):
            etat_jeu = "menu"

    # Pièces
    for coin in coins:
        if not coin["collected"]:
            dist = ((player.centerx - coin["pos"][0]) ** 2 + (player.centery - coin["pos"][1]) ** 2) ** 0.5
            if dist < 30:
                coin["collected"] = True
                score += 1

    # Changer de niveau
    if all(c["collected"] for c in coins):
        niveau += 1
        if niveau > 2:
            etat_jeu = "fin"
        else:
            charger_niveau(niveau)

    # Dessin
    screen.fill((135, 206, 235))
    for plat in platforms:
        pygame.draw.rect(screen, BROWN if plat.y < 360 else GREEN, plat)

    for enemy in enemies:
        pygame.draw.rect(screen, (139, 0, 0), enemy)

    pygame.draw.rect(screen, RED, player)

    for coin in coins:
        if not coin["collected"]:
            pygame.draw.circle(screen, GOLD, coin["pos"], 8)

    # Score
    txt = font.render(f"Score: {score}  -  Niveau: {niveau}", True, WHITE)
    screen.blit(txt, (10, 10))

    pygame.display.flip()
    clock.tick(60)
