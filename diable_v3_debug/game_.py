import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 1000, 400
CONSOLE_WIDTH = 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Devil Level")
clock = pygame.time.Clock()

# Colors (devilish theme)
HELL_RED = (180, 0, 0)
LAVA = (255, 80, 0)
DARK = (30, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont(None, 28)
console_font = pygame.font.SysFont(None, 22)

# Player
player = pygame.Rect(100, 300, 40, 40)
player_dx = 0
player_dy = 0
player_speed = 5
jump_force = -10
gravity = 0.5
grounded = False

# Levels
niveau = 1
score = 0
etat_jeu = "menu"

# Debug console
debug_logs = []
def log(msg):
    debug_logs.append(str(msg))
    if len(debug_logs) > 18:
        debug_logs.pop(0)

def generer_niveau(n):
    platforms = [pygame.Rect(0, 360, WIDTH - CONSOLE_WIDTH, 40)]
    enemies = []
    coins = []
    spikes = []
    lava = []
    # Add platforms
    for i in range(1, n+2):
        plat = pygame.Rect(150*i, 320 - 40*i, 100, 20)
        platforms.append(plat)
        # Add spikes on some platforms
        if i % 2 == 0:
            spikes.append(pygame.Rect(plat.x + 30, plat.y - 10, 40, 10))
    # Add enemies
    for i in range(n):
        enemy = pygame.Rect(200 + i*200, 320 - 40*(i+1), 40, 40)
        enemies.append(enemy)
    # Add coins
    for i in range(n+2):
        coins.append({"pos": (170 + i*150, 320 - 40*i - 20), "collected": False})
    # Add lava pits
    for i in range(n):
        if i % 2 == 1:
            lava.append(pygame.Rect(120 + i*180, 380, 80, 20))
    return platforms, enemies, coins, spikes, lava

def charger_niveau(n):
    global platforms, enemies, coins, spikes, lava, score, player
    player.x, player.y = 100, 300
    score = 0
    platforms, enemies, coins, spikes, lava = generer_niveau(n)

def afficher_menu():
    screen.fill(HELL_RED)
    titre = font.render("DEVIL LEVEL - Press SPACE to play", True, WHITE)
    screen.blit(titre, (WIDTH // 2 - titre.get_width() // 2, HEIGHT // 2 - 30))
    pygame.display.flip()

def afficher_victoire():
    screen.fill(HELL_RED)
    msg = font.render("🔥 You conquered the Devil Levels! 🔥", True, WHITE)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 20))
    pygame.display.flip()

def afficher_defaite():
    screen.fill(DARK)
    msg = font.render("💀 Game Over! Press R to restart.", True, WHITE)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 20))
    pygame.display.flip()

# Main loop
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
            niveau = 1
            etat_jeu = "jeu"
        clock.tick(60)
        continue

    if etat_jeu == "fin":
        afficher_victoire()
        if keys[pygame.K_r]:
            etat_jeu = "menu"
        clock.tick(60)
        continue

    if etat_jeu == "mort":
        afficher_defaite()
        if keys[pygame.K_r]:
            etat_jeu = "menu"
        clock.tick(60)
        continue

    # === GAME UPDATE ===
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
                log(f"Player landed on platform at {plat}")
    # Spikes
    for spike in spikes:
        if player.colliderect(spike):
            etat_jeu = "mort"
    # Lava
    for l in lava:
        if player.colliderect(l):
            etat_jeu = "mort"
    # Enemies
    for enemy in enemies:
        enemy.x += random.choice([-2, 2])
        if enemy.left < 0 or enemy.right > WIDTH - CONSOLE_WIDTH:
            enemy.x -= random.choice([-2, 2])
        if player.colliderect(enemy):
            etat_jeu = "mort"
    # Coins
    for coin in coins:
        if not coin["collected"]:
            dist = ((player.centerx - coin["pos"][0]) ** 2 + (player.centery - coin["pos"][1]) ** 2) ** 0.5
            if dist < 30:
                coin["collected"] = True
                score += 1
                log(f"Coin collected at {coin['pos']} - Score: {score}")
    # Next level
    if all(c["collected"] for c in coins):
        niveau += 1
        if niveau > 7:
            etat_jeu = "fin"
        else:
            charger_niveau(niveau)
    # Out of bounds
    if player.top > HEIGHT:
        etat_jeu = "mort"
    # Drawing
    screen.fill(DARK)
    # Lava
    for l in lava:
        pygame.draw.rect(screen, LAVA, l)
    # Platforms
    for plat in platforms:
        pygame.draw.rect(screen, HELL_RED, plat)
    # Spikes
    for spike in spikes:
        pygame.draw.polygon(screen, WHITE, [
            (spike.x, spike.y + 10),
            (spike.x + 20, spike.y),
            (spike.x + 40, spike.y + 10)
        ])
    # Enemies
    for enemy in enemies:
        pygame.draw.rect(screen, BLACK, enemy)
        pygame.draw.circle(screen, HELL_RED, enemy.center, 10)
    # Player
    pygame.draw.rect(screen, (255, 50, 50), player)
    # Coins
    for coin in coins:
        if not coin["collected"]:
            pygame.draw.circle(screen, GOLD, coin["pos"], 8)
    # Score
    txt = font.render(f"Score: {score}  -  Level: {niveau} / 7", True, WHITE)
    screen.blit(txt, (10, 10))
    # Debug console
    pygame.draw.rect(screen, (50, 0, 0), (WIDTH - CONSOLE_WIDTH, 0, CONSOLE_WIDTH, HEIGHT))
    pygame.draw.line(screen, (0, 0, 0), (WIDTH - CONSOLE_WIDTH, 0), (WIDTH - CONSOLE_WIDTH, HEIGHT), 2)
    console_title = console_font.render("DEVIL CONSOLE", True, (255, 255, 255))
    screen.blit(console_title, (WIDTH - CONSOLE_WIDTH + 10, 10))
    for i, ll in enumerate(debug_logs[-16:]):
        txt = console_font.render(ll, True, (200, 200, 200))
        screen.blit(txt, (WIDTH - CONSOLE_WIDTH + 10, 35 + i * 22))
    pygame.display.flip()
    clock.tick(60)


