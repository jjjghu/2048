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

def draw_tile(value, x, y):
    pygame.draw.rect(screen, TILE_COLOR, (x, y, 90, 90))
    text = FONT.render(str(value), True, TEXT_COLOR)
    text_rect = text.get_rect(center=(x + 45, y + 45))
    screen.blit(text, text_rect)
def main():
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BACKGROUND_COLOR)
        draw_tile(2, 155, 155)
        pygame.display.flip()
if __name__ == "__main__":
    main()