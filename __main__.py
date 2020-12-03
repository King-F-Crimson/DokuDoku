import pygame
import random

random.seed(8)

block_size = 40
board_size = 10
board = [[False for i in range(board_size)] for j in range(board_size)]

screen_width = block_size * (board_size + 2 + 5)
screen_height = block_size * (board_size + 2 + 5)

background_color = pygame.Color(0, 0, 0)
block_color = pygame.Color(0, 200, 240)
transparent_block_color = pygame.Color(0, 50, 60)
border_color = pygame.Color(240, 240, 240)

shape_list = [
    # O block.
    [
        [True, True, False, False],
        [True, True, False, False],
        [False, False, False, False],
        [False, False, False, False],
    ],
    [
        [True, True, False, False],
        [False, True, True, False],
        [False, False, False, False],
        [False, False, False, False],
    ],
    [
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False],
        [True, False, False, False],
    ],
    [
        [True, True, True, False],
        [True, False, False, False],
        [True, False, False, False],
        [False, False, False, False],
    ],
]
shape_selection_count = 3

board[5][2] = True
board[5][3] = True
board[5][4] = True
board[6][3] = True

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("DokuDoku")

shape_selection = []
for i in range(shape_selection_count):
    shape_selection.append(random.choice(shape_list))

selected_shape = None

def draw_shape(shape, left, top, color):
    for row in range(4):
        for col in range(4):
            if shape[row][col]:
                pygame.draw.rect(screen, color, pygame.Rect(left + col * block_size, top + row * block_size, block_size, block_size))
                pygame.draw.rect(screen, border_color, pygame.Rect(left + col * block_size, top + row * block_size, block_size, block_size), 1)

def select_shape(event):
    x, y = event.pos
    block_x = x // block_size
    block_y = y // block_size

    # Check if cursor y is out of range
    if block_y <= board_size + 1 or block_y >= board_size + 5:
        return

    # Check which shape is selected by X
    global selected_shape
    if block_x >= 1 and block_x <= 5:
        selected_shape = shape_selection[0]
    elif block_x >= 6 and block_x <= 10:
        selected_shape = shape_selection[1]
    elif block_x >= 11 and block_x <= 15:
        selected_shape = shape_selection[2]

def place_shape(event):
    x, y = event.pos
    block_x = x // block_size
    block_y = y // block_size

    global selected_shape
    for row in range(4):
        for col in range(4):
            if selected_shape[row][col]:
                board[block_y - 1 + row][block_x - 1 + col] = True

    selected_shape = None

def is_placeable():
    x, y = pygame.mouse.get_pos()
    block_x = x // block_size
    block_y = y // block_size

    return True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if selected_shape == None:
                    select_shape(event)
                elif is_placeable():
                    place_shape(event)

    screen.fill(background_color)

    # Draw blocks
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col]:
                pygame.draw.rect(screen, block_color, pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size))
            pygame.draw.rect(screen, border_color, pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size), 1)

    # Draw shape selection
    for i in range(shape_selection_count):
        draw_shape(shape_selection[i], (i * 5 + 1) * block_size, (board_size + 2) * block_size, block_color)

    # Draw selected shape
    if selected_shape != None:
        x, y = pygame.mouse.get_pos()
        block_x = x // block_size
        block_y = y // block_size

        # Draw placement guide
        draw_shape(selected_shape, block_x * block_size, block_y * block_size, transparent_block_color)

        # Draw selected shape on cursor
        draw_shape(selected_shape, x - (block_size / 2), y - (block_size / 2), block_color)

    pygame.display.flip()