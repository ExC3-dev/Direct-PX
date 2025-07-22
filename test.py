import directpx
import random
import time
import ctypes

# Windows API: capture keypresses without triggering Windows
user32 = ctypes.windll.user32
VK_LEFT, VK_UP, VK_RIGHT, VK_DOWN = 0x25, 0x26, 0x27, 0x28
VK_SPACE, VK_CONTROL = 0x20, 0x11

def is_pressed(vk):
    return user32.GetAsyncKeyState(vk) & 0x8000 != 0

def move_mouse_and_click(x, y):
    user32.SetCursorPos(x, y)
    user32.mouse_event(2, 0, 0, 0, 0)  # Mouse left down
    user32.mouse_event(4, 0, 0, 0, 0)  # Mouse left up

screen_w, screen_h = directpx.get_screen_size()

cols = round(screen_w/20)
rows = round(screen_h/20)

cell_w = screen_w // cols
cell_h = screen_h // rows

directpx.init(screen_w, screen_h)

snake = [(5, 5)]
direction = (1, 0)
food = (10, 10)
score = 0

def draw_box_cell(x, y, r, g, b):
    directpx.draw_box(x * cell_w, y * cell_h, cell_w, cell_h, r, g, b, 255)

def draw_score(score):
    directpx.draw_text(5, 5, f"SCORE: {score}", 255, 255, 255)

def get_input_dir(current):
    if is_pressed(VK_UP) and current != (0, 1): return (0, -1)
    if is_pressed(VK_DOWN) and current != (0, -1): return (0, 1)
    if is_pressed(VK_LEFT) and current != (1, 0): return (-1, 0)
    if is_pressed(VK_RIGHT) and current != (-1, 0): return (1, 0)
    return current

# Game loop
while True:
    try:
        direction = get_input_dir(direction)
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Click on snake head if CTRL or SPACE
        if is_pressed(VK_CONTROL):
            head_x = snake[0][0] * cell_w + cell_w // 2
            head_y = snake[0][1] * cell_h + cell_h // 2
            move_mouse_and_click(head_x, head_y)
            time.sleep(0.2)

        if (
            head in snake or
            head[0] < 0 or head[0] >= cols or
            head[1] < 0 or head[1] >= rows
        ):
            snake = [(5, 5)]
            direction = (1, 0)
            food = (random.randint(0, cols - 1), random.randint(0, rows - 1))
            score = 0
            time.sleep(0.5)
            continue

        snake.insert(0, head)
        if head == food:
            score += 1
            while True:
                food = (random.randint(0, cols - 1), random.randint(0, rows - 1))
                if food not in snake:
                    break
        else:
            snake.pop()

        # Draw everything
        directpx.clear()
        for x, y in snake:
            draw_box_cell(x, y, 0, 255, 0)
        draw_box_cell(food[0], food[1], 255, 0, 0)
        draw_score(score)
        directpx.update()
        time.sleep(0.1)

    except KeyboardInterrupt:
        break
