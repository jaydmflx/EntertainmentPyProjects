import pygame
import random
import sys
import time

pygame.init()

# Board Configuration
ROWS = 10
COLS = 10
SIZE = 48
TOP_BAR_HEIGHT = 70

WIDTH = COLS * SIZE
HEIGHT = (ROWS * SIZE) + TOP_BAR_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper Deluxe")
clock = pygame.time.Clock()

# Compact Retro Arcade Fonts
FONT_HUD = pygame.font.SysFont("Courier", 13, bold=True)
FONT_CELL = pygame.font.SysFont("Courier", 18, bold=True)
FONT_BANNER = pygame.font.SysFont("Courier", 22, bold=True)

# Classic Color Palette
COLOR_BG = (25, 25, 35)
COLOR_TOPBAR = (15, 15, 25)
COLOR_HIDDEN = (65, 75, 90)
COLOR_REVEALED = (190, 195, 205)
COLOR_BORDER = (10, 10, 15)
COLOR_GOLD = (255, 215, 0)
COLOR_TEXT = (220, 220, 230)
COLOR_GREEN = (50, 205, 50)
COLOR_RED = (235, 60, 60)

NUMBER_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128),
}

MINES = 15

# Global Persistent Stats
high_score = 0

# Game Session State
board = []
revealed = []
flagged = []
first_click = True
game_over = False
win = False
start_time = 0
elapsed_time = 0
score = 0


def generate_mines(safe_r, safe_c):
    """Generates mine locations ensuring the first clicked tile is always safe."""
    global board
    board = [[0] * COLS for _ in range(ROWS)]
    mines_placed = 0

    while mines_placed < MINES:
        r = random.randint(0, ROWS - 1)
        c = random.randint(0, COLS - 1)

        # Skip safe tile & immediate surroundings on first click
        if abs(r - safe_r) <= 1 and abs(c - safe_c) <= 1:
            continue

        if board[r][c] != -1:
            board[r][c] = -1
            mines_placed += 1

    # Calculate adjacent mine numbers
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == -1:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == -1:
                        count += 1
            board[r][c] = count


