import pygame
import random
import time

from shapes import shape_list

random.seed(time.time())

random_shapes = True

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
shape_selection = []
selected_shape = None

shape_selection = []
if random_shapes:
    shape_selection = random.sample(shape_list, shape_selection_count)

manual_shape_mode = not random_shapes

score_per_line = [
    0,
    100,
    300,
    600,
    1000,
    1500,
    2500
]

score_per_streak = [
    0,
    250,
    400,
    550,
    700,
    850,
    1000,
    1150,
    1300,
    1450
]

lines_cleared = 0
score = 0
streak = 0

screen_width = block_size * max((board_size + 2), (shape_selection_count * (max_shape_size + 1) + 1))
if random_shapes:
    screen_height = block_size * (board_size + max_shape_size + 3)
else:
    screen_height = block_size * (board_size + (max_shape_size * 2) + 5)

scroll_x = 0

color_index = 0
game_over = False

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

def get_shape_index(block_x, block_y):
    # Check if cursor y is out of range
    if block_y <= board_size + 1 or block_y >= board_size + (max_shape_size + 1):
        return None

    # Check if cursor x is in between gap
    if block_x % (max_shape_size + 1) == 0:
        return None

    # Check which shape is selected by X
    return block_x // (max_shape_size + 1)

def select_shape(index):
    global selected_shape
    selected_shape = shape_selection[index]

def get_manual_shape_index(block_x, block_y):
    # Check if cursor y is out of range
    if block_y <= board_size + max_shape_size + 3 or block_y >= board_size + (2 * max_shape_size) + 4:
        return None

    # Check if cursor x is in between gap
    if block_x % (max_shape_size + 1) == 0:
        return None

    # Check which shape is selected by X
    return (block_x // (max_shape_size + 1)) + (-scroll_x // block_size // (max_shape_size + 1))

def select_manual_shape(index):
    global manual_shape_mode
    global game_over

    shape = shape_list[index]

    shape_selection.append(shape)
    if len(shape_selection) == shape_selection_count:
        game_over = check_game_end()
        manual_shape_mode = False

def put_shape_in_board(board_x, board_y, color):
    num_block_placed = 0

    for row in range(max_shape_size):
        for col in range(max_shape_size):
            if selected_shape[row][col]:
                board[board_y + row][board_x + col] = True
                board_color[board_y + row][board_x + col] = color
                num_block_placed += 1

    return num_block_placed

def place_shape(board_x, board_y):
    global color_index
    global shape_selection
    global selected_shape
    global lines_cleared
    global streak
    global score
    global manual_shape_mode
    global game_over

    num_block_placed = put_shape_in_board(board_x, board_y, color_index)
    shape_selection.remove(selected_shape)
    selected_shape = None

    line_count = clear_lines()
    lines_cleared += line_count
    score += score_per_line[line_count] + score_per_streak[streak] + (num_block_placed * 10)
    if (line_count > 0):
        streak += 1
    else:
        streak = 0

    if len(shape_selection) == 0:
        color_index = (color_index + 1) % block_color_count
        if random_shapes:
            shape_selection = random.sample(shape_list, shape_selection_count)
        else:
            manual_shape_mode = True
    else:
        game_over = check_game_end()

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

def is_placeable(shape, board_x, board_y):
    if board_x < 0 or board_y < 0:
        return False

    for row in range(max_shape_size):
        for col in range(max_shape_size):
            if shape[row][col]:
                try:
                    if board[board_y + row][board_x + col]:
                        return False
                except IndexError:
                    return False

    return True

def check_game_end():
    for shape in shape_selection:
        for row in range(board_size):
            for col in range(board_size):
                if is_placeable(shape, row, col):
                    return False

    return True

def scroll_shape_selection(val):
    global scroll_x

    scroll_x += val * (max_shape_size + 1) * block_size
    scroll_x = min(0, max(scroll_x, -(max_shape_size + 1) * block_size * (len(shape_list) - shape_selection_count)))

def step(action):
    # Place shape
    if action < 100:
        place_shape(action % 10, action // 10)
    # Choose shape
    else:
        select_shape(action - 100)

def handle_event(event):
    global shape_selection
    global selected_shape
    global color_index

    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = pygame.mouse.get_pos()
        block_x, block_y = x // block_size, y // block_size
        board_x, board_y = block_x - 1, block_y - 1

        if manual_shape_mode:
            # Select manual shape
            if event.button == 1:
                index = get_manual_shape_index(block_x, block_y)
                if (index != None):
                    select_manual_shape(index)
            # Remove last manual shape.
            if event.button == 3:
                if (shape_selection):
                    shape_selection.pop()
        else:
            if event.button == 1:
                # Select shape
                if selected_shape == None:
                    index = get_shape_index(block_x, block_y)
                    if (index != None):
                        step(index + 100)
                # Place shape
                elif is_placeable(selected_shape, board_x, board_y):
                    step(board_x + board_y * 10)
                    
            # Remove selected block using right-click
            elif event.button == 3:
                selected_shape = None

    if event.type == pygame.MOUSEWHEEL:
        scroll_shape_selection(event.y)

def draw():
    # Get position in block size
    x, y = pygame.mouse.get_pos()
    block_x = x // block_size
    block_y = y // block_size

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
        # Make selection shape transparent when a shape is picked
        color = block_colors[color_index]
        if (selected_shape != None):
            color = color.lerp(background_color, 0.75)
        draw_shape(shape_selection[i], (i * (max_shape_size + 1) + 1) * block_size, (board_size + 2) * block_size, color)

    # Draw selected shape
    if selected_shape != None:
        # Draw placement guide if placeable
        if is_placeable(selected_shape, block_x - 1, block_y - 1):
            draw_shape(selected_shape, block_x * block_size, block_y * block_size, block_colors[color_index].lerp(background_color, 0.75))

        # Draw selected shape on cursor
        draw_shape(selected_shape, x - (block_size / 2), y - (block_size / 2), block_colors[color_index])

    # Draw all manual selection shapes
    if not random_shapes:
        for i, shape in enumerate(shape_list):
            draw_shape(shape, block_size * (i * (max_shape_size + 1) + 1) + scroll_x, block_size * (board_size + max_shape_size + 4), block_colors[color_index])

    # Draw scroll text
    if not random_shapes:
        scroll_text = font.render(str(-scroll_x // ((max_shape_size + 1) * block_size)), True, border_color)
        screen.blit(scroll_text, (8, block_size * (board_size + max_shape_size + 3)))

    # Draw score
    score_text = font.render("Score: " + str(score), True, border_color)
    screen.blit(score_text, (8, 4))

    # Draw lines cleared
    lines_cleared_text = font.render("Lines: " + str(lines_cleared), True, border_color)
    screen.blit(lines_cleared_text, (168, 4))

    # Draw streak
    streak_text = font.render("Streak: " + str(streak), True, border_color)
    screen.blit(streak_text, (328, 4))

    # Draw game over
    if game_over:
        game_over_text = font.render("Game over!", True, border_color)
        screen.blit(game_over_text, (8, 20))

    # Update display
    pygame.display.flip()

def run():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over:
                continue
            handle_event(event)

        draw()

    pygame.quit()

if __name__ == "__main__":
    run()