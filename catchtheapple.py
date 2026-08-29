import pygame
import random
import sys

pygame.init()

# Window Setup
W, H = 550, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Catch the Falling Objects Arcade")
clock = pygame.time.Clock()

# Micro Arcade Fonts
FONT_HUD = pygame.font.SysFont("Courier", 12, bold=True)
FONT_BANNER = pygame.font.SysFont("Courier", 20, bold=True)

# Aesthetic Palette
COLOR_BG = (15, 12, 24)
COLOR_TOPBAR = (8, 6, 14)
COLOR_TEXT = (220, 210, 240)
COLOR_GOLD = (255, 215, 0)
COLOR_RED = (235, 60, 60)
COLOR_GREEN = (60, 220, 100)
COLOR_BASKET = (210, 140, 70)
COLOR_BASKET_RIM = (240, 170, 100)

# Entities
player = pygame.Rect(W // 2 - 40, H - 50, 80, 24)
objects = []
particles = []
trail = []

# Game State
score = 0
high_score = 0
lives = 5
spawn_timer = 0
game_over = False
shake_timer = 0

def create_particles(x, y, color, count=6):
    for _ in range(count):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-3, 3),
            "dy": random.uniform(-4, -1),
            "radius": random.randint(2, 4),
            "color": color,
            "life": 1.0
        })

def spawn_object():
    obj_type = random.choices(["apple", "gold", "bomb"], weights=[70, 15, 15])[0]
    rect = pygame.Rect(random.randint(20, W - 40), -30, 24, 24)
    return {"rect": rect, "type": obj_type}

def reset():
    global objects, particles, trail, score, lives, spawn_timer, game_over, shake_timer
    objects.clear()
    particles.clear()
    trail.clear()
    player.x = W // 2 - 40
    score = 0
    lives = 5
    spawn_timer = 0
    game_over = False
    shake_timer = 0

reset()

