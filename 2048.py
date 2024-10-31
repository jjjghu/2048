import pygame
import sys

pygame.init()
WINDOW_SIZE = (400, 400)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('2048')

BACKGROUND_COLOR = (187, 174, 160)
TILE_COLOR = (238, 238, 238)
TEXT_COLOR = (119, 110, 101)

FONT = pygame.font.Font(None, 72)

GRID_SIZE = 4
GRID_PADDING = 10
GRID_WIDTH = WINDOW_SIZE[0] // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE[1] // GRID_SIZE

def draw_grid():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            pygame.draw.rect(screen, TILE_COLOR, (j * GRID_WIDTH, i * GRID_HEIGHT, GRID_WIDTH - GRID_PADDING, GRID_HEIGHT - GRID_PADDING))

def draw_tile(value, x, y):
    pygame.draw.rect(screen, TILE_COLOR, (x, y, GRID_WIDTH - GRID_PADDING, GRID_HEIGHT - GRID_PADDING))
    text = FONT.render(str(value), True, TEXT_COLOR)
    text_rect = text.get_rect(center=(x + GRID_WIDTH // 2, y + GRID_HEIGHT // 2))
    screen.blit(text, text_rect)

def main():
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_tile(2, GRID_WIDTH * (GRID_SIZE - 1), GRID_HEIGHT * (GRID_SIZE - 1))
        pygame.display.flip()

if __name__ == "__main__":
    main()