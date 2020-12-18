import pygame
import random
import time

from shapes import shape_list

class Game:
    def __init__(self):
        # Board settings
        self.board_size = 10
        self.shape_size = 5

        # Display settings
        self.block_size = 40            # Size for each block in pixel
        self.background_color = pygame.Color(0, 0, 0)
        self.border_color = pygame.Color(240, 240, 240)

        # Shape selection settings
        self.random_shapes = True      # Set to False to choose the shapes manually
        self.shape_selection_count = 3

        # Scoring settings
        self.score_per_line = [
            0,
            100,
            300,
            600,
            1000,
            1500,
            2500
        ]
        self.score_per_streak = [
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

        # Setup block colors
        self.block_colors = []
        self.block_color_count = 6
        color_range = 360 / self.block_color_count
        for i in range(self.block_color_count):
            color = pygame.Color(0, 0, 0)
            color.hsla = (i * color_range, 80, 50, 100)
            self.block_colors.append(color)

        # Setup display
        screen_width = self.block_size * max((self.board_size + 2), (self.shape_selection_count * (self.shape_size + 1) + 1))
        if self.random_shapes:
            screen_height = self.block_size * (self.board_size + self.shape_size + 3)
        else:
            # Add extra screen height for manual shape selection
            screen_height = self.block_size * (self.board_size + (self.shape_size * 2) + 5)
        self.scroll_x = 0
        self.color_index = 0

        self.start()

        # Initialize pygame
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("DokuDoku")

    def start(self):
        # Initialize board
        self.board = [[False for i in range(self.board_size)] for j in range(self.board_size)]   # Block is filled if True
        self.board_color = [[0 for i in range(self.board_size)] for j in range(self.board_size)] # Block color

        # Initialize shape selection
        self.manual_shape_mode = not self.random_shapes
        self.selected_shape = None
        self.shape_selection = []
        if self.random_shapes:
            self.shape_selection = random.sample(shape_list, self.shape_selection_count)

        # Initialize scoring
        self.lines_cleared = 0
        self.score = 0
        self.streak = 0
        self.game_over = False

    def draw_shape(self, shape, left, top, color):
        for row in range(self.shape_size):
            for col in range(self.shape_size):
                if shape[row][col]:
                    pygame.draw.rect(self.screen, color, pygame.Rect(left + col * self.block_size, top + row * self.block_size, self.block_size, self.block_size))
                    pygame.draw.rect(self.screen, self.border_color, pygame.Rect(left + col * self.block_size, top + row * self.block_size, self.block_size, self.block_size), 1)

    def get_shape_index(self, block_x, block_y):
        # Check if cursor y is out of range
        if block_y <= self.board_size + 1 or block_y >= self.board_size + (self.shape_size + 1):
            return None

        # Check if cursor x is in between gap
        if block_x % (self.shape_size + 1) == 0:
            return None

        # Check which shape is selected by X
        return block_x // (self.shape_size + 1)

    def select_shape(self, index):
        try:
            self.selected_shape = self.shape_selection[index]
        except IndexError:
            return False
        else:
            return True

    def get_manual_shape_index(self, block_x, block_y):
        # Check if cursor y is out of range
        if block_y <= self.board_size + self.shape_size + 3 or block_y >= self.board_size + (2 * self.shape_size) + 4:
            return None

        # Check if cursor x is in between gap
        if block_x % (self.shape_size + 1) == 0:
            return None

        # Check which shape is selected by X
        return (block_x // (self.shape_size + 1)) + (-self.scroll_x // self.block_size // (self.shape_size + 1))

    def select_manual_shape(self, index):
        shape = shape_list[index]

        self.shape_selection.append(shape)
        if len(self.shape_selection) == self.shape_selection_count:
            self.game_over = self.check_game_end()
            self.manual_shape_mode = False

    def put_shape_in_board(self, board_x, board_y, color):
        num_block_placed = 0

        for row in range(self.shape_size):
            for col in range(self.shape_size):
                if self.selected_shape[row][col]:
                    self.board[board_y + row][board_x + col] = True
                    self.board_color[board_y + row][board_x + col] = color
                    num_block_placed += 1

        return num_block_placed

    def place_shape(self, board_x, board_y):
        # Check if placeable
        if self.selected_shape == None or not self.is_placeable(self.selected_shape, board_x, board_y):
            return False, 0

        num_block_placed = self.put_shape_in_board(board_x, board_y, self.color_index)
        self.shape_selection.remove(self.selected_shape)
        self.selected_shape = None

        line_count = self.clear_lines()
        score = self.score_per_line[line_count] + self.score_per_streak[self.streak] + (num_block_placed * 10)
        self.lines_cleared += line_count
        self.score += score
        if (line_count > 0):
            self.streak += 1
        else:
            self.streak = 0

        if len(self.shape_selection) == 0:
            self.color_index = (self.color_index + 1) % self.block_color_count
            if self.random_shapes:
                self.shape_selection = random.sample(shape_list, self.shape_selection_count)
                self.game_over = self.check_game_end()
            else:
                self.manual_shape_mode = True
        else:
            self.game_over = self.check_game_end()

        return True, score

    def clear_lines(self):
        line_count = 0

        # Find rows to be cleared
        clear_rows = []
        for row in range(self.board_size):
            row_clear = True
            for col in range(self.board_size):
                if not self.board[row][col]:
                    row_clear = False
                    break
            if row_clear:
                clear_rows.append(row)
                line_count += 1

        # Find cols to be cleared
        clear_cols = []
        for col in range(self.board_size):
            col_clear = True
            for row in range(self.board_size):
                if not self.board[row][col]:
                    col_clear = False
                    break
            if col_clear:
                clear_cols.append(col)
                line_count += 1

        # Defer self, clearing so + shaped clear is cleared properly
        for row in clear_rows:
            for col in range(self.board_size):
                self.board[row][col] = False

        for col in clear_cols:
            for row in range(self.board_size):
                self.board[row][col] = False

        return line_count

    def is_placeable(self, shape, board_x, board_y):
        if board_x < 0 or board_y < 0:
            return False

        for row in range(self.shape_size):
            for col in range(self.shape_size):
                if shape[row][col]:
                    try:
                        if self.board[board_y + row][board_x + col]:
                            return False
                    except IndexError:
                        return False

        return True

    def is_shape_placeable(self, shape):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_placeable(shape, row, col):
                    return True

        return False

    def check_game_end(self):
        for shape in self.shape_selection:
            if self.is_shape_placeable(shape):
                return False

        return True

    def scroll_shape_selection(self, val):
        self.scroll_x += val * (self.shape_size + 1) * self.block_size
        self.scroll_x = min(0, max(self.scroll_x, -(self.shape_size + 1) * self.block_size * (len(shape_list) - self.shape_selection_count)))

    def step(self, action):
        # Place shape
        if action < 100:
            success, score = self.place_shape(action % 10, action // 10)
            if success:
                return score
            else:
                return -1
        # Choose shape
        else:
            success = self.select_shape(action - 100)
            if success:
                return 1
            else:
                return -1

    def handle_player_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            block_x, block_y = x // self.block_size, y // self.block_size
            board_x, board_y = block_x - 1, block_y - 1

            if self.manual_shape_mode:
                # Select manual shape
                if event.button == 1:
                    index = self.get_manual_shape_index(block_x, block_y)
                    if (index != None):
                        self.select_manual_shape(index)
                # Remove last manual shape.
                if event.button == 3:
                    if (self.shape_selection):
                        self.shape_selection.pop()
            else:
                if event.button == 1:
                    # Select shape
                    if self.selected_shape == None:
                        index = self.get_shape_index(block_x, block_y)
                        if (index != None):
                            self.step(index + 100)
                    # Place shape
                    elif self.is_placeable(self.selected_shape, board_x, board_y):
                        self.step(board_x + board_y * 10)
                        
                # Remove selected block using right-click
                elif event.button == 3:
                    self.selected_shape = None

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_shape_selection(event.y)

    def draw(self):
        # Get position in block size
        x, y = pygame.mouse.get_pos()
        block_x = x // self.block_size
        block_y = y // self.block_size

        # Drawing
        # Reset screen with background color
        self.screen.fill(self.background_color)

        # Draw blocks
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col]:
                    pygame.draw.rect(self.screen, self.block_colors[self.board_color[row][col]], pygame.Rect((1 + col) * self.block_size, (1 + row) * self.block_size, self.block_size, self.block_size))
                pygame.draw.rect(self.screen, self.border_color, pygame.Rect((1 + col) * self.block_size, (1 + row) * self.block_size, self.block_size, self.block_size), 1)

        # Draw shape selection
        for i in range(len(self.shape_selection)):
            # Make selection shape transparent when a shape is picked
            color = self.block_colors[self.color_index]
            if (self.selected_shape != None):
                color = color.lerp(self.background_color, 0.75)
            self.draw_shape(self.shape_selection[i], (i * (self.shape_size + 1) + 1) * self.block_size, (self.board_size + 2) * self.block_size, color)

        # Draw selected shape
        if self.selected_shape != None:
            # Draw placement guide if placeable
            if self.is_placeable(self.selected_shape, block_x - 1, block_y - 1):
                self.draw_shape(self.selected_shape, block_x * self.block_size, block_y * self.block_size, self.block_colors[self.color_index].lerp(self.background_color, 0.75))

            # Draw selected shape on cursor
            self.draw_shape(self.selected_shape, x - (self.block_size / 2), y - (self.block_size / 2), self.block_colors[self.color_index])

        # Draw all manual selection shapes
        if not self.random_shapes:
            for i, shape in enumerate(shape_list):
                self.draw_shape(shape, self.block_size * (i * (self.shape_size + 1) + 1) + self.scroll_x, self.block_size * (self.board_size + self.shape_size + 4), self.block_colors[self.color_index])

        # Draw scroll text
        if not self.random_shapes:
            scroll_text = self.font.render(str(-self.scroll_x // ((self.shape_size + 1) * self.block_size)), True, self.border_color)
            self.screen.blit(scroll_text, (8, self.block_size * (self.board_size + self.shape_size + 3)))

        # Draw score
        score_text = self.font.render("Score: " + str(self.score), True, self.border_color)
        self.screen.blit(score_text, (8, 4))

        # Draw lines cleared
        lines_cleared_text = self.font.render("Lines: " + str(self.lines_cleared), True, self.border_color)
        self.screen.blit(lines_cleared_text, (168, 4))

        # Draw streak
        streak_text = self.font.render("Streak: " + str(self.streak), True, self.border_color)
        self.screen.blit(streak_text, (328, 4))

        # Draw game over
        if self.game_over:
            self.game_over_text = self.font.render("Game over!", True, self.border_color)
            self.screen.blit(self.game_over_text, (8, 20))

        # Update display
        pygame.display.flip()

    def run(self, agent=None):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if not self.game_over:
                    self.handle_player_input(event)

            if agent != None:
                reward = self.step(agent.get_action())
                agent.set_reward(reward)

            self.draw()

            if self.game_over:
                time.sleep(1)
                self.start()

        pygame.quit()


if __name__ == "__main__":
    random.seed(time.time())

    game = Game()
    game.run()