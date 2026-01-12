import time

import pygame
import sys
import numpy as np

# ----------------------------
# Game constants
# ----------------------------
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


BG = (18, 22, 28)          # deep charcoal background
BLACK = (255, 255, 255)
BOARD = (33, 116, 255)    # modern blue board
HOLE = (12, 14, 18)      # dark holes
RED = (231, 76, 60)      # player 1
YELLOW = (241, 196, 15)  # player 2
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
# ----------------------------
def create_board():
    return np.zeros((ROWS, COLS), dtype=int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid(board, col):
    return board[ROWS - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS):
        if board[r][col] == 0:
            return r

def draw_board(board):
    screen.fill(BG)

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

    pygame.display.update()


def winning_move(board, piece):
    # Horizontal
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c+i] == piece for i in range(4)):
                return True

    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True

    # Diagonal /
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True

    # Diagonal \
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True

    return False

# ----------------------------
# Game setup
# ----------------------------
board = create_board()
turn = 1
game_over = False
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
            pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH
, SQUARE))
            posx = event.pos[0]
            color = RED if turn == 1 else YELLOW
            pygame.draw.circle(screen, color, (posx, SQUARE // 2), RADIUS)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH
, SQUARE))
            posx = event.pos[0]
            col = (posx - OFFSET_X) // SQUARE
            if col < 0 or col >= COLS:
                continue

            if is_valid(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, turn)

                if winning_move(board, turn):
                    label = font.render(
                        f"Player {turn} wins!",
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
                draw_board(board)

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                board = create_board()
                draw_board(board)
                game_over = False
                turn = 1
