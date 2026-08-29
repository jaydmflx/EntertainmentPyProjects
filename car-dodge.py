import pygame
import random
import sys

pygame.init()

WIDTH = 500
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Dodge")

clock = pygame.time.Clock()

player = pygame.Rect(220, 500, 50, 80)

enemy = pygame.Rect(
    random.randint(50, 400),
    -100,
    50,
    80
)

score = 0
high_score = 0  # Global high score tracker
game_over = False

# Changed all HUD/UI text to small font (25px)
small = pygame.font.SysFont("Arial", 25)


while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r and game_over:

                player.x = 220
                enemy.x = random.randint(50, 400)
                enemy.y = -100

                score = 0
                game_over = False

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()


    keys = pygame.key.get_pressed()

    if not game_over:

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= 6

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += 6

        player.x = max(0, min(WIDTH - player.width, player.x))

        # Progressive speed: Starts at 4 (slow) and increases by 0.5 per point up to max 16
        enemy_speed = min(16, 4 + (score * 0.5))
        enemy.y += enemy_speed

        if enemy.y > HEIGHT:

            enemy.y = -100
            enemy.x = random.randint(50, 400)

            score += 1
            if score > high_score:
                high_score = score

        if player.colliderect(enemy):
            game_over = True


    screen.fill("gray")

    # Road
    pygame.draw.rect(screen, "black", (40, 0, 420, HEIGHT))

    # Road lines
    for y in range(0, HEIGHT, 80):
        pygame.draw.rect(screen, "white", (245, y, 10, 40))

    # Cars
    pygame.draw.rect(screen, "hotpink", player)
    pygame.draw.rect(screen, "mediumpurple", enemy)

    # In-game HUD (Small Font)
    score_text = small.render(f"Score: {score}  High Score: {high_score}", True, "white")
    screen.blit(score_text, (50, 10))


    if game_over:

        go_text = small.render("GAME OVER", True, "white")
        screen.blit(go_text, (190, 250))

        final_score_text = small.render(f"Score: {score} | High: {high_score}", True, "white")
        screen.blit(final_score_text, (170, 285))

        restart_text = small.render("Press R to Restart", True, "white")
        screen.blit(restart_text, (160, 320))


    pygame.display.update()
    clock.tick(60)