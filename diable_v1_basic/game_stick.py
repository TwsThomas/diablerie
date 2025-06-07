import pygame
import sys

# Initialisation
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Stickman (dessiné à la main)
class Stickman(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = [self.draw_frame1(), self.draw_frame2()]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.vel_y = 0
        self.on_ground = True
        self.alive = True
        self.frame_counter = 0

    def draw_frame1(self):
        surf = pygame.Surface((40, 80), pygame.SRCALPHA)
        pygame.draw.circle(surf, BLACK, (20, 10), 10)  # tête
        pygame.draw.line(surf, BLACK, (20, 20), (20, 50), 2)  # corps
        pygame.draw.line(surf, BLACK, (20, 30), (5, 40), 2)  # bras gauche
        pygame.draw.line(surf, BLACK, (20, 30), (35, 40), 2)  # bras droit
        pygame.draw.line(surf, BLACK, (20, 50), (10, 70), 2)  # jambe gauche
        pygame.draw.line(surf, BLACK, (20, 50), (30, 70), 2)  # jambe droite
        return surf

    def draw_frame2(self):
        surf = pygame.Surface((40, 80), pygame.SRCALPHA)
        pygame.draw.circle(surf, BLACK, (20, 10), 10)
        pygame.draw.line(surf, BLACK, (20, 20), (20, 50), 2)
        pygame.draw.line(surf, BLACK, (20, 30), (10, 40), 2)
        pygame.draw.line(surf, BLACK, (20, 30), (30, 40), 2)
        pygame.draw.line(surf, BLACK, (20, 50), (25, 70), 2)
        pygame.draw.line(surf, BLACK, (20, 50), (15, 70), 2)
        return surf

    def update(self, keys):
        if not self.alive:
            return

        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5

        self.rect.x += dx

        # Animation
        if dx != 0:
            self.frame_counter += 1
            if self.frame_counter >= 10:
                self.frame_counter = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]

        # Gravité
        self.vel_y += 1
        self.rect.y += self.vel_y

        # Sol
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def jump(self):
        if self.on_ground and self.alive:
            self.vel_y = -20

    def explode(self):
        self.alive = False
        self.image.fill(RED)

# Ennemi simple
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))

# Groupes
player = Stickman(100, HEIGHT - 100)
enemy = Enemy(400, HEIGHT - 90)
all_sprites = pygame.sprite.Group(player, enemy)
enemies = pygame.sprite.Group(enemy)

# Boucle principale
running = True
while running:
    clock.tick(60) # means 
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()

    # Mise à jour
    all_sprites.update(keys)

    # Collisions
    if pygame.sprite.spritecollide(player, enemies, False):
        player.explode()

    # Affichage
    screen.fill(WHITE)
    all_sprites.draw(screen)
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - 50, WIDTH, 50))  # sol
    pygame.display.flip()

pygame.quit()
sys.exit()
