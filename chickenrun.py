import pygame
import random
import sys

pygame.init()

# Compact Screen Dimensions
WIDTH = 360
HEIGHT = 460

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chicken Run Arcade")

clock = pygame.time.Clock()

# Micro Arcade Fonts
FONT_HUD = pygame.font.SysFont("Courier", 10, bold=True)
FONT_BANNER = pygame.font.SysFont("Courier", 16, bold=True)

# Aesthetic Palette
COLOR_BG = (15, 12, 24)
COLOR_TOPBAR = (8, 6, 14)
COLOR_TEXT = (200, 200, 220)
COLOR_GOLD = (255, 215, 0)
COLOR_RED = (220, 30, 30)
COLOR_YELLOW = (255, 190, 0)

# Chicken Palette (Front Facing)
COLOR_CHICKEN_BODY = (245, 245, 240)
COLOR_CHICKEN_SHADOW = (210, 210, 215)
COLOR_WING = (230, 230, 235)

# Obstacle Palette (Neon Pink Debris)
COLOR_DEBRIS = (255, 20, 147)        # Deep HotPink
COLOR_DEBRIS_HIGHLIGHT = (255, 105, 180) # Light Pink

# Entities
player = pygame.Rect(WIDTH // 2 - 12, HEIGHT - 50, 24, 24)
obstacles = []
collectibles = []
particles = []

# Game State
high_score = 0
score = 0
game_over = False
spawn_timer = 0
collect_timer = 0

def reset_game():
    global obstacles, collectibles, particles, score, game_over, spawn_timer, collect_timer
    player.x = (WIDTH // 2) - 12
    obstacles.clear()
    collectibles.clear()
    particles.clear()
    score = 0
    game_over = False
    spawn_timer = 0
    collect_timer = 0

reset_game()

# Main Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not game_over:
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= 5
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += 5
            moving = True

        player.x = max(2, min(WIDTH - player.width - 2, player.x))

        # Trail Particles when moving
        if moving and random.random() < 0.4:
            particles.append({
                "x": player.centerx + random.randint(-4, 4),
                "y": player.bottom - 2,
                "radius": random.randint(2, 4),
                "alpha": 255
            })

        # Difficulty Scaling
        spawn_rate = max(15, 38 - (score // 4))
        obstacle_speed = 4.5 + (score // 10)

        # Spawn Pink Debris
        spawn_timer += 1
        if spawn_timer >= spawn_rate:
            obs_width = random.randint(20, 36)
            obstacle = pygame.Rect(random.randint(0, WIDTH - obs_width), -20, obs_width, 18)
            obstacles.append(obstacle)
            spawn_timer = 0

        # Spawn Golden Eggs (+5 score)
        collect_timer += 1
        if collect_timer >= 120:
            collectibles.append(pygame.Rect(random.randint(10, WIDTH - 20), -15, 12, 14))
            collect_timer = 0

        # Move & Check Debris
        for obstacle in obstacles[:]:
            obstacle.y += obstacle_speed
            if obstacle.y > HEIGHT:
                obstacles.remove(obstacle)
                score += 1
                if score > high_score:
                    high_score = score

            if obstacle.colliderect(player):
                game_over = True

        # Move & Check Collectibles
        for item in collectibles[:]:
            item.y += 3
            if item.y > HEIGHT:
                collectibles.remove(item)
            elif item.colliderect(player):
                collectibles.remove(item)
                score += 5
                if score > high_score:
                    high_score = score

    # Update Trail Particles
    for p in particles[:]:
        p["y"] += 1
        p["alpha"] -= 15
        if p["alpha"] <= 0:
            particles.remove(p)

    # --- RENDER ---
    screen.fill(COLOR_BG)

    # 1. Particles
    for p in particles:
        p_surf = pygame.Surface((p["radius"] * 2, p["radius"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (200, 200, 200, p["alpha"]), (p["radius"], p["radius"]), p["radius"])
        screen.blit(p_surf, (p["x"] - p["radius"], p["y"] - p["radius"]))

    # 2. Pink Obstacles (Debris)
    for obstacle in obstacles:
        pygame.draw.rect(screen, COLOR_DEBRIS, obstacle, border_radius=3)
        pygame.draw.rect(screen, COLOR_DEBRIS_HIGHLIGHT, obstacle, 1, border_radius=3)

    # 3. Collectibles (Golden Eggs)
    for item in collectibles:
        pygame.draw.ellipse(screen, COLOR_GOLD, item)
        pygame.draw.ellipse(screen, (255, 255, 255), (item.x + 3, item.y + 3, 3, 4)) # Highlight

    # 4. FRONT-FACING CHICKEN PLAYER RENDERING
    px, py, pw, ph = player.x, player.y, player.width, player.height
    cx = px + pw // 2

    # Drop Shadow
    pygame.draw.ellipse(screen, (10, 8, 16), (px + 2, py + ph - 4, pw - 4, 6))

    # Side Wings (Left & Right)
    pygame.draw.ellipse(screen, COLOR_WING, (px - 2, py + 8, 7, 12))
    pygame.draw.ellipse(screen, COLOR_WING, (px + pw - 5, py + 8, 7, 12))

    # Main Body (Centered Box)
    pygame.draw.rect(screen, COLOR_CHICKEN_BODY, (px + 2, py + 4, pw - 4, ph - 4), border_radius=6)
    pygame.draw.rect(screen, COLOR_CHICKEN_SHADOW, (px + 2, py + ph - 6, pw - 4, 6), border_bottom_left_radius=6, border_bottom_right_radius=6)

    # Centered Comb (Top Red Crest)
    pygame.draw.circle(screen, COLOR_RED, (cx - 3, py + 2), 3)
    pygame.draw.circle(screen, COLOR_RED, (cx, py + 1), 3)
    pygame.draw.circle(screen, COLOR_RED, (cx + 3, py + 2), 3)

    # Eyes (Symmetrical Left & Right)
    pygame.draw.circle(screen, (15, 15, 15), (cx - 5, py + 10), 2)
    pygame.draw.circle(screen, (255, 255, 255), (cx - 6, py + 9), 1)
    pygame.draw.circle(screen, (15, 15, 15), (cx + 5, py + 10), 2)
    pygame.draw.circle(screen, (255, 255, 255), (cx + 4, py + 9), 1)

    # Centered Beak (Down-pointing Triangle)
    pygame.draw.polygon(screen, COLOR_YELLOW, [
        (cx - 3, py + 12),
        (cx + 3, py + 12),
        (cx, py + 17)
    ])

    # Wattle (Red flap under beak)
    pygame.draw.circle(screen, COLOR_RED, (cx - 2, py + 17), 2)
    pygame.draw.circle(screen, COLOR_RED, (cx + 2, py + 17), 2)

    # 5. Top Micro HUD
    pygame.draw.rect(screen, COLOR_TOPBAR, (0, 0, WIDTH, 28))
    pygame.draw.line(screen, COLOR_DEBRIS, (0, 28), (WIDTH, 28), 1)

    score_surf = FONT_HUD.render(f"SCORE:{score:04d}", True, COLOR_DEBRIS_HIGHLIGHT)
    hi_surf = FONT_HUD.render(f"HI-SCORE:{high_score:04d}", True, COLOR_GOLD)

    screen.blit(score_surf, (10, 9))
    screen.blit(hi_surf, (WIDTH - hi_surf.get_width() - 10, 9))

    # 6. Game Over Screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 6, 14, 210))
        screen.blit(overlay, (0, 0))

        banner = FONT_BANNER.render("GAME OVER", True, COLOR_DEBRIS_HIGHLIGHT)
        sub_text = FONT_HUD.render("PRESS 'R' TO RESTART", True, COLOR_TEXT)
        final_score = FONT_HUD.render(f"FINAL SCORE: {score:04d}", True, COLOR_GOLD)

        screen.blit(banner, (WIDTH // 2 - banner.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 25))

    pygame.display.update()
    clock.tick(60)