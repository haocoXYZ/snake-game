import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600
PLAY_Y_START = 40

dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Test Drawing')

# Checkerboard colors
light_green = (170, 215, 81)
dark_green = (162, 209, 73)

# Fill background with checkerboard
dis.fill(light_green)
BLOCK_SIZE = 20
for x in range(0, WIDTH, BLOCK_SIZE):
    for y in range(PLAY_Y_START, HEIGHT, BLOCK_SIZE):
        col = x // BLOCK_SIZE
        row = (y - PLAY_Y_START) // BLOCK_SIZE
        if (col + row) % 2 != 0:
            pygame.draw.rect(dis, dark_green, [x, y, BLOCK_SIZE, BLOCK_SIZE])

def draw_instruction_graphic(cx, cy):
    # Main panel (dark green rounded square)
    pygame.draw.rect(dis, (48, 85, 33), [cx - 80, cy - 80, 160, 160], border_radius=28)
    
    # Keyboard center for arrows
    kx = cx - 17
    ky = cy - 15
    
    # Draw arrow keys (white squares with dark green triangles)
    keys = {
        'up': [kx, ky - 28, 24, 24],
        'down': [kx, ky, 24, 24],
        'left': [kx - 28, ky, 24, 24],
        'right': [kx + 28, ky, 24, 24]
    }
    
    for key_dir, rect in keys.items():
        pygame.draw.rect(dis, (255, 255, 255), rect, border_radius=5)
        
        # Triangles pointing in respective directions
        rx, ry, rw, rh = rect
        kx_c = rx + rw // 2
        ky_c = ry + rh // 2
        
        if key_dir == 'up':
            pts = [(kx_c, ky_c - 6), (kx_c - 5, ky_c + 4), (kx_c + 5, ky_c + 4)]
        elif key_dir == 'down':
            pts = [(kx_c, ky_c + 6), (kx_c - 5, ky_c - 4), (kx_c + 5, ky_c - 4)]
        elif key_dir == 'left':
            pts = [(kx_c - 6, ky_c), (kx_c + 4, ky_c - 5), (kx_c + 4, ky_c + 5)]
        elif key_dir == 'right':
            pts = [(kx_c + 6, ky_c), (kx_c - 4, ky_c - 5), (kx_c - 4, ky_c + 5)]
            
        pygame.draw.polygon(dis, (48, 85, 33), pts)

    # Draw hand pointer on the right side of the keys, pointing to the Right key
    hx = kx + 40
    hy = ky + 34
    
    # Hand silhouette in white
    # Index finger pointing straight up:
    pygame.draw.rect(dis, (255, 255, 255), [hx - 5, hy - 32, 10, 35], border_radius=5)
    # Palm/Base:
    pygame.draw.rect(dis, (255, 255, 255), [hx - 7, hy, 26, 28], border_radius=10)
    # Folded fingers block:
    pygame.draw.rect(dis, (255, 255, 255), [hx + 3, hy - 14, 18, 32], border_radius=8)
    # Thumb pointing up-left:
    pygame.draw.rect(dis, (255, 255, 255), [hx - 18, hy + 2, 14, 10], border_radius=5)
    # Smooth connection circle:
    pygame.draw.circle(dis, (255, 255, 255), (hx - 10, hy + 7), 6)
    # Wrist extending to bottom:
    pygame.draw.rect(dis, (255, 255, 255), [hx - 4, hy + 20, 18, 37], border_radius=2)

# Render at center
draw_instruction_graphic(400, 320)

pygame.display.update()
pygame.image.save(dis, "scratch/test_output.png")
pygame.quit()