def flood_fill(r, c):
    """Automatically opens all adjacent blank tiles recursively."""
    if not (0 <= r < ROWS and 0 <= c < COLS):
        return
    if revealed[r][c] or flagged[r][c]:
        return

    revealed[r][c] = True

    if board[r][c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr != 0 or dc != 0:
                    flood_fill(r + dr, c + dc)


def check_win():
    """Checks if all safe non-mine tiles have been successfully revealed."""
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != -1 and not revealed[r][c]:
                return False
    return True


def reset_game():
    global board, revealed, flagged, first_click, game_over, win
    global start_time, elapsed_time, score

    board = [[0] * COLS for _ in range(ROWS)]
    revealed = [[False] * COLS for _ in range(ROWS)]
    flagged = [[False] * COLS for _ in range(ROWS)]

    first_click = True
    game_over = False
    win = False
    start_time = 0
    elapsed_time = 0
    score = 0


reset_game()

# Main Event Loop
while True:
    if not game_over and not win and not first_click:
        elapsed_time = int(time.time() - start_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not win:
            mx, my = event.pos

            # Check if click is inside grid space (below Top HUD Bar)
            if my >= TOP_BAR_HEIGHT:
                c = mx // SIZE
                r = (my - TOP_BAR_HEIGHT) // SIZE

                if 0 <= r < ROWS and 0 <= c < COLS:
                    # LEFT-CLICK: Reveal Cell
                    if event.button == 1:
                        if first_click:
                            generate_mines(r, c)
                            start_time = time.time()
                            first_click = False

                        if not flagged[r][c]:
                            if board[r][c] == -1:
                                revealed[r][c] = True
                                game_over = True
                            else:
                                flood_fill(r, c)
                                if check_win():
                                    win = True
                                    # Calculate Victory Score: Speed + Clean Sweep Bonus
                                    score = max(100, (ROWS * COLS * 50) - (elapsed_time * 10))
                                    if score > high_score:
                                        high_score = score

                    # RIGHT-CLICK: Toggle Flag
                    elif event.button == 3:
                        if not revealed[r][c] and not first_click:
                            flagged[r][c] = not flagged[r][c]

    # RENDER SCREEN
    screen.fill(COLOR_BG)

    # 1. TOP HUD BAR (Scores, Flag Count, Timer)
    pygame.draw.rect(screen, COLOR_TOPBAR, (0, 0, WIDTH, TOP_BAR_HEIGHT))
    pygame.draw.line(screen, COLOR_BORDER, (0, TOP_BAR_HEIGHT), (WIDTH, TOP_BAR_HEIGHT), 2)

    # Calculate remaining flags
    flags_used = sum(row.count(True) for row in flagged)
    remaining_flags = MINES - flags_used

    p_flags = FONT_HUD.render(f"FLAGS:{remaining_flags:02d}", True, COLOR_RED)
    p_time = FONT_HUD.render(f"TIME:{elapsed_time:03d}s", True, COLOR_TEXT)
    p_score = FONT_HUD.render(f"SCORE:{score:04d}", True, COLOR_GOLD)
    p_hi = FONT_HUD.render(f"HI:{high_score:04d}", True, COLOR_GOLD)

    screen.blit(p_flags, (12, 14))
    screen.blit(p_time, (120, 14))
    screen.blit(p_score, (230, 14))
    screen.blit(p_hi, (340, 14))

    info_sub = FONT_HUD.render("[L-CLICK] Dig  [R-CLICK] Flag  [R] Reset", True, COLOR_TEXT)
    screen.blit(info_sub, (12, 42))

    # 2. MINESWEEPER BOARD GRID
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * SIZE, r * SIZE + TOP_BAR_HEIGHT, SIZE, SIZE)

            if revealed[r][c]:
                pygame.draw.rect(screen, COLOR_REVEALED, rect)

                if board[r][c] > 0:
                    val_color = NUMBER_COLORS.get(board[r][c], (0, 0, 0))
                    text_surf = FONT_CELL.render(str(board[r][c]), True, val_color)
                    screen.blit(
                        text_surf,
                        (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2)
                    )

                elif board[r][c] == -1:
                    # Mine Bomb Graphic
                    pygame.draw.rect(screen, COLOR_RED, rect)
                    pygame.draw.circle(screen, (0, 0, 0), rect.center, SIZE // 4)
                    bomb_text = FONT_CELL.render("*", True, (255, 255, 255))
                    screen.blit(
                        bomb_text,
                        (rect.centerx - bomb_text.get_width() // 2, rect.centery - bomb_text.get_height() // 2 + 2)
                    )

            else:
                pygame.draw.rect(screen, COLOR_HIDDEN, rect)

                if flagged[r][c]:
                    flag_surf = FONT_CELL.render("P", True, COLOR_RED)
                    screen.blit(
                        flag_surf,
                        (rect.centerx - flag_surf.get_width() // 2, rect.centery - flag_surf.get_height() // 2)
                    )

            # Cell borders
            pygame.draw.rect(screen, COLOR_BORDER, rect, 1)

    # 3. GAME OVER / WIN BANNER OVERLAYS
    if game_over:
        # Reveal all mines on death
        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] == -1:
                    revealed[r][c] = True

        banner = FONT_BANNER.render("BOOM! GAME OVER - PRESS R", True, COLOR_RED)
        bg_rect = banner.get_rect(center=(WIDTH // 2, TOP_BAR_HEIGHT + (ROWS * SIZE) // 2))
        pygame.draw.rect(screen, COLOR_TOPBAR, bg_rect.inflate(20, 14))
        pygame.draw.rect(screen, COLOR_RED, bg_rect.inflate(20, 14), 2)
        screen.blit(banner, bg_rect)

    elif win:
        banner = FONT_BANNER.render("BOARD CLEARED! PRESS R", True, COLOR_GREEN)
        bg_rect = banner.get_rect(center=(WIDTH // 2, TOP_BAR_HEIGHT + (ROWS * SIZE) // 2))
        pygame.draw.rect(screen, COLOR_TOPBAR, bg_rect.inflate(20, 14))
        pygame.draw.rect(screen, COLOR_GREEN, bg_rect.inflate(20, 14), 2)
        screen.blit(banner, bg_rect)

    pygame.display.update()
    clock.tick(60)