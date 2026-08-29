import pygame
import random
import sys

pygame.init()

WIDTH = 600
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker Arcade")

clock = pygame.time.Clock()

# Micro Fonts
FONT_HUD = pygame.font.SysFont("Courier", 14, bold=True)
FONT_BANNER = pygame.font.SysFont("Courier", 24, bold=True)

# Aesthetic Palette
COLOR_BG = (15, 12, 24)
COLOR_TOPBAR = (8, 6, 14)
COLOR_PADDLE = (255, 105, 180)  # HotPink
COLOR_BALL = (255, 255, 255)
COLOR_TEXT = (220, 210, 240)
COLOR_GOLD = (255, 215, 0)

# Row Colors for Bricks (Vibrant Neon)
ROW_COLORS = [
    (255, 60, 100),   # Red-Pink
    (255, 140, 0),    # Orange
    (255, 215, 0),    # Gold
    (50, 205, 50),    # Lime
    (147, 112, 219)   # Purple
]

# Entities
paddle = pygame.Rect(250, 550, 100, 15)
ball = pygame.Rect(290, 500, 16, 16)

ball_speed = 7
ball_dx = 4
ball_dy = -6

bricks = []
particles = []
powerups = []
trail = []

score = 0
high_score = 0
game_over = False
win = False
shake_timer = 0

def create_bricks():
    brick_list = []
    for row in range(5):
        for column in range(8):
            rect = pygame.Rect(column * 72 + 14, row * 26 + 50, 64, 18)
            brick_list.append({"rect": rect, "color": ROW_COLORS[row]})
    return brick_list

def create_particles(x, y, color):
    for _ in range(8):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-4, 4),
            "dy": random.uniform(-4, 4),
            "size": random.randint(3, 5),
            "color": color,
            "life": 1.0
        })

def reset_game():
    global score, game_over, win, bricks, particles, powerups, trail, ball_dx, ball_dy, shake_timer
    paddle.width = 100
    paddle.x = (WIDTH // 2) - 50
    ball.x = (WIDTH // 2) - 8
    ball.y = 480

    ball_dx = 4
    ball_dy = -6

    score = 0
    game_over = False
    win = False
    shake_timer = 0

    bricks = create_bricks()
    particles.clear()
    powerups.clear()
    trail.clear()

bricks = create_bricks()

# Main Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game_over or win):
                reset_game()
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not game_over and not win:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            paddle.x -= 8
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            paddle.x += 8

        paddle.x = max(0, min(WIDTH - paddle.width, paddle.x))

        # Ball Motion Trail
        trail.append({"x": ball.centerx, "y": ball.centery, "alpha": 255})
        if len(trail) > 6:
            trail.pop(0)

        ball.x += ball_dx
        ball.y += ball_dy

        # Wall Collisions
        if ball.left <= 0:
            ball.left = 0
            ball_dx *= -1
        elif ball.right >= WIDTH:
            ball.right = WIDTH
            ball_dx *= -1

        if ball.top <= 35:
            ball.top = 35
            ball_dy *= -1

        # Paddle Collision (Dynamic Angle Scaling)
        if ball.colliderect(paddle) and ball_dy > 0:
            ball.bottom = paddle.top
            hit_pos = (ball.centerx - paddle.left) / paddle.width  # 0.0 (left) to 1.0 (right)
            ball_dx = (hit_pos - 0.5) * 12  # Range: -6 to 6
            ball_dy = -abs(ball_dy)

        # Brick Collisions
        for b in bricks[:]:
            if ball.colliderect(b["rect"]):
                ball_dy *= -1
                create_particles(b["rect"].centerx, b["rect"].centery, b["color"])
                bricks.remove(b)

                shake_timer = 4
                score += 10
                if score > high_score:
                    high_score = score

                # Power-up Spawn Chance (20%)
                if random.random() < 0.20:
                    p_type = random.choice(["wide", "bonus"])
                    powerups.append({"rect": pygame.Rect(b["rect"].centerx - 10, b["rect"].centery, 20, 20), "type": p_type})

                break

        # Move Power-ups
        for p in powerups[:]:
            p["rect"].y += 3
            if p["rect"].colliderect(paddle):
                if p["type"] == "wide":
                    paddle.width = min(160, paddle.width + 30)
                elif p["type"] == "bonus":
                    score += 100
                    if score > high_score:
                        high_score = score
                powerups.remove(p)
            elif p["rect"].y > HEIGHT:
                powerups.remove(p)

        # Win/Loss Checks
        if ball.bottom >= HEIGHT:
            game_over = True
        if len(bricks) == 0:
            win = True

    # Screen Shake Offset
    render_offset_x = random.randint(-2, 2) if shake_timer > 0 else 0
    render_offset_y = random.randint(-2, 2) if shake_timer > 0 else 0
    if shake_timer > 0:
        shake_timer -= 1

    # --- RENDER ---
    screen.fill(COLOR_BG)

    # Apply Screen Shake Offset
    game_surface = pygame.Surface((WIDTH, HEIGHT))
    game_surface.fill(COLOR_BG)

    # 1. Ball Trail
    for t in trail:
        t["alpha"] -= 35
        if t["alpha"] > 0:
            t_surf = pygame.Surface((ball.width, ball.height), pygame.SRCALPHA)
            pygame.draw.ellipse(t_surf, (255, 255, 255, max(0, t["alpha"])), (0, 0, ball.width, ball.height))
            game_surface.blit(t_surf, (t["x"] - ball.width // 2, t["y"] - ball.height // 2))

    # 2. Paddle & Ball
    pygame.draw.rect(game_surface, COLOR_PADDLE, paddle, border_radius=4)
    pygame.draw.ellipse(game_surface, COLOR_BALL, ball)

    # 3. Bricks
    for b in bricks:
        pygame.draw.rect(game_surface, b["color"], b["rect"], border_radius=3)
        pygame.draw.rect(game_surface, (255, 255, 255), b["rect"], 1, border_radius=3)

    # 4. Particles
    for particle in particles[:]:
        particle["x"] += particle["dx"]
        particle["y"] += particle["dy"]
        particle["life"] -= 0.04
        if particle["life"] <= 0:
            particles.remove(particle)
        else:
            p_surf = pygame.Surface((particle["size"], particle["size"]), pygame.SRCALPHA)
            alpha_color = (*particle["color"], int(255 * particle["life"]))
            p_surf.fill(alpha_color)
            game_surface.blit(p_surf, (particle["x"], particle["y"]))

    # 5. Power-ups
    for p in powerups:
        color = (50, 205, 50) if p["type"] == "wide" else COLOR_GOLD
        pygame.draw.rect(game_surface, color, p["rect"], border_radius=5)
        txt = "W" if p["type"] == "wide" else "$"
        p_txt = FONT_HUD.render(txt, True, (0, 0, 0))
        game_surface.blit(p_txt, (p["rect"].x + 6, p["rect"].y + 2))

    screen.blit(game_surface, (render_offset_x, render_offset_y))

    # 6. Top HUD
    pygame.draw.rect(screen, COLOR_TOPBAR, (0, 0, WIDTH, 35))
    pygame.draw.line(screen, COLOR_PADDLE, (0, 35), (WIDTH, 35), 1)

    score_surf = FONT_HUD.render(f"SCORE:{score:04d}", True, COLOR_PADDLE)
    hi_surf = FONT_HUD.render(f"HI-SCORE:{high_score:04d}", True, COLOR_GOLD)
    screen.blit(score_surf, (15, 10))
    screen.blit(hi_surf, (WIDTH - hi_surf.get_width() - 15, 10))

    # 7. Game Over / Win Overlays
    if game_over or win:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 6, 14, 210))
        screen.blit(overlay, (0, 0))

        banner_text = "YOU WIN!" if win else "GAME OVER"
        banner_color = COLOR_GOLD if win else COLOR_PADDLE
        banner = FONT_BANNER.render(banner_text, True, banner_color)
        score_info = FONT_HUD.render(f"FINAL SCORE: {score:04d}", True, COLOR_TEXT)
        sub_text = FONT_HUD.render("PRESS 'R' TO RESTART", True, COLOR_TEXT)

        screen.blit(banner, (WIDTH // 2 - banner.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(score_info, (WIDTH // 2 - score_info.get_width() // 2, HEIGHT // 2))
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 30))

    pygame.display.update()
    clock.tick(60)