import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DokuDoku")

block_size = 64
board_size = 9
board = [[False] * board_size] * board_size

block_color = pygame.Color(0, 200, 240)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for row in range(board_size):
        for col in range(board_size):
            pygame.draw.rect(screen, block_color, pygame.Rect(col * block_size, row * block_size, block_size, block_size))
    
    pygame.display.flip()