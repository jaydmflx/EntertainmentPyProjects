import pygame
import random
import sys

pygame.init()

# Extended Width to fit Side HUD Panel
WIDTH = 480
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris Arcade")
clock = pygame.time.Clock()

# Compact Grid Setup
CELL = 22
COLS = 10
ROWS = 20
BOARD_X = 20
BOARD_Y = 30

# Modern Compact Typography
FONT_HUD = pygame.font.SysFont("Courier", 12, bold=True)
FONT_VALUE = pygame.font.SysFont("Courier", 16, bold=True)
FONT_BANNER = pygame.font.SysFont("Courier", 20, bold=True)

# Aesthetic Palette (HotPink & MediumPurple Primary Accents)
COLOR_BG = (15, 12, 25)
COLOR_SIDEBAR = (25, 20, 40)
COLOR_GRID = (45, 35, 65)
COLOR_P1 = (255, 105, 180)     # HotPink
COLOR_P2 = (147, 112, 219)     # MediumPurple
COLOR_GOLD = (255, 215, 0)
COLOR_CYAN = (0, 240, 240)
COLOR_TEXT = (220, 210, 240)

# Custom Piece Palette
SHAPE_COLORS = [
    (0, 240, 240),      # I: Cyan
    (255, 215, 0),      # O: Gold
    COLOR_P2,           # T: MediumPurple
    (255, 165, 0),      # L: Orange
    (60, 110, 245),     # J: Blue
    COLOR_P1,           # S: HotPink
    (235, 60, 60)       # Z: Red
]

shapes = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]

# High Score Persistence Across Matches
high_score = 0


def get_random_piece():
    idx = random.randint(0, len(shapes) - 1)
    return shapes[idx], SHAPE_COLORS[idx]


def reset_game():
    global board, piece, piece_color, next_piece, next_color
    global piece_x, piece_y, score, lines_cleared, level, game_over

    board = [[0] * COLS for _ in range(ROWS)]
    piece, piece_color = get_random_piece()
    next_piece, next_color = get_random_piece()

    piece_x = 3
    piece_y = 0

    score = 0
    lines_cleared = 0
    level = 1
    game_over = False


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


def collision(shape, x, y):
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c]:
                nx = x + c
                ny = y + r
                if nx < 0 or nx >= COLS:
                    return True
                if ny >= ROWS:
                    return True
                if ny >= 0 and board[ny][nx]:
                    return True
    return False


def place_piece():
    for r in range(len(piece)):
        for c in range(len(piece[r])):
            if piece[r][c]:
                if piece_y + r >= 0:
                    board[piece_y + r][piece_x + c] = piece_color


