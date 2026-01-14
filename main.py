import math
import random
import time
import pygame
import sys
import numpy as np

# ----------------------------
# Game constants
# ----------------------------
Funny_mode = True
board_flipped = False

ROWS = 6
COLS = 7
SQUARE = 100
RADIUS = SQUARE // 2 - 5

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

BOARD_WIDTH = COLS * SQUARE
BOARD_HEIGHT = ROWS * SQUARE

OFFSET_X = (WINDOW_WIDTH - BOARD_WIDTH) // 2
OFFSET_Y = (WINDOW_HEIGHT - BOARD_HEIGHT) // 2 + 50  # push down for top bar


BG = (20, 20, 41)          # deep charcoal background
BLACK = (20, 20, 41)
BOARD = (52, 120, 137)    # modern blue board
HOLE = (20, 20, 41)      # dark holes
RED = (199, 75, 38)      # player 1
YELLOW = (244, 184, 64)  # player 2
TEXT = (236, 240, 241)   # off-white text


# ----------------------------
# Initialize pygame
# ----------------------------
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Connect 4")
font = pygame.font.SysFont("arial", 48)

# ----------------------------
# Board functions
# Yellow is 2
# Red is 1
# ----------------------------
def create_board():
    return np.zeros((ROWS, COLS), dtype=int)

def convert_row_col_to_pos(row, col):
    return (OFFSET_X + col * SQUARE + SQUARE // 2, OFFSET_Y + (ROWS - 1 - row) * SQUARE + SQUARE // 2)

def is_valid(board, col):
    return board[ROWS - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    start_row_col = None
    end_row_col = None

    # Horizontal
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c+i] == piece for i in range(4)):
                start_row_col = (r, c)
                end_row_col = (r, c+3)
                return True, start_row_col, end_row_col

    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                start_row_col = (r, c)
                end_row_col = (r+3, c)
                return True, start_row_col, end_row_col

    # Diagonal /
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                start_row_col = (r, c)
                end_row_col = (r+3, c+3)
                return True, start_row_col, end_row_col

    # Diagonal \
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r-i][c+i] == piece for i in range(4)):
                start_row_col = (r, c)
                end_row_col = (r-3, c+3)
                return True, start_row_col, end_row_col

    return False, start_row_col, end_row_col


