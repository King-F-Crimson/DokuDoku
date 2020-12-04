import pygame
import random
import time

from shapes import shape_list

random.seed(time.time())

block_size = 40
board_size = 10
board = [[False for i in range(board_size)] for j in range(board_size)]
board_color = [[0 for i in range(board_size)] for j in range(board_size)]

max_shape_size = 5

background_color = pygame.Color(0, 0, 0)
border_color = pygame.Color(240, 240, 240)

# Set block colors from HSLA
block_colors = []
block_color_count = 6
color_range = 360 / block_color_count
for i in range(block_color_count):
    color = pygame.Color(0, 0, 0)
    color.hsla = (i * color_range, 80, 50, 100)
    block_colors.append(color)

shape_selection_count = 3
shape_selection = random.sample(shape_list, shape_selection_count)
selected_shape = None

lines_cleared = 0

screen_width = block_size * max((board_size + 2), (shape_selection_count * (max_shape_size + 1) + 1))
screen_height = block_size * (board_size + max_shape_size + 3)

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("DokuDoku")
font = pygame.font.SysFont(None, 24)

def draw_shape(shape, left, top, color):
    for row in range(max_shape_size):
        for col in range(max_shape_size):
            if shape[row][col]:
                pygame.draw.rect(screen, color, pygame.Rect(left + col * block_size, top + row * block_size, block_size, block_size))
                pygame.draw.rect(screen, border_color, pygame.Rect(left + col * block_size, top + row * block_size, block_size, block_size), 1)

def select_shape(event, block_x, block_y):
    # Check if cursor y is out of range
    if block_y <= board_size + 1 or block_y >= board_size + (max_shape_size + 1):
        return None

    # Check if cursor x is in between gap
    if block_x % (max_shape_size + 1) == 0:
        return None

    # Check which shape is selected by X
    try:
        return shape_selection[block_x // (max_shape_size + 1)]
    except IndexError:
        return None

def place_shape(event, block_x, block_y, color):
    for row in range(max_shape_size):
        for col in range(max_shape_size):
            if selected_shape[row][col]:
                board[block_y - 1 + row][block_x - 1 + col] = True
                board_color[block_y - 1 + row][block_x - 1 + col] = color

def clear_lines():
    lines_cleared = 0

    # Find rows to be cleared
    clear_rows = []
    for row in range(board_size):
        row_clear = True
        for col in range(board_size):
            if not board[row][col]:
                row_clear = False
                break
        if row_clear:
            clear_rows.append(row)
            lines_cleared += 1

    # Find cols to be cleared
    clear_cols = []
    for col in range(board_size):
        col_clear = True
        for row in range(board_size):
            if not board[row][col]:
                col_clear = False
                break
        if col_clear:
            clear_cols.append(col)
            lines_cleared += 1

    # Defer clearing so + shaped clear is cleared properly
    for row in clear_rows:
        for col in range(board_size):
            board[row][col] = False

    for col in clear_cols:
        for row in range(board_size):
            board[row][col] = False

    return lines_cleared

def is_placeable(shape, block_x, block_y):
    if block_x == 0 or block_y == 0:
        return False

    for row in range(max_shape_size):
        for col in range(max_shape_size):
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
color_index = 0
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
                        place_shape(event, block_x, block_y, color_index)
                        shape_selection.remove(selected_shape)
                        selected_shape = None
                        lines_cleared += clear_lines()
                        if len(shape_selection) == 0:
                            shape_selection = random.sample(shape_list, shape_selection_count)
                            color_index = (color_index + 1) % block_color_count
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
                pygame.draw.rect(screen, block_colors[board_color[row][col]], pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size))
            pygame.draw.rect(screen, border_color, pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size), 1)

    # Draw shape selection
    for i in range(len(shape_selection)):
        # Make selected shape not drawn
        if (shape_selection[i] != selected_shape):
            draw_shape(shape_selection[i], (i * (max_shape_size + 1) + 1) * block_size, (board_size + 2) * block_size, block_colors[color_index])

    # Draw selected shape
    if selected_shape != None:
        # Draw placement guide if placeable
        if is_placeable(selected_shape, block_x, block_y):
            draw_shape(selected_shape, block_x * block_size, block_y * block_size, block_colors[color_index].lerp(background_color, 0.75))

        # Draw selected shape on cursor
        draw_shape(selected_shape, x - (block_size / 2), y - (block_size / 2), block_colors[color_index])

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