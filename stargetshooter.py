import pygame
import random
import sys

pygame.init()

WIDTH = 600
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Target Shooter")

# Hide the standard mouse cursor
pygame.mouse.set_visible(False)

clock = pygame.time.Clock()

target = pygame.Rect(
    random.randint(50, 550),
    random.randint(50, 550),
    50,
    50
)

score = 0
high_score = 0
time_left = 30

start_time = pygame.time.get_ticks()

font = pygame.font.SysFont("Arial", 25)

def draw_sniper_crosshair(surface, pos):
    """Draws a compact sniper scope crosshair centered at the mouse position."""
    x, y = pos
    color = "hotpink"
    
    # Smaller outer scope ring (radius 12)
    pygame.draw.circle(surface, color, (x, y), 12, 1)
    # Tiny center dot
    pygame.draw.circle(surface, color, (x, y), 1)
    
    # Reticle lines (shorter lengths and tight center gap)
    pygame.draw.line(surface, color, (x - 18, y), (x - 4, y), 1)  # Left
    pygame.draw.line(surface, color, (x + 4, y), (x + 18, y), 1)  # Right
    pygame.draw.line(surface, color, (x, y - 18), (x, y - 4), 1)  # Top
    pygame.draw.line(surface, color, (x, y + 4), (x, y + 18), 1)  # Bottom

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                score = 0
                start_time = pygame.time.get_ticks()
                target.x = random.randint(50, 550)
                target.y = random.randint(50, 550)

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if time_left > 0 and target.collidepoint(event.pos):
                score += 1
                if score > high_score:
                    high_score = score

                target.x = random.randint(50, 550)
                target.y = random.randint(50, 550)

    elapsed = (pygame.time.get_ticks() - start_time) // 1000
    time_left = max(0, 30 - elapsed)

    screen.fill("black")

    if time_left > 0:
        pygame.draw.circle(
            screen,
            "mediumpurple",
            target.center,
            25
        )

        screen.blit(font.render(f"Score: {score}", True, "white"), (20, 20))
        screen.blit(font.render(f"High Score: {high_score}", True, "white"), (20, 50))
        screen.blit(font.render(f"Time: {time_left}", True, "white"), (20, 80))

    else:
        screen.blit(
            font.render(f"TIME'S UP! Score: {score}", True, "white"),
            (180, 250)
        )
        screen.blit(
            font.render(f"High Score: {high_score}", True, "white"),
            (220, 285)
        )
        screen.blit(
            font.render("Press R to Restart", True, "white"),
            (210, 320)
        )

    # Draw crosshair over game elements
    mouse_pos = pygame.mouse.get_pos()
    draw_sniper_crosshair(screen, mouse_pos)

    pygame.display.update()
    clock.tick(60)