def create_vignette(size, color, intensity):
    """
    Generates a colored vignette surface programmatically.
    size: A tuple (width, height) for the surface size.
    color: An RGB tuple for the vignette color (e.g., (0, 0, 0) for black).
    intensity: A float (0 to 1) for the vignette's strength/spread.
    """
    vignette_surface = pygame.Surface(size, pygame.SRCALPHA)
    vignette_surface.fill((0, 0, 0, 0))  # Start completely transparent

    width, height = size
    center_x, center_y = width // 2, height // 2
    max_distance = math.sqrt(center_x ** 2 + center_y ** 2)

    scale_size = (100, 100)
    scale_img = pygame.Surface(scale_size, flags=pygame.SRCALPHA)
    for i in range(scale_size[0]):
        for j in range(scale_size[1]):
            # Calculate distance from center normalized to 0-1
            dist = math.sqrt((i - scale_size[0] / 2) ** 2 + (j - scale_size[1] / 2) ** 2)
            max_scale_dist = math.sqrt((scale_size[0] / 2) ** 2 + (scale_size[1] / 2) ** 2)
            # Use smoothstep for a softer fade
            t = min(1, max(0, dist / (max_scale_dist * intensity)))
            # The alpha value is a fade from transparent (center) to opaque (edges)
            alpha = int(t * 255)
            scale_img.set_at((i, j), (color[0], color[1], color[2], alpha))

    # Scale the small image to the full screen size
    scaled_vignette = pygame.transform.smoothscale(scale_img, size)

    # Blit the scaled vignette onto a clean surface with the desired color
    final_vignette = pygame.Surface(size, pygame.SRCALPHA)
    final_vignette.fill(color)  # Fill with the color
    # Use BLEND_RGBA_MIN to take the minimum alpha value for each pixel, preserving the gradient transparency
    final_vignette.blit(scaled_vignette, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return final_vignette

# ----------------------------
# Game setup
# ----------------------------
board = create_board()
turn = 1
game_over = False
vignette_intensity = 3
yellow_vignette_overlay = create_vignette((WINDOW_WIDTH, WINDOW_HEIGHT), YELLOW, vignette_intensity)
red_vignette_overlay = create_vignette((WINDOW_WIDTH, WINDOW_HEIGHT), RED, vignette_intensity)

def draw_board(board):
    screen.fill(BG)
    if turn == 2:
        screen.blit(yellow_vignette_overlay, (0, 0))
    elif turn == 1:
        screen.blit(red_vignette_overlay, (0, 0))

    for c in range(COLS):
        for r in range(ROWS):
            x = OFFSET_X + c * SQUARE
            y = OFFSET_Y + r * SQUARE

            pygame.draw.rect(screen, BOARD, (x, y, SQUARE, SQUARE))
            pygame.draw.circle(
                screen,
                HOLE,
                (x + SQUARE // 2, y + SQUARE // 2),
                RADIUS
            )

    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == 1:
                pygame.draw.circle(
                    screen,
                    RED,
                    (OFFSET_X + c * SQUARE + SQUARE // 2,
                     OFFSET_Y + (ROWS - 1 - r) * SQUARE + SQUARE // 2),
                    RADIUS
                )
            elif board[r][c] == 2:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (OFFSET_X + c * SQUARE + SQUARE // 2,
                     OFFSET_Y + (ROWS - 1 - r) * SQUARE + SQUARE // 2),
                    RADIUS
                )

def drop_piece(board, row, col, pieceID, piece_pos):
    piece = pygame.rect.Rect(0, 0, SQUARE, SQUARE)
    piece.center = piece_pos
    des_x, des_y = convert_row_col_to_pos(row, col)
    increese_rate = 1
    while des_y > piece.centery:
        piece.centery += increese_rate
        if piece.centerx > des_x:
            piece.centerx -= 1
        elif piece.centerx < des_x:
            piece.centerx += 1

        increese_rate *= 1.01

        draw_board(board)
        color = RED if pieceID == 1 else YELLOW
        pygame.draw.circle(screen, color, piece.center, RADIUS)
        pygame.display.update()


    board[row][col] = pieceID

draw_board(board)


# ----------------------------
# Game loop
# ----------------------------
while True:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            draw_board(board)
            posx = event.pos[0]
            color = RED if turn == 1 else YELLOW
            pygame.draw.circle(screen, color, (posx, SQUARE // 2), RADIUS)

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            draw_board(board)
            posx = event.pos[0]
            col = (posx - OFFSET_X) // SQUARE
            if col < 0 or col >= COLS:
                continue

            if is_valid(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, turn, (posx, SQUARE // 2))

                game_won, start, end = winning_move(board, turn)
                if game_won:
                    draw_board(board)
                    label = font.render(
                        f"Player {turn} wins!",
                        True, TEXT
                     )
                    line_start = convert_row_col_to_pos(start[0], start[1])
                    line_end = convert_row_col_to_pos(end[0], end[1])
                    pygame.draw.line(screen, TEXT, line_start, line_end, 6)
                    pygame.display.update()
                    time.sleep(2)
                    end_card_colour = YELLOW if turn == 2 else RED
                    screen.fill((18, 42, 30))
                    screen.blit(label, (WINDOW_WIDTH/2 - label.get_width()/2, WINDOW_HEIGHT/2 - label.get_height()/2))
                    pygame.display.update()
                    time.sleep(2)
                    exit()
                    game_over = True
                elif not 0 in board:
                    draw_board(board)
                    label = font.render(
                        f"The game is a draw",
                        True, TEXT
                     )
                    pygame.display.update()
                    time.sleep(2)
                    screen.fill((18, 42, 30))
                    screen.blit(label, (WINDOW_WIDTH/2 - label.get_width()/2, WINDOW_HEIGHT/2 - label.get_height()/2))
                    pygame.display.update()
                    time.sleep(2)
                    exit()
                    game_over = True

                turn = 2 if turn == 1 else 1
                if Funny_mode:
                    for i in range(len(board)):
                        if random.randint(1,2) == 1:
                            board[i] = board[i][::-1]
                    if random.randint(1, 2) == 1:
                        board = board[::-1]
                        board_flipped = not board_flipped

                    if not 0 in board[len(board)-1]:
                        draw_board(board)
                        label = font.render(
                            f"The game is a draw",
                            True, TEXT
                        )
                        pygame.display.update()
                        time.sleep(2)
                        screen.fill((18, 42, 30))
                        screen.blit(label, (
                        WINDOW_WIDTH / 2 - label.get_width() / 2, WINDOW_HEIGHT / 2 - label.get_height() / 2))
                        pygame.display.update()
                        time.sleep(2)
                        exit()
                draw_board(board)

        pygame.display.update()

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                board = create_board()
                draw_board(board)
                game_over = False
                turn = 1