def clear_lines():
    global board, score, lines_cleared, level, high_score

    new_board = [row for row in board if not all(row)]
    cleared = ROWS - len(new_board)

    # Standard Tetris Scoring System
    score_multipliers = {1: 100, 2: 300, 3: 500, 4: 800}
    if cleared in score_multipliers:
        score += score_multipliers[cleared] * level

    lines_cleared += cleared
    level = (lines_cleared // 10) + 1

    if score > high_score:
        high_score = score

    while len(new_board) < ROWS:
        new_board.insert(0, [0] * COLS)

    board = new_board


reset_game()
fall_timer = 0

# Main Game Loop
while True:
    # Speed up falling as level increases
    fall_speed = max(5, 30 - (level * 2))

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

            if not game_over:
                if event.key == pygame.K_LEFT:
                    if not collision(piece, piece_x - 1, piece_y):
                        piece_x -= 1

                if event.key == pygame.K_RIGHT:
                    if not collision(piece, piece_x + 1, piece_y):
                        piece_x += 1

                if event.key == pygame.K_DOWN:
                    if not collision(piece, piece_x, piece_y + 1):
                        piece_y += 1
                        score += 1  # Soft Drop bonus

                if event.key == pygame.K_UP:
                    new_piece = rotate(piece)
                    if not collision(new_piece, piece_x, piece_y):
                        piece = new_piece

                if event.key == pygame.K_SPACE:
                    drop_bonus = 0
                    while not collision(piece, piece_x, piece_y + 1):
                        piece_y += 1
                        drop_bonus += 2  # Hard Drop bonus
                    score += drop_bonus

    if not game_over:
        fall_timer += 1
        if fall_timer >= fall_speed:
            fall_timer = 0
            if not collision(piece, piece_x, piece_y + 1):
                piece_y += 1
            else:
                place_piece()
                clear_lines()
                piece, piece_color = next_piece, next_color
                next_piece, next_color = get_random_piece()
                piece_x = 3
                piece_y = 0

                if collision(piece, piece_x, piece_y):
                    game_over = True

    # RENDER SCREEN
    screen.fill(COLOR_BG)

    # 1. DRAW BOARD GRID & STACKED BLOCKS
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL, CELL)

            if board[r][c]:
                pygame.draw.rect(screen, board[r][c], rect)
                pygame.draw.rect(screen, COLOR_BG, rect, 1)
            else:
                pygame.draw.rect(screen, COLOR_SIDEBAR, rect)
                pygame.draw.rect(screen, COLOR_GRID, rect, 1)

    # Outer Board Frame
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, COLS * CELL, ROWS * CELL)
    pygame.draw.rect(screen, COLOR_P1, board_rect, 2)

    # 2. DRAW ACTIVE PIECE
    if not game_over:
        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c]:
                    rect = pygame.Rect(
                        BOARD_X + (piece_x + c) * CELL,
                        BOARD_Y + (piece_y + r) * CELL,
                        CELL,
                        CELL
                    )
                    pygame.draw.rect(screen, piece_color, rect)
                    pygame.draw.rect(screen, COLOR_BG, rect, 1)

    # 3. SIDE HUD PANEL
    hud_x = BOARD_X + (COLS * CELL) + 20
    hud_width = WIDTH - hud_x - 20

    # Next Piece Box
    next_box = pygame.Rect(hud_x, BOARD_Y, hud_width, 90)
    pygame.draw.rect(screen, COLOR_SIDEBAR, next_box)
    pygame.draw.rect(screen, COLOR_P2, next_box, 1)

    lbl_next = FONT_HUD.render("NEXT", True, COLOR_P2)
    screen.blit(lbl_next, (hud_x + 10, BOARD_Y + 8))

    for r in range(len(next_piece)):
        for c in range(len(next_piece[r])):
            if next_piece[r][c]:
                # Centered alignment inside preview box
                ox = hud_x + (hud_width // 2) - (len(next_piece[0]) * CELL // 2)
                oy = BOARD_Y + 45 - (len(next_piece) * CELL // 2)
                rect = pygame.Rect(ox + c * CELL, oy + r * CELL, CELL, CELL)
                pygame.draw.rect(screen, next_color, rect)
                pygame.draw.rect(screen, COLOR_BG, rect, 1)

    # Stats HUD Block
    labels_data = [
        ("SCORE", f"{score:06d}", COLOR_P1),
        ("HIGH SCORE", f"{high_score:06d}", COLOR_GOLD),
        ("LEVEL", f"{level:02d}", COLOR_CYAN),
        ("LINES", f"{lines_cleared:03d}", COLOR_TEXT)
    ]

    start_hud_y = BOARD_Y + 110
    for i, (label, value, col) in enumerate(labels_data):
        lbl_surf = FONT_HUD.render(label, True, COLOR_TEXT)
        val_surf = FONT_VALUE.render(value, True, col)
        screen.blit(lbl_surf, (hud_x, start_hud_y + (i * 45)))
        screen.blit(val_surf, (hud_x, start_hud_y + (i * 45) + 16))

    # Controls Text Guide
    guide_lines = ["UP: Rotate", "L/R: Move", "DN: Soft Drop", "SPC: Hard Drop", "R: Restart"]
    for i, txt in enumerate(guide_lines):
        g_surf = FONT_HUD.render(txt, True, COLOR_TEXT)
        screen.blit(g_surf, (hud_x, start_hud_y + 195 + (i * 15)))

    # 4. GAME OVER BANNER
    if game_over:
        banner = FONT_BANNER.render("GAME OVER", True, COLOR_P1)
        sub_banner = FONT_HUD.render("PRESS 'R' TO RESTART", True, COLOR_TEXT)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 18, 210))
        screen.blit(overlay, (0, 0))

        screen.blit(banner, (WIDTH // 2 - banner.get_width() // 2, HEIGHT // 2 - 25))
        screen.blit(sub_banner, (WIDTH // 2 - sub_banner.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.update()
    clock.tick(60)