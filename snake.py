import pygame
import random
import sys

# =========================
# SETTINGS
# =========================
ROWS = 25
COLUMNS = 25
TILE_SIZE = 25

GAME_WIDTH = COLUMNS * TILE_SIZE
GAME_HEIGHT = ROWS * TILE_SIZE

# Starting speed
SNAKE_SPEED = 6


# =========================
# INITIALIZE
# =========================
pygame.init()

window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Snake Game ni Vine")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 50)
small_font = pygame.font.SysFont("Arial", 25)

high_score = 0  # Global high score tracker


# =========================
# RANDOM POSITION
# =========================
def get_random(limit):
    return random.randint(0, limit - 1) * TILE_SIZE


# =========================
# RESET GAME
# =========================
def reset_game():

    global snake
    global food
    global snake_velocity
    global game_over
    global score

    # Snake starts in the middle
    start_x = (COLUMNS // 2) * TILE_SIZE
    start_y = (ROWS // 2) * TILE_SIZE

    snake = [
        pygame.Rect(start_x, start_y, TILE_SIZE, TILE_SIZE),
        pygame.Rect(start_x - TILE_SIZE, start_y, TILE_SIZE, TILE_SIZE),
        pygame.Rect(start_x - TILE_SIZE * 2, start_y, TILE_SIZE, TILE_SIZE)
    ]

    score = 0

    # Snake automatically moves right
    snake_velocity = [TILE_SIZE, 0]

    # Create food
    create_food()

    game_over = False


# =========================
# CREATE FOOD
# =========================
def create_food():

    global food

    while True:

        new_food = pygame.Rect(
            get_random(COLUMNS),
            get_random(ROWS),
            TILE_SIZE,
            TILE_SIZE
        )

        # Make sure food does not spawn inside snake
        if not any(new_food.colliderect(part) for part in snake):
            food = new_food
            break


# =========================
# START GAME
# =========================
reset_game()


# =========================
# MAIN GAME LOOP
# =========================
while True:

    # =========================
    # EVENTS
    # =========================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # Restart
            if game_over and event.key == pygame.K_r:
                reset_game()

            # Quit
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # =========================
            # MOVEMENT
            # =========================
            elif not game_over:

                # UP
                if event.key in (pygame.K_UP, pygame.K_w):

                    # Prevent going directly down
                    if snake_velocity != [0, TILE_SIZE]:
                        snake_velocity = [0, -TILE_SIZE]

                # DOWN
                elif event.key in (pygame.K_DOWN, pygame.K_s):

                    # Prevent going directly up
                    if snake_velocity != [0, -TILE_SIZE]:
                        snake_velocity = [0, TILE_SIZE]

                # LEFT
                elif event.key in (pygame.K_LEFT, pygame.K_a):

                    # Prevent going directly right
                    if snake_velocity != [TILE_SIZE, 0]:
                        snake_velocity = [-TILE_SIZE, 0]

                # RIGHT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):

                    # Prevent going directly left
                    if snake_velocity != [-TILE_SIZE, 0]:
                        snake_velocity = [TILE_SIZE, 0]


    # =========================
    # GAME UPDATE
    # =========================
    if not game_over:

        # Move body from back to front
        for i in range(len(snake) - 1, 0, -1):
            snake[i] = snake[i - 1].copy()

        # Move head
        snake[0].move_ip(snake_velocity)

        # =========================
        # WALL COLLISION
        # =========================
        if not window.get_rect().contains(snake[0]):
            game_over = True

        # =========================
        # SELF COLLISION
        # =========================
        for part in snake[1:]:

            if snake[0].colliderect(part):
                game_over = True
                break

        # =========================
        # FOOD
        # =========================
        if not game_over and snake[0].colliderect(food):

            # Add new body part
            snake.append(snake[-1].copy())

            # Update scores
            score += 1
            if score > high_score:
                high_score = score

            # Create new food
            create_food()


    # =========================
    # DRAW
    # =========================
    window.fill("black")

    if not game_over:

        # Draw food
        pygame.draw.rect(
            window,
            "red",
            food
        )

        # Draw snake
        for i, snake_part in enumerate(snake):

            if i == 0:
                # Snake head
                pygame.draw.rect(
                    window,
                    "green",
                    snake_part
                )

            else:
                # Snake body
                pygame.draw.rect(
                    window,
                    "limegreen",
                    snake_part
                )

        # Draw HUD (Score & High Score in small_font)
        score_text = small_font.render(
            f"Score: {score}   High Score: {high_score}",
            True,
            "white"
        )
        window.blit(score_text, (10, 10))

    else:

        # =========================
        # GAME OVER SCREEN
        # =========================

        game_over_text = font.render(
            "GAME OVER",
            True,
            "white"
        )

        x = GAME_WIDTH // 2 - game_over_text.get_width() // 2
        y = GAME_HEIGHT // 2 - 80

        window.blit(
            game_over_text,
            (x, y)
        )

        final_score_text = small_font.render(
            f"Score: {score} | High Score: {high_score}",
            True,
            "white"
        )
        x_score = GAME_WIDTH // 2 - final_score_text.get_width() // 2
        y_score = GAME_HEIGHT // 2 - 10

        window.blit(
            final_score_text,
            (x_score, y_score)
        )

        restart_text = small_font.render(
            "Press R to Restart",
            True,
            "white"
        )

        x2 = GAME_WIDTH // 2 - restart_text.get_width() // 2
        y2 = GAME_HEIGHT // 2 + 30

        window.blit(
            restart_text,
            (x2, y2)
        )


    # =========================
    # UPDATE SCREEN
    # =========================
    pygame.display.update()

    # Game speed
    clock.tick(SNAKE_SPEED)