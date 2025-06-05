import pygame
import sys

from niveaux import generer_niveau

pygame.init()
WIDTH, HEIGHT = 1000, 400  # élargir pour la console debug
CONSOLE_WIDTH = 200

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

# Couleurs pastel et sombres
COLORS = {
    # Pastel
    "pastel_red": (255, 179, 186),
    "pastel_green": (186, 255, 201),
    "pastel_blue": (186, 225, 255),
    "pastel_yellow": (255, 255, 186),
    "pastel_purple": (218, 186, 255),
    "pastel_orange": (255, 223, 186),
    "pastel_pink": (255, 192, 203),
    # Sombres
    "dark_red": (64, 0, 0),
    "dark_green": (0, 64, 0),
    "dark_blue": (0, 0, 64),
    "dark_yellow": (64, 64, 0),
    "dark_purple": (32, 0, 64),
    "dark_orange": (102, 51, 0),
    "dark_grey": (30, 30, 30)
}

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
    platforms, enemies, enemy_direction, coins = generer_niveau(n)

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
console_font = pygame.font.SysFont(None, 22)

# Console debug
debug_logs = []

def log_debug(msg):
    debug_logs.append(str(msg))
    if len(debug_logs) > 18:
        debug_logs.pop(0)

def rainbow(i):
    color_keys = [
        "pastel_red", "pastel_orange", "pastel_yellow", "pastel_green", "pastel_blue",
        "pastel_purple", "pastel_pink"
    ]
    return color_keys[i % len(color_keys)]

# Boucle principale
while True:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if etat_jeu == "menu":
        afficher_menu()
        # if keys[pygame.K_SPACE]:
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
        if niveau > 10:
            etat_jeu = "fin"
        else:
            charger_niveau(niveau)

    # Exemple de log debug (ajoutez ce que vous voulez)
    log_debug(f"Player: x={player.x}, y={player.y}, grounded={grounded}")

    # Dessin
    screen.fill(COLORS["pastel_blue"])

    # Affichage des 20 traits verticaux numérotés
    nb_traits = 20
    espace = WIDTH // (nb_traits + 1)
    for i in range(nb_traits):
        x = (i + 1) * espace
        pygame.draw.line(screen, COLORS[rainbow(i)], (x, 0), (x, HEIGHT), 1)
        num_txt = font.render(str(i + 1), True, COLORS[rainbow(i)])
        screen.blit(num_txt, (x - num_txt.get_width() // 2, 5))

    for plat in platforms:
        pygame.draw.rect(screen, BROWN if plat.y < 360 else GREEN, plat)

    for enemy in enemies:
        pygame.draw.rect(screen, (139, 0, 0), enemy)

    pygame.draw.rect(screen, RED, player)

    for coin in coins:
        if not coin["collected"]:
            pygame.draw.circle(screen, GOLD, coin["pos"], 8)

    # Score
    txt = font.render(f"Score: {score}  -  Niveau: {niveau} / 10", True, WHITE)
    screen.blit(txt, (10, 10))

    # Affichage de la console debug à droite
    pygame.draw.rect(screen, COLORS["dark_grey"], (WIDTH - CONSOLE_WIDTH, 0, CONSOLE_WIDTH, HEIGHT))
    pygame.draw.line(screen, (0, 0, 0), (WIDTH - CONSOLE_WIDTH, 0), (WIDTH - CONSOLE_WIDTH, HEIGHT), 2)
    console_title = console_font.render("DEBUG CONSOLE", True, (255, 255, 255))
    screen.blit(console_title, (WIDTH - CONSOLE_WIDTH + 10, 10))
    for i, log in enumerate(debug_logs[-16:]):
        txt = console_font.render(log, True, (200, 200, 200))
        screen.blit(txt, (WIDTH - CONSOLE_WIDTH + 10, 35 + i * 22))

    pygame.display.flip()
    clock.tick(60)


