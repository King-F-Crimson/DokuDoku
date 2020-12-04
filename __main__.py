import pygame
import random
import time

from shapes import shape_list

random.seed(time.time())

block_size = 40
board_size = 10
board = [[False for i in range(board_size)] for j in range(board_size)]

screen_width = block_size * (board_size + 2 + 5)
screen_height = block_size * (board_size + 2 + 5)

background_color = pygame.Color(0, 0, 0)
border_color = pygame.Color(240, 240, 240)

# Set block colors from HSLA
block_colors = []
transparent_block_colors = []
block_color_count = 12
color_range = 360 / block_color_count
for i in range(block_color_count):
    color = pygame.Color(0, 0, 0)
    color.hsla = (i * color_range, 80, 50, 100)
    block_colors.append(color)
    transparent_block_colors.append(color.lerp(background_color, 0.75))

shape_selection_count = 3
shape_selection = random.sample(shape_list, 3)
selected_shape = None

lines_cleared = 0

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("DokuDoku")
font = pygame.font.SysFont(None, 24)

def draw_shape(shape, left, top, color):
    for row in range(4):
        for col in range(4):
            if shape[row][col]:
                pygame.draw.rect(screen, color, pygame.Rect(left + col * block_size, top + row * block_size, block_size, block_size))
                pygame.draw.rect(screen, border_color, pygame.Rect(left + col * block_size, top + row * block_size, block_size, block_size), 1)

def select_shape(event, block_x, block_y):
    # Check if cursor y is out of range
    if block_y <= board_size + 1 or block_y >= board_size + 5:
        return None

    # Check which shape is selected by X
    if block_x >= 1 and block_x <= 5:
        return shape_selection[0]
    elif block_x >= 6 and block_x <= 10:
        return shape_selection[1]
    elif block_x >= 11 and block_x <= 15:
        return shape_selection[2]

def place_shape(event, block_x, block_y):
    for row in range(4):
        for col in range(4):
            if selected_shape[row][col]:
                board[block_y - 1 + row][block_x - 1 + col] = True

def clear_lines():
    lines_cleared = 0

    # Clear rows
    for row in range(board_size):
        row_clear = True
        for col in range(board_size):
            if not board[row][col]:
                row_clear = False
                break
        if row_clear:
            for col in range(board_size):
                board[row][col] = False
            lines_cleared += 1

    # Clear cols
    for col in range(board_size):
        col_clear = True
        for row in range(board_size):
            if not board[row][col]:
                col_clear = False
                break
        if col_clear:
            for row in range(board_size):
                board[row][col] = False
            lines_cleared += 1

    return lines_cleared

def is_placeable(shape, block_x, block_y):
    if block_x == 0 or block_y == 0:
        return False

    for row in range(4):
        for col in range(4):
            if shape[row][col]:
                try:
                    if board[block_y - 1 + row][block_x - 1 + col]:
                        return False
                except IndexError:
                    return False

    return True

def check_game_end():
    for shape in shape_selection:
        for row in range(board_size):
            for col in range(board_size):
                if is_placeable(shape, 1 + row, 1 + col):
                    return False

    return True

running = True
game_over = False
while running:
    # Get position in block size
    x, y = pygame.mouse.get_pos()
    block_x = x // block_size
    block_y = y // block_size

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Select shape
                    if selected_shape == None:
                        selected_shape = select_shape(event, block_x, block_y)
                    # Place shape
                    elif is_placeable(selected_shape, block_x, block_y):
                        place_shape(event, block_x, block_y)
                        selected_shape = None
                        lines_cleared += clear_lines()
                        shape_selection = random.sample(shape_list, 3)
                        game_over = check_game_end()
                # Remove selected block using right-click
                elif event.button == 3:
                    selected_shape = None

    # Drawing
    # Reset screen with background color
    screen.fill(background_color)

    # Draw blocks
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col]:
                pygame.draw.rect(screen, block_colors[0], pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size))
            pygame.draw.rect(screen, border_color, pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size), 1)

    # Draw shape selection
    for i in range(shape_selection_count):
        draw_shape(shape_selection[i], (i * 5 + 1) * block_size, (board_size + 2) * block_size, block_colors[0])

    # Draw selected shape
    if selected_shape != None:
        # Draw placement guide if placeable
        if is_placeable(selected_shape, block_x, block_y):
            draw_shape(selected_shape, block_x * block_size, block_y * block_size, transparent_block_colors[0])

        # Draw selected shape on cursor
        draw_shape(selected_shape, x - (block_size / 2), y - (block_size / 2), block_colors[0])

    # Draw score
    score = font.render(str(lines_cleared), True, border_color)
    screen.blit(score, (8, 4))

    # Draw game over
    if game_over:
        game_over_text = font.render("Game over!", True, border_color)
        screen.blit(game_over_text, (8, 20))

    # Update display
    pygame.display.flip()

pygame.quit()