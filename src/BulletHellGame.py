import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Hell")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (60, 255, 60)
YELLOW = (255, 255, 100)
font = pygame.font.SysFont("Arial", 24)
bg = pygame.Surface((WIDTH, HEIGHT))
bg.fill((10, 10, 30))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (10, 10), 10)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 60))
        self.hitbox_radius = 4
        self.speed = 5
        self.cooldown = 0

    def update(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx = -self.speed
        if keys[pygame.K_RIGHT]: dx = self.speed
        if keys[pygame.K_UP]: dy = -self.speed
        if keys[pygame.K_DOWN]: dy = self.speed
        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(screen.get_rect())
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self, group):
        if self.cooldown == 0:
            bullet = Bullet(self.rect.centerx, self.rect.top, -7, "player")
            group.add(bullet)
            self.cooldown = 3

    def draw_hitbox(self, surface):
        pygame.draw.circle(surface, WHITE, self.rect.center, self.hitbox_radius, 1)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, owner):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(YELLOW if owner == "player" else RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.owner = owner

    def update(self):
        self.rect.y += self.speed
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0

    def update(self):
        self.timer += 1

    def springs_dream(self, group):
        if self.timer % 15 == 0:
            for i in range(0, 360, 30):
                angle = math.radians(i + self.timer % 360)
                vx = math.cos(angle) * 2
                vy = math.sin(angle) * 2
                bullet = Bullet(self.rect.centerx, self.rect.centery, 0, "enemy")
                bullet.vx = vx
                bullet.vy = vy
                bullet.update = lambda self=bullet: setattr(self.rect, 'x', self.rect.x + self.vx) or setattr(self.rect, 'y', self.rect.y + self.vy)
                group.add(bullet)

    def star_shower(self, group):
        if self.timer % 10 == 0:
            for i in range(3):
                x = random.randint(0, WIDTH)
                bullet = Bullet(x, 0, 3, "enemy")
                group.add(bullet)

    def timebomb(self, group):
        if self.timer % 5 == 0:
            for offset in [0, 90, 180, 270]:
                angle = (self.timer * 5 + offset) % 360
                rad = math.radians(angle)
                vx = math.cos(rad) * 2.5
                vy = math.sin(rad) * 2.5
                bullet = Bullet(self.rect.centerx, self.rect.centery, 0, "enemy")
                bullet.vx = vx
                bullet.vy = vy
                bullet.update = lambda self=bullet: setattr(self.rect, 'x', self.rect.x + self.vx) or setattr(self.rect, 'y', self.rect.y + self.vy)
                group.add(bullet)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = [pygame.Surface((10, 10), pygame.SRCALPHA) for _ in range(5)]
        for i, surf in enumerate(self.frames):
            pygame.draw.circle(surf, YELLOW, (5, 5), 5 - i)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_index = 0

    def update(self):
        self.frame_index += 1
        if self.frame_index < len(self.frames):
            self.image = self.frames[self.frame_index]
        else:
            self.kill()

def draw_score(surface):
    text = font.render(f"Lives: {lives}", True, WHITE)
    surface.blit(text, (10, HEIGHT - 30))

def draw_boss_hp(surface, hp_ratio):
    bar_width = 300
    bar_height = 15
    x = WIDTH // 2 - bar_width // 2
    y = 30
    pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)
    pygame.draw.rect(surface, RED, (x, y, bar_width * hp_ratio, bar_height))

spellcards = [
    {"duration": 1500, "pattern": "springs_dream", "hp": 100, "name": "Spring's Dream"},
    {"duration": 1500, "pattern": "star_shower", "hp": 100, "name": "Star Shower"},
    {"duration": 1500, "pattern": "timebomb", "hp": 100, "name": "Timebomb"},
]

player = Player()
enemy = Enemy(WIDTH//2, 100)
player_group = pygame.sprite.Group(player)
enemy_group = pygame.sprite.Group(enemy)
bullets_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

current_card_index = 0
card_timer = 0
current_card_hp = spellcards[0]["hp"]
phase_clear_timer = 0
spell_flash_timer = 0
lives = 3
continue_mode = False
win_mode = False

running = True
while running:
    clock.tick(FPS)
    screen.blit(bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if not continue_mode and not win_mode:
        player.update(keys)
        if keys[pygame.K_z]:
            player.shoot(bullets_group)

    if keys[pygame.K_c] and continue_mode:
        lives = 3
        continue_mode = False
        card_timer = 0
        current_card_index = 0
        current_card_hp = spellcards[0]["hp"]
        player.rect.center = (WIDTH//2, HEIGHT - 60)
        bullets_group.empty()

    if not continue_mode and not win_mode:
        enemy.update()
        card = spellcards[current_card_index]
        card_timer += 1
        if hasattr(enemy, card["pattern"]):
            getattr(enemy, card["pattern"])(bullets_group)

        bullets_group.update()
        explosion_group.update()

        for bullet in bullets_group:
            if bullet.owner == "enemy":
                dist = math.hypot(bullet.rect.centerx - player.rect.centerx, bullet.rect.centery - player.rect.centery)
                if dist < player.hitbox_radius + 3:
                    lives -= 1
                    bullet.kill()
                    bullets_group.empty()
                    player.rect.center = (WIDTH//2, HEIGHT - 60)
                    if lives <= 0:
                        continue_mode = True

            elif bullet.owner == "player":
                if enemy.rect.collidepoint(bullet.rect.center):
                    bullet.kill()
                    current_card_hp -= 1
                    explosion = Explosion(*bullet.rect.center)
                    explosion_group.add(explosion)

        if card_timer > card["duration"] or current_card_hp <= 0:
            current_card_index += 1
            if current_card_index >= len(spellcards):
                win_mode = True
            else:
                card_timer = 0
                current_card_hp = spellcards[current_card_index]["hp"]
                bullets_group.empty()

    bullets_group.draw(screen)
    explosion_group.draw(screen)
    enemy_group.draw(screen)
    player_group.draw(screen)
    player.draw_hitbox(screen)
    draw_score(screen)
    if not win_mode:
        draw_boss_hp(screen, current_card_hp / spellcards[current_card_index]["hp"])

    if continue_mode:
        text = font.render("GAME OVER", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 30))
        text = font.render("Press C to Continue", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 10))

    if win_mode:
        text = font.render("You Win!", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 10))

    pygame.display.flip()

pygame.quit()
