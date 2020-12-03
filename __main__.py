import pygame

block_size = 40
board_size = 10
board = [[False for i in range(board_size)] for j in range(board_size)]

screen_width = block_size * (board_size + 2)
screen_height = block_size * (board_size + 2 + 5)

block_color = pygame.Color(0, 200, 240)
border_color = pygame.Color(240, 240, 240)

board[5][2] = True
board[5][3] = True
board[5][4] = True
board[6][3] = True

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("DokuDoku")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw blocks
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col]:
                pygame.draw.rect(screen, block_color, pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size))

    # Draw block border
    for row in range(board_size):
        for col in range(board_size):
            pygame.draw.rect(screen, border_color, pygame.Rect((1 + col) * block_size, (1 + row) * block_size, block_size, block_size), 1)

    pygame.display.flip()