# Main Loop
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if game_over and e.key == pygame.K_RKEY if hasattr(pygame, 'K_RKEY') else e.key == pygame.K_r:
                reset()

    if not game_over:
        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= 8
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += 8
            moving = True

        player.clamp_ip(pygame.Rect(0, 35, W, H - 35))

        # Basket Trail Dust
        if moving and random.random() < 0.4:
            trail.append({
                "x": player.centerx + random.randint(-20, 20),
                "y": player.bottom - 2,
                "radius": random.randint(2, 4),
                "alpha": 255
            })

        # Dynamic Difficulty Scaling
        spawn_rate = max(20, 50 - (score // 3))
        fall_speed = 3.5 + (score // 8)

        spawn_timer += 1
        if spawn_timer >= spawn_rate:
            spawn_timer = 0
            objects.append(spawn_object())

        # Update Falling Objects
        for o in objects[:]:
            o["rect"].y += fall_speed

            # Catch Check
            if o["rect"].colliderect(player):
                if o["type"] == "apple":
                    score += 1
                    create_particles(o["rect"].centerx, o["rect"].centery, COLOR_RED)
                elif o["type"] == "gold":
                    score += 3
                    create_particles(o["rect"].centerx, o["rect"].centery, COLOR_GOLD, count=10)
                elif o["type"] == "bomb":
                    lives -= 1
                    shake_timer = 8
                    create_particles(o["rect"].centerx, o["rect"].centery, (100, 100, 100), count=12)

                if score > high_score:
                    high_score = score
                if lives <= 0:
                    game_over = True

                objects.remove(o)

            # Missed Check
            elif o["rect"].top > H:
                if o["type"] != "bomb":
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                objects.remove(o)

    # Update Trail
    for t in trail[:]:
        t["y"] += 0.5
        t["alpha"] -= 15
        if t["alpha"] <= 0:
            trail.remove(t)

    # Screen Shake Offset
    offset_x = random.randint(-3, 3) if shake_timer > 0 else 0
    offset_y = random.randint(-3, 3) if shake_timer > 0 else 0
    if shake_timer > 0:
        shake_timer -= 1

    # --- RENDER ---
    screen.fill(COLOR_BG)
    game_surface = pygame.Surface((W, H), pygame.SRCALPHA)

    # 1. Trail Particles
    for t in trail:
        t_surf = pygame.Surface((t["radius"] * 2, t["radius"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(t_surf, (180, 180, 180, max(0, t["alpha"])), (t["radius"], t["radius"]), t["radius"])
        game_surface.blit(t_surf, (t["x"] - t["radius"], t["y"] - t["radius"]))

    # 2. Objects
    for o in objects:
        r = o["rect"]
        if o["type"] == "apple":
            pygame.draw.circle(game_surface, COLOR_RED, r.center, 12)
            pygame.draw.circle(game_surface, COLOR_GREEN, (r.centerx + 3, r.centery - 10), 3) # Leaf
        elif o["type"] == "gold":
            pygame.draw.circle(game_surface, COLOR_GOLD, r.center, 12)
            pygame.draw.circle(game_surface, (255, 255, 255), (r.centerx - 3, r.centery - 3), 3) # Sparkle
        elif o["type"] == "bomb":
            pygame.draw.circle(game_surface, (40, 40, 40), r.center, 12)
            pygame.draw.line(game_surface, COLOR_GOLD, (r.centerx, r.centery - 12), (r.centerx + 4, r.centery - 16), 2)

    # 3. Wicker Basket Player
    px, py, pw, ph = player.x, player.y, player.width, player.height
    pygame.draw.rect(game_surface, COLOR_BASKET, (px, py + 4, pw, ph - 4), border_radius=4)
    pygame.draw.rect(game_surface, COLOR_BASKET_RIM, (px - 2, py, pw + 4, 6), border_radius=3)
    # Basket Weave Lines
    for x in range(px + 10, px + pw, 12):
        pygame.draw.line(game_surface, (160, 100, 40), (x, py + 6), (x, py + ph - 2), 2)

    # 4. Impact Particles
    for p in particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 0.04
        if p["life"] <= 0:
            particles.remove(p)
        else:
            p_surf = pygame.Surface((p["radius"] * 2, p["radius"] * 2), pygame.SRCALPHA)
            color_with_alpha = (*p["color"], int(255 * p["life"]))
            pygame.draw.circle(p_surf, color_with_alpha, (p["radius"], p["radius"]), p["radius"])
            game_surface.blit(p_surf, (p["x"] - p["radius"], p["y"] - p["radius"]))

    screen.blit(game_surface, (offset_x, offset_y))

    # 5. Top Micro HUD Bar
    pygame.draw.rect(screen, COLOR_TOPBAR, (0, 0, W, 35))
    pygame.draw.line(screen, COLOR_GOLD, (0, 35), (W, 35), 1)

    score_surf = FONT_HUD.render(f"SCORE:{score:04d}", True, COLOR_GOLD)
    hi_surf = FONT_HUD.render(f"HI-SCORE:{high_score:04d}", True, COLOR_TEXT)
    lives_surf = FONT_HUD.render(f"LIVES: {'♥' * max(0, lives)}", True, COLOR_RED)

    screen.blit(score_surf, (15, 10))
    screen.blit(hi_surf, (W // 2 - hi_surf.get_width() // 2, 10))
    screen.blit(lives_surf, (W - lives_surf.get_width() - 15, 10))

    # 6. Game Over Screen
    if game_over:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((8, 6, 14, 210))
        screen.blit(overlay, (0, 0))

        banner = FONT_BANNER.render("GAME OVER", True, COLOR_RED)
        final_score = FONT_HUD.render(f"FINAL SCORE: {score:04d}", True, COLOR_GOLD)
        sub_text = FONT_HUD.render("PRESS 'R' TO RESTART", True, COLOR_TEXT)

        screen.blit(banner, (W // 2 - banner.get_width() // 2, H // 2 - 40))
        screen.blit(final_score, (W // 2 - final_score.get_width() // 2, H // 2))
        screen.blit(sub_text, (W // 2 - sub_text.get_width() // 2, H // 2 + 30))

    pygame.display.flip()
    clock.tick(60)