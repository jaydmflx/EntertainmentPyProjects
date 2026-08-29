import pygame
import sys
import random

pygame.init()

WIDTH = 800
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis / Pong")

clock = pygame.time.Clock()

# Colors
COLOR_BG = (10, 10, 18)
COLOR_P1 = (255, 105, 180)     # Hot Pink
COLOR_P2 = (147, 112, 219)     # Medium Purple
COLOR_BALL = (255, 230, 0)     # Yellow
COLOR_NET = (100, 100, 120)
COLOR_TEXT = (200, 200, 220)
COLOR_GOLD = (255, 215, 0)

# Retro Arcade Typography
FONT_HUD = pygame.font.SysFont("Courier", 16, bold=True)
FONT_LARGE = pygame.font.SysFont("Courier", 34, bold=True)
FONT_INFO = pygame.font.SysFont("Courier", 14, bold=True)

left_paddle = pygame.Rect(30, 250, 16, 90)
right_paddle = pygame.Rect(754, 250, 16, 90)
ball = pygame.Rect(390, 290, 16, 16)

ball_speed_base = 6
ball_x = ball_speed_base
ball_y = ball_speed_base

# Ping Pong Match, High Score & Win Counts
p1_score = 0
p2_score = 0
p1_high_score = 0
p2_high_score = 0

p1_match_wins = 0
p2_match_wins = 0

winner_text = ""
game_over = False


def reset_ball():
    """Resets ball position with a randomized angle launch."""
    global ball_x, ball_y
    ball.center = (WIDTH // 2, 275)
    ball_y = random.choice([-5, -4, 4, 5])
    ball_x = -ball_speed_base if ball_x > 0 else ball_speed_base


def reset_match():
    """Resets current round points while keeping high scores & win tallies intact."""
    global p1_score, p2_score, game_over, winner_text
    p1_score = 0
    p2_score = 0
    game_over = False
    winner_text = ""
    reset_ball()


# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_match()

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not game_over:
        keys = pygame.key.get_pressed()

        # Player 1 Controls (W / S)
        if keys[pygame.K_w]:
            left_paddle.y -= 7
        if keys[pygame.K_s]:
            left_paddle.y += 7

        # Player 2 Controls (UP / DOWN)
        if keys[pygame.K_UP]:
            right_paddle.y -= 7
        if keys[pygame.K_DOWN]:
            right_paddle.y += 7

        # Clamp Paddles inside table boundaries
        left_paddle.y = max(0, min(550 - left_paddle.height, left_paddle.y))
        right_paddle.y = max(0, min(550 - right_paddle.height, right_paddle.y))

        # Ball Movement
        ball.x += ball_x
        ball.y += ball_y

        # Top/Bottom Wall Bounces
        if ball.top <= 0 or ball.bottom >= 550:
            ball_y *= -1

        # Angle-based paddle collision
        if ball.colliderect(left_paddle) and ball_x < 0:
            ball_x = abs(ball_x) + 0.2
            impact_offset = (ball.centery - left_paddle.centery) / (left_paddle.height / 2)
            ball_y = impact_offset * 7

        if ball.colliderect(right_paddle) and ball_x > 0:
            ball_x = -(abs(ball_x) + 0.2)
            impact_offset = (ball.centery - right_paddle.centery) / (right_paddle.height / 2)
            ball_y = impact_offset * 7

        # Ping-Pong Scoring Logic (First to 11, must win by 2)
        if ball.left <= 0:
            p2_score += 1
            if p2_score > p2_high_score:
                p2_high_score = p2_score

            # Check Match Win Condition
            if p2_score >= 11 and (p2_score - p1_score) >= 2:
                game_over = True
                p2_match_wins += 1
                winner_text = "PLAYER 2 WINS!"
            else:
                reset_ball()

        if ball.right >= WIDTH:
            p1_score += 1
            if p1_score > p1_high_score:
                p1_high_score = p1_score

            # Check Match Win Condition
            if p1_score >= 11 and (p1_score - p2_score) >= 2:
                game_over = True
                p1_match_wins += 1
                winner_text = "PLAYER 1 WINS!"
            else:
                reset_ball()

    # RENDER SCREEN
    screen.fill(COLOR_BG)

    # Draw Center Net
    for y in range(0, 550, 20):
        pygame.draw.rect(screen, COLOR_NET, (WIDTH // 2 - 2, y, 4, 10))

    # Draw Bottom Boundary Line
    pygame.draw.line(screen, COLOR_NET, (0, 550), (WIDTH, 550), 3)

    # Draw Game Objects
    pygame.draw.rect(screen, COLOR_P1, left_paddle)
    pygame.draw.rect(screen, COLOR_P2, right_paddle)
    pygame.draw.ellipse(screen, COLOR_BALL, ball)

    # Render HUD Details
    p1_score_surf = FONT_HUD.render(f"P1 SCORE:{p1_score:02d}", True, COLOR_P1)
    p1_high_surf = FONT_HUD.render(f"HI:{p1_high_score:02d}", True, COLOR_GOLD)
    p1_wins_surf = FONT_HUD.render(f"WINS:{p1_match_wins}", True, COLOR_CYAN := (0, 255, 240))

    p2_score_surf = FONT_HUD.render(f"P2 SCORE:{p2_score:02d}", True, COLOR_P2)
    p2_high_surf = FONT_HUD.render(f"HI:{p2_high_score:02d}", True, COLOR_GOLD)
    p2_wins_surf = FONT_HUD.render(f"WINS:{p2_match_wins}", True, COLOR_CYAN)

    # Top HUD Layout
    # Left Side (Player 1)
    screen.blit(p1_score_surf, (20, 15))
    screen.blit(p1_high_surf, (150, 15))
    screen.blit(p1_wins_surf, (230, 15))

    # Right Side (Player 2)
    screen.blit(p2_wins_surf, (WIDTH - 300, 15))
    screen.blit(p2_high_surf, (WIDTH - 220, 15))
    screen.blit(p2_score_surf, (WIDTH - 140, 15))

    # Bottom Controls Guide Banner
    controls_p1 = FONT_INFO.render("P1: [W] UP  [S] DOWN", True, COLOR_P1)
    controls_p2 = FONT_INFO.render("P2: [UP ARROW] UP  [DOWN ARROW] DOWN", True, COLOR_P2)

    screen.blit(controls_p1, (20, 575))
    screen.blit(controls_p2, (WIDTH - controls_p2.get_width() - 20, 575))

    # Game Over Screen
    if game_over:
        win_surf = FONT_LARGE.render(winner_text, True, COLOR_GOLD)
        restart_surf = FONT_HUD.render("PRESS 'R' TO PLAY NEXT MATCH", True, COLOR_TEXT)

        screen.blit(win_surf, (WIDTH // 2 - win_surf.get_width() // 2, 230))
        screen.blit(restart_surf, (WIDTH // 2 - restart_surf.get_width() // 2, 285))

    pygame.display.update()
    clock.tick(60)