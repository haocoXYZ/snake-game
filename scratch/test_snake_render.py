import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 600
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Test Snake Render')

light_green = (170, 215, 81)
dark_green = (162, 209, 73)

dis.fill(light_green)
BLOCK_SIZE = 20
PLAY_Y_START = 40
for x in range(0, WIDTH, BLOCK_SIZE):
    for y in range(PLAY_Y_START, HEIGHT, BLOCK_SIZE):
        col = x // BLOCK_SIZE
        row = (y - PLAY_Y_START) // BLOCK_SIZE
        if (col + row) % 2 != 0:
            pygame.draw.rect(dis, dark_green, [x, y, BLOCK_SIZE, BLOCK_SIZE])

# Profiles with alternating colors
SNAKE_PROFILES = {
    "cobra": {
        "name": "Gold Corn Snake",
        "body": (231, 145, 47),
        "body_alt": (243, 175, 59),
        "head": (200, 115, 30)
    },
    "taipan": {
        "name": "Garden Garter",
        "body": (68, 122, 60),
        "body_alt": (120, 175, 90),
        "head": (50, 95, 43)
    },
    "mamba": {
        "name": "Wild Blackberry",
        "body": (54, 43, 68),
        "body_alt": (110, 80, 130),
        "head": (38, 29, 50)
    }
}

current_snake_id = "cobra"
SNAKE_BODY = SNAKE_PROFILES[current_snake_id]["body"]
SNAKE_BODY_ALT = SNAKE_PROFILES[current_snake_id]["body_alt"]
SNAKE_HEAD = SNAKE_PROFILES[current_snake_id]["head"]

# Draw a snake of length 5 moving right
# Segment list: [tail, ..., head]
snake_list = [
    [100, 200],
    [120, 200],
    [140, 200],
    [160, 200],
    [180, 200]
]

def draw_test_snake(snake_list, dx, dy):
    n = len(snake_list)
    block_size = BLOCK_SIZE
    
    for i, x in enumerate(snake_list):
        is_head = (i == n - 1)
        is_tail = (i == 0)
        
        draw_x = x[0]
        draw_y = x[1]
        
        cx, cy = draw_x + block_size/2, draw_y + block_size/2
        
        if is_head:
            # Bullet shape head
            rect = [int(draw_x - 1), int(draw_y - 1), block_size + 2, block_size + 2]
            
            # Radii based on direction
            if dx > 0:
                r_tl, r_bl, r_tr, r_br = 4, 4, 11, 11
            elif dx < 0:
                r_tl, r_bl, r_tr, r_br = 11, 11, 4, 4
            elif dy > 0:
                r_tl, r_tr, r_bl, r_br = 4, 4, 11, 11
            else: # up or stationary default
                r_tl, r_tr, r_bl, r_br = 11, 11, 4, 4
                
            pygame.draw.rect(
                dis, 
                SNAKE_HEAD, 
                rect, 
                border_top_left_radius=r_tl,
                border_top_right_radius=r_tr,
                border_bottom_left_radius=r_bl,
                border_bottom_right_radius=r_br
            )
            
            # Tiny snout detail or eyes
            ex1, ey1 = cx + 4, cy - 5
            ex2, ey2 = cx + 4, cy + 5
            pygame.draw.circle(dis, (255, 255, 255), (int(ex1), int(ey1)), 4)
            pygame.draw.circle(dis, (255, 255, 255), (int(ex2), int(ey2)), 4)
            pygame.draw.circle(dis, (0, 0, 0), (int(ex1 + 1), int(ey1)), 1)
            pygame.draw.circle(dis, (0, 0, 0), (int(ex2 + 1), int(ey2)), 1)
            
        else:
            # Alternate body segment color
            color = SNAKE_BODY if (i % 2 == 0) else SNAKE_BODY_ALT
            
            # Tapered tail sizing
            if i == 0:
                radius = 6.0
            elif i == 1:
                radius = 8.0
            elif i == 2:
                radius = 9.5
            else:
                radius = 11.0 # overlapping circles
                
            pygame.draw.circle(dis, color, (int(cx), int(cy)), int(radius))
            
            # Distinct decorative spot inside segments
            if current_snake_id == "cobra":
                pygame.draw.circle(dis, (253, 220, 100), (int(cx), int(cy)), int(radius * 0.35))
            elif current_snake_id == "taipan":
                pygame.draw.circle(dis, (235, 225, 170), (int(cx), int(cy)), int(radius * 0.3))
            elif current_snake_id == "mamba":
                pygame.draw.circle(dis, (200, 80, 120), (int(cx), int(cy)), int(radius * 0.3))

draw_test_snake(snake_list, 1, 0)

# Draw a taipan snake (green) at y=300
current_snake_id = "taipan"
SNAKE_BODY = SNAKE_PROFILES[current_snake_id]["body"]
SNAKE_BODY_ALT = SNAKE_PROFILES[current_snake_id]["body_alt"]
SNAKE_HEAD = SNAKE_PROFILES[current_snake_id]["head"]
taipan_list = [
    [100, 300],
    [120, 300],
    [140, 300],
    [160, 300],
    [180, 300]
]
draw_test_snake(taipan_list, 1, 0)

# Draw a mamba snake (purple) at y=400
current_snake_id = "mamba"
SNAKE_BODY = SNAKE_PROFILES[current_snake_id]["body"]
SNAKE_BODY_ALT = SNAKE_PROFILES[current_snake_id]["body_alt"]
SNAKE_HEAD = SNAKE_PROFILES[current_snake_id]["head"]
mamba_list = [
    [100, 400],
    [120, 400],
    [140, 400],
    [160, 400],
    [180, 400]
]
draw_test_snake(mamba_list, 1, 0)

pygame.display.update()
pygame.image.save(dis, "scratch/snake_render_output.png")
pygame.quit()
