__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so
*.egg-info/
.venv/
venv/
env/
.pytest_cache/
.mypy_cache/
.DS_Store
Thumbs.db
.vscode/
.idea/
.godot/
.import/
export_presets.cfg
*.tmp
 """
ForgeRoyale - Prototype Pygame
Copyright (c) 2026 Amine Medouar
"""

import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ForgeRoyale")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)

WORLD_W, WORLD_H = 2200, 1400
PLAYER_SPEED = 280
BULLET_SPEED = 700

def clamp(v, a, b):
    return max(a, min(b, v))

class Player:
    def __init__(self):
        self.x = WORLD_W // 2
        self.y = WORLD_H // 2
        self.r = 16
        self.hp = 100
        self.wood = 8
        self.stone = 4
        self.cooldown = 0.0

    def move(self, dt, keys):
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_q] or keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP])
        l = math.hypot(dx, dy)
        if l > 0:
            dx /= l
            dy /= l
        self.x += dx * PLAYER_SPEED * dt
        self.y += dy * PLAYER_SPEED * dt
        self.x = clamp(self.x, 0, WORLD_W)
        self.y = clamp(self.y, 0, WORLD_H)
        self.cooldown -= dt

class Enemy:
    def __init__(self):
        self.x = random.randint(100, WORLD_W - 100)
        self.y = random.randint(100, WORLD_H - 100)
        self.hp = 60
        self.r = 12
        self.speed = random.uniform(90, 130)

class Bullet:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = 1.2
        self.r = 4

player = Player()
enemies = [Enemy() for _ in range(10)]
bullets = []
zone_center = (WORLD_W // 2, WORLD_H // 2)
zone_radius = 420
zone_timer = 0
game_over = False

running = True
while running:
    dt = clock.tick(60) / 1000
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False

    if not game_over:
        keys = pygame.key.get_pressed()
        player.move(dt, keys)

        # Tir
        if pygame.mouse.get_pressed()[0] and player.cooldown <= 0:
            mx, my = pygame.mouse.get_pos()
            camx = player.x - WIDTH / 2
            camy = player.y - HEIGHT / 2
            wx, wy = mx + camx, my + camy
            dx, dy = wx - player.x, wy - player.y
            l = math.hypot(dx, dy) + 1e-6
            bullets.append(Bullet(player.x, player.y, dx / l * BULLET_SPEED, dy / l * BULLET_SPEED))
            player.cooldown = 0.14

        # Build
        if keys[pygame.K_e] and player.wood >= 5 and player.stone >= 2:
            player.wood -= 5
            player.stone -= 2

        # Harvest
        if keys[pygame.K_r]:
            player.wood += 1 if random.random() < 0.05 else 0
            player.stone += 1 if random.random() < 0.03 else 0

        # Zone
        zone_timer += dt
        if zone_timer > 4.5:
            zone_radius = max(140, zone_radius - 18)
            zone_timer = 0
        if math.hypot(player.x - zone_center[0], player.y - zone_center[1]) > zone_radius:
            player.hp -= int(8 * dt + 0.6)

        # Ennemis
        for en in enemies:
            dx, dy = player.x - en.x, player.y - en.y
            l = math.hypot(dx, dy) + 1e-6
            en.x += dx / l * en.speed * dt
            en.y += dy / l * en.speed * dt
            if math.hypot(player.x - en.x, player.y - en.y) < player.r + en.r:
                player.hp -= int(10 * dt + 0.6)

        # Bullets
        alive_b = []
        for b in bullets:
            b.x += b.vx * dt
            b.y += b.vy * dt
            b.life -= dt
            hit = False
            for en in enemies:
                if en.hp > 0 and math.hypot(b.x - en.x, b.y - en.y) < b.r + en.r:
                    en.hp -= 20
                    hit = True
                    break
            if b.life > 0 and not hit:
                alive_b.append(b)
        bullets = alive_b
        enemies = [en for en in enemies if en.hp > 0]

        if player.hp <= 0:
            player.hp = 0
            game_over = True

    camx = clamp(player.x - WIDTH / 2, 0, WORLD_W - WIDTH)
    camy = clamp(player.y - HEIGHT / 2, 0, WORLD_H - HEIGHT)

    screen.fill((33, 42, 50))
    pygame.draw.circle(screen, (100, 210, 255), (int(zone_center[0] - camx), int(zone_center[1] - camy)), int(zone_radius), 3)

    for en in enemies:
        pygame.draw.circle(screen, (220, 80, 80), (int(en.x - camx), int(en.y - camy)), en.r)

    for b in bullets:
        pygame.draw.circle(screen, (255, 220, 130), (int(b.x - camx), int(b.y - camy)), b.r)

    pygame.draw.circle(screen, (90, 180, 255), (int(player.x - camx), int(player.y - camy)), player.r)

    ui = font.render(f"HP:{player.hp}  WOOD:{player.wood}  STONE:{player.stone}  ENEMIES:{len(enemies)}", True, (240,240,240))
    screen.blit(ui, (16, 14))
    if game_over:
        go = font.render("GAME OVER - ESC", True, (255, 120, 120))
        screen.blit(go, (WIDTH//2 - 90, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
