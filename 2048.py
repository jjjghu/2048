import pygame
import sys
import random

# 初始化 Pygame
pygame.init()
WINDOW_SIZE = (400, 500)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('2048')

# 顏色設置
BACKGROUND_COLOR = (187, 173, 160)
TILE_COLOR = (205, 193, 180)
SPECIAL_TILE_COLOR = (238, 228, 218)
TEXT_COLOR = (119, 110, 101)
SCOREBOARD_COLOR = (119, 110, 101)

# 字體設定
FONT = pygame.font.Font(None, 55)
SCORE_FONT = pygame.font.Font(None, 40)

# 網格大小與間距
GRID_SIZE = 4
GRID_PADDING = 15
GRID_TOP_MARGIN = 100
GRID_WIDTH = (WINDOW_SIZE[0] - GRID_PADDING * (GRID_SIZE + 1)) // GRID_SIZE
GRID_HEIGHT = (WINDOW_SIZE[1] - GRID_PADDING * (GRID_SIZE + 1) - GRID_TOP_MARGIN) // GRID_SIZE

# 初始化遊戲網格
grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

# 初始化分數
score = 0

# 为每个数字定义颜色
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

# 默认颜色（用于未定义的数字）
DEFAULT_TILE_COLOR = (205, 193, 180)

# 畫記分欄
def draw_scoreboard():
    score_text = SCORE_FONT.render(f'Score: {score}', True, SCOREBOARD_COLOR)
    score_rect = score_text.get_rect(center=(WINDOW_SIZE[0] // 2, GRID_TOP_MARGIN // 2))
    screen.blit(score_text, score_rect)

# 畫網格
def draw_grid():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = GRID_PADDING + j * (GRID_WIDTH + GRID_PADDING)
            y = GRID_TOP_MARGIN + GRID_PADDING + i * (GRID_HEIGHT + GRID_PADDING)
            pygame.draw.rect(screen, TILE_COLOR, (x, y, GRID_WIDTH, GRID_HEIGHT))

# 畫數字方塊
def draw_tile(value, row, col):
    if value == 0:
        return
    x = GRID_PADDING + col * (GRID_WIDTH + GRID_PADDING)
    y = GRID_TOP_MARGIN + GRID_PADDING + row * (GRID_HEIGHT + GRID_PADDING)
    
    # 使用 TILE_COLORS 字典获取颜色，如果没有定义则使用默认颜色
    tile_color = TILE_COLORS.get(value, DEFAULT_TILE_COLOR)
    
    pygame.draw.rect(screen, tile_color, (x, y, GRID_WIDTH, GRID_HEIGHT))
    
    # 根据数字大小调整字体大小
    font_size = 55 if value < 100 else 45 if value < 1000 else 35
    font = pygame.font.Font(None, font_size)
    
    # 根据背景颜色选择文字颜色
    text_color = TEXT_COLOR if value < 8 else (249, 246, 242)  # 深色背景使用浅色文字
    
    text = font.render(str(value), True, text_color)
    text_rect = text.get_rect(center=(x + GRID_WIDTH // 2, y + GRID_HEIGHT // 2))
    screen.blit(text, text_rect)

# 隨機生成新方塊
def spawn_new_tile():
    empty_tiles = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if not empty_tiles:
        return
    row, col = random.choice(empty_tiles)
    grid[row][col] = random.choice([2, 4])

# 移動並合併方塊
def move_and_merge(direction):
    global score
    moved = False
    
    def slide_row_left(row):
        global score
        nonlocal moved
        new_row = [v for v in row if v != 0]
        for i in range(len(new_row) - 1):
            if new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                score += new_row[i]
                new_row[i + 1] = 0
                moved = True
        new_row = [v for v in new_row if v != 0]
        padded_row = new_row + [0] * (GRID_SIZE - len(new_row))
        if padded_row != row:  # 检查是否发生了移动
            moved = True
        return padded_row

    for i in range(GRID_SIZE):
        if direction == 'LEFT':
            grid[i] = slide_row_left(grid[i])
        elif direction == 'RIGHT':
            grid[i] = list(reversed(slide_row_left(list(reversed(grid[i])))))
        elif direction == 'UP':
            col = [grid[r][i] for r in range(GRID_SIZE)]
            new_col = slide_row_left(col)
            for r in range(GRID_SIZE):
                if grid[r][i] != new_col[r]:  # 检查列是否发生了变化
                    moved = True
                grid[r][i] = new_col[r]
        elif direction == 'DOWN':
            col = [grid[r][i] for r in range(GRID_SIZE)]
            new_col = list(reversed(slide_row_left(list(reversed(col)))))
            for r in range(GRID_SIZE):
                if grid[r][i] != new_col[r]:  # 检查列是否发生了变化
                    moved = True
                grid[r][i] = new_col[r]
    
    if moved:
        spawn_new_tile()  # 生成新的随机方块
  # 生成新的隨機方塊

# 主函數
def main():
    global score
    spawn_new_tile()
    spawn_new_tile()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_and_merge('UP')
                elif event.key == pygame.K_DOWN:
                    move_and_merge('DOWN')
                elif event.key == pygame.K_LEFT:
                    move_and_merge('LEFT')
                elif event.key == pygame.K_RIGHT:
                    move_and_merge('RIGHT')
        
        # 畫圖
        screen.fill(BACKGROUND_COLOR)
        draw_scoreboard()
        draw_grid()
        
        # 畫數字方塊
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                draw_tile(grid[i][j], i, j)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
