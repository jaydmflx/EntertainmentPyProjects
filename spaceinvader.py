import pygame
import sys

pygame.init()

WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()

# Retro Arcade Typography & Color Palette
FONT_SMALL = pygame.font.SysFont("Courier", 16, bold=True)
FONT_LARGE = pygame.font.SysFont("Courier", 30, bold=True)

COLOR_BG = (10, 10, 18)
COLOR_PLAYER = (255, 105, 180)    # Pink
COLOR_ALIEN = (147, 112, 219)     # MediumPurple
COLOR_CYAN = (0, 255, 240)
COLOR_RED = (255, 50, 80)
COLOR_YELLOW = (255, 230, 0)

player = pygame.Rect(275, 530, 40, 20)
bullets = []
enemies = []

score = 0
high_score = 0
wave = 1
game_over = False

# Base Movement Settings
base_enemy_speed = 2.0
enemy_direction = 1
enemy_speed = base_enemy_speed
drop_speed = 12


def spawn_wave(current_wave):
    """Spawns smaller invaders with tighter grid spacing."""
    global enemy_speed, drop_speed, enemy_direction
    
    num_rows = min(5, 2 + (current_wave // 2))
    enemy_speed = base_enemy_speed + (current_wave - 1) * 0.5
    drop_speed = min(24, 12 + (current_wave - 1) * 2)
    enemy_direction = 1

    enemy_list = []
    # Smaller invaders: 26x18 width/height, spaced 50px horizontally, 32px vertically
    for row in range(num_rows):
        for column in range(8):
            enemy_list.append(
                pygame.Rect(110 + column * 50, 50 + row * 32, 26, 18)
            )
    return enemy_list


enemies = spawn_wave(wave)


def reset_game():
    global player, bullets, enemies, score, wave, game_over
    player.x = 275
    bullets.clear()
    score = 0
    wave = 1
    enemies = spawn_wave(wave)
    game_over = False


def draw_player(surface, rect):
    """Draws the player shooter in Pink."""
    pygame.draw.rect(surface, COLOR_PLAYER, (rect.x, rect.y + 8, rect.width, 12))
    pygame.draw.rect(surface, COLOR_PLAYER, (rect.x + 16, rect.y, 8, 8))


def draw_invader(surface, rect):
    """Draws smaller scaled pixel-style alien invaders (26x18)."""
    x, y = rect.x, rect.y
    # Main Body Core (14x9)
    pygame.draw.rect(surface, COLOR_ALIEN, (x + 6, y + 3, 14, 9))
    # Antennas
    pygame.draw.rect(surface, COLOR_ALIEN, (x + 3, y, 3, 3))
    pygame.draw.rect(surface, COLOR_ALIEN, (x + 20, y, 3, 3))
    # Wings / Arms
    pygame.draw.rect(surface, COLOR_ALIEN, (x, y + 6, 3, 9))
    pygame.draw.rect(surface, COLOR_ALIEN, (x + 23, y + 6, 3, 9))
    # Legs
    pygame.draw.rect(surface, COLOR_ALIEN, (x + 3, y + 15, 3, 3))
    pygame.draw.rect(surface, COLOR_ALIEN, (x + 20, y + 15, 3, 3))


# Main Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullet = pygame.Rect(player.centerx - 2, player.top - 8, 4, 10)
                bullets.append(bullet)

            if event.key == pygame.K_r and game_over:
                reset_game()

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not game_over:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= 6
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += 6

        player.x = max(0, min(WIDTH - player.width, player.x))

        # Move bullets
        for bullet in bullets[:]:
            bullet.y -= 9
            if bullet.bottom < 0:
                bullets.remove(bullet)

        # Move enemies
        hit_edge = False
        for enemy in enemies:
            enemy.x += enemy_speed * enemy_direction
            if enemy.right >= WIDTH or enemy.left <= 0:
                hit_edge = True

        if hit_edge:
            enemy_direction *= -1
            for enemy in enemies:
                enemy.y += drop_speed

        # Bullet collisions
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.colliderect(enemy):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 100
                    if score > high_score:
                        high_score = score
                    break

        # Endless Wave Trigger
        if len(enemies) == 0:
            wave += 1
            bullets.clear()
            enemies = spawn_wave(wave)

        # Lose conditions
        for enemy in enemies:
            if enemy.colliderect(player) or enemy.bottom >= player.top:
                game_over = True

    # Render Screen
    screen.fill(COLOR_BG)

    draw_player(screen, player)

    for enemy in enemies:
        draw_invader(screen, enemy)

    for bullet in bullets:
        pygame.draw.rect(screen, COLOR_YELLOW, bullet)

    # Arcade Bottom Boundary
    pygame.draw.line(screen, COLOR_PLAYER, (0, 560), (WIDTH, 560), 2)

    # Render HUD
    score_surface = FONT_SMALL.render(f"SCORE: {score:05d}", True, COLOR_CYAN)
    wave_surface = FONT_SMALL.render(f"WAVE: {wave}", True, COLOR_YELLOW)
    high_surface = FONT_SMALL.render(f"HI-SCORE: {high_score:05d}", True, COLOR_CYAN)

    screen.blit(score_surface, (15, 15))
    screen.blit(wave_surface, (250, 15))
    screen.blit(high_surface, (WIDTH - 170, 15))

    # Game Over Overlay
    if game_over:
        text_main = FONT_LARGE.render("GAME OVER", True, COLOR_RED)
        text_sub = FONT_SMALL.render("PRESS 'R' TO RESTART", True, (200, 200, 200))

        screen.blit(text_main, (WIDTH // 2 - text_main.get_width() // 2, 250))
        screen.blit(text_sub, (WIDTH // 2 - text_sub.get_width() // 2, 300))

    pygame.display.update()
    clock.tick(60)