import pygame
import random
import sys
import json
import os
import asyncio

pygame.init()

# Change directory to script's directory to resolve relative paths for web assets
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# --- Jungle Theme Colors ---
BG_COLOR = (15, 40, 15)
GRID_COLOR = (25, 55, 25)
FOOD_COLOR = (231, 76, 60)
OBSTACLE_COLOR = (139, 69, 19)
OBSTACLE_INNER = (101, 50, 14)
SCORE_BG = (10, 25, 10)
SCORE_LINE = (39, 174, 96)
TEXT_COLOR = (241, 196, 15)

SNAKE_PROFILES = {
    "cobra": {
        "name": "King Cobra",
        "body": (218, 165, 32),   # Goldenrod
        "head": (184, 134, 11)    # Dark goldenrod
    },
    "taipan": {
        "name": "Inland Taipan",
        "body": (107, 142, 35),   # Olive Drab
        "head": (85, 107, 47)     # Dark Olive Green
    },
    "mamba": {
        "name": "Black Mamba",
        "body": (60, 60, 60),     # Dark Gray
        "head": (30, 30, 30)      # Very dark
    }
}

# Current Snake Colors (Default)
SNAKE_BODY = SNAKE_PROFILES["cobra"]["body"]
SNAKE_HEAD = SNAKE_PROFILES["cobra"]["head"]
current_snake_name = SNAKE_PROFILES["cobra"]["name"]
current_snake_id = "cobra"

# --- Dimensions ---
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
PLAY_Y_START = 40

dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Jungle Snake')

clock = pygame.time.Clock()
SNAKE_SPEED = 15

# App State
app_state = "menu"
SCORE_FILE = "scores.json"
SETTINGS_FILE = "settings.json"

# --- Fonts ---
try:
    font_style = pygame.font.Font("Roboto.ttf", 50)
    score_font = pygame.font.Font("Roboto.ttf", 24)
    btn_font = pygame.font.Font("Roboto.ttf", 25)
except:
    pass

# --- Background Image ---
bg_img = None
try:
    bg_img = pygame.image.load("jungle_bg.png")
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT - PLAY_Y_START))
except Exception as e:
    pass

def draw_game_background():
    if bg_img:
        dis.blit(bg_img, (0, PLAY_Y_START))
    else:
        dis.fill(BG_COLOR)

def load_scores():
    if sys.platform == "emscripten":
        try:
            from platform import window
            saved_data = window.localStorage.getItem("jungle_snake_scores")
            if saved_data:
                return json.loads(saved_data)
        except Exception as e:
            pass
        return []
    else:
        if not os.path.exists(SCORE_FILE):
            return []
        try:
            with open(SCORE_FILE, "r") as f:
                return json.load(f)
        except:
            return []

def save_score(score, snake_name):
    scores = load_scores()
    scores.append({"score": score, "snake": snake_name})
    # Sort by score descending
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    # Keep top 5
    scores = scores[:5]
    
    if sys.platform == "emscripten":
        try:
            from platform import window
            window.localStorage.setItem("jungle_snake_scores", json.dumps(scores))
        except Exception as e:
            pass
    else:
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(scores, f)
        except:
            pass

def load_settings():
    global SNAKE_SPEED, SNAKE_BODY, SNAKE_HEAD, current_snake_name, current_snake_id
    data = None
    if sys.platform == "emscripten":
        try:
            from platform import window
            saved_data = window.localStorage.getItem("jungle_snake_settings")
            if saved_data:
                data = json.loads(saved_data)
        except:
            pass
    else:
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
            except:
                pass
    if data:
        if "speed" in data:
            SNAKE_SPEED = data["speed"]
        if "snake_id" in data:
            snake_id = data["snake_id"]
            if snake_id in SNAKE_PROFILES:
                SNAKE_BODY = SNAKE_PROFILES[snake_id]["body"]
                SNAKE_HEAD = SNAKE_PROFILES[snake_id]["head"]
                current_snake_name = SNAKE_PROFILES[snake_id]["name"]
                current_snake_id = snake_id

def save_settings():
    data = {
        "speed": SNAKE_SPEED,
        "snake_id": current_snake_id
    }
    if sys.platform == "emscripten":
        try:
            from platform import window
            window.localStorage.setItem("jungle_snake_settings", json.dumps(data))
        except:
            pass
    else:
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f)
        except:
            pass

def draw_grid():
    for x in range(0, WIDTH, BLOCK_SIZE):
        pygame.draw.line(dis, GRID_COLOR, (x, PLAY_Y_START), (x, HEIGHT))
    for y in range(PLAY_Y_START, HEIGHT, BLOCK_SIZE):
        pygame.draw.line(dis, GRID_COLOR, (0, y), (WIDTH, y))

def draw_score(score):
    pygame.draw.rect(dis, SCORE_BG, [0, 0, WIDTH, PLAY_Y_START])
    pygame.draw.line(dis, SCORE_LINE, (0, PLAY_Y_START - 1), (WIDTH, PLAY_Y_START - 1), 3)
    value = score_font.render(f"JUNGLE SCORE: {score}", True, TEXT_COLOR)
    dis.blit(value, [15, 8])
    
    speed_txt = score_font.render(f"SPEED: {SNAKE_SPEED}", True, TEXT_COLOR)
    dis.blit(speed_txt, [WIDTH - 150, 8])

def draw_snake(block_size, snake_list, prev_snake_list, t, x_change=0, y_change=0):
    n = len(snake_list)
    m = len(prev_snake_list)
    for i, x in enumerate(snake_list):
        is_head = (i == n - 1)
        is_tail = (i == 0)
        
        # Calculate interpolated position for smooth drawing
        if m > 0:
            d = (n - 1) - i
            j = (m - 1) - d
            if j >= 0:
                prev_pos = prev_snake_list[j]
            else:
                prev_pos = x
            draw_x = prev_pos[0] + (x[0] - prev_pos[0]) * t
            draw_y = prev_pos[1] + (x[1] - prev_pos[1]) * t
        else:
            draw_x = x[0]
            draw_y = x[1]
            
        rect = [draw_x, draw_y, block_size, block_size]
        
        dx, dy = 0, -1
        if n > 1:
            if is_head:
                prev = snake_list[-2]
                dx = x[0] - prev[0]
                dy = x[1] - prev[1]
            else:
                nxt = snake_list[i+1]
                dx = nxt[0] - x[0]
                dy = nxt[1] - x[1]
                
            if dx != 0: dx = dx / abs(dx)
            if dy != 0: dy = dy / abs(dy)
        else:
            if x_change != 0: 
                dx = x_change / abs(x_change)
                dy = 0
            elif y_change != 0: 
                dx = 0
                dy = y_change / abs(y_change)

        if is_head:
            if current_snake_id == "cobra":
                hood_color = (139, 101, 8)
                hood_rect = None
                if dx > 0:
                    hood_rect = [draw_x - 5, draw_y - 8, block_size, block_size + 16]
                elif dx < 0:
                    hood_rect = [draw_x + 5, draw_y - 8, block_size, block_size + 16]
                elif dy > 0:
                    hood_rect = [draw_x - 8, draw_y - 5, block_size + 16, block_size]
                elif dy < 0:
                    hood_rect = [draw_x - 8, draw_y + 5, block_size + 16, block_size]
                
                if hood_rect:
                    pygame.draw.ellipse(dis, hood_color, hood_rect)

            pygame.draw.rect(dis, SNAKE_HEAD, rect, border_radius=6)
            
            eye_radius = 3
            cx, cy = draw_x + block_size/2, draw_y + block_size/2
            
            if dx > 0:
                ex1, ey1 = cx + 4, cy - 5
                ex2, ey2 = cx + 4, cy + 5
            elif dx < 0:
                ex1, ey1 = cx - 4, cy - 5
                ex2, ey2 = cx - 4, cy + 5
            elif dy > 0:
                ex1, ey1 = cx - 5, cy + 4
                ex2, ey2 = cx + 5, cy + 4
            else:
                ex1, ey1 = cx - 5, cy - 4
                ex2, ey2 = cx + 5, cy - 4

            pygame.draw.circle(dis, (255, 255, 255), (int(ex1), int(ey1)), eye_radius)
            pygame.draw.circle(dis, (255, 255, 255), (int(ex2), int(ey2)), eye_radius)
            
            px1, py1 = ex1 + dx, ey1 + dy
            px2, py2 = ex2 + dx, ey2 + dy
            pygame.draw.circle(dis, (0, 0, 0), (int(px1), int(py1)), 1)
            pygame.draw.circle(dis, (0, 0, 0), (int(px2), int(py2)), 1)
            
            if current_snake_id == "mamba":
                mouth_x, mouth_y = cx + (dx * 8), cy + (dy * 8)
                pygame.draw.circle(dis, (15, 15, 15), (int(mouth_x), int(mouth_y)), 3)
            
            if random.random() < 0.2:
                tx, ty = cx + (dx * 16), cy + (dy * 16)
                pygame.draw.line(dis, (255, 50, 50), (cx + dx*8, cy + dy*8), (tx, ty), 2)
                pygame.draw.line(dis, (255, 50, 50), (tx, ty), (tx + dx*3 - dy*3, ty + dy*3 + dx*3), 1)
                pygame.draw.line(dis, (255, 50, 50), (tx, ty), (tx + dx*3 + dy*3, ty + dy*3 - dx*3), 1)

        else:
            if is_tail:
                pygame.draw.rect(dis, SNAKE_BODY, [draw_x+4, draw_y+4, block_size-8, block_size-8], border_radius=4)
            else:
                pygame.draw.rect(dis, SNAKE_BODY, rect, border_radius=4)
            
            if current_snake_id == "cobra" and i % 2 == 0:
                pygame.draw.rect(dis, (238, 203, 50), [draw_x+6, draw_y+6, block_size-12, block_size-12], border_radius=2)
            elif current_snake_id == "taipan":
                if dx != 0:
                    pygame.draw.line(dis, (65, 85, 27), (draw_x, draw_y + block_size/2), (draw_x + block_size, draw_y + block_size/2), 3)
                else:
                    pygame.draw.line(dis, (65, 85, 27), (draw_x + block_size/2, draw_y), (draw_x + block_size/2, draw_y + block_size), 3)
            elif current_snake_id == "mamba":
                pygame.draw.circle(dis, (80, 80, 80), (int(draw_x+block_size/2), int(draw_y+block_size/2)), 2)

def draw_obstacles(block_size, obstacles_data):
    for obj in obstacles_data:
        t = obj['type']
        rx, ry = obj['x'], obj['y']
        rw, rh = obj['rw'], obj['rh']
        w_cells, h_cells = obj['w_cells'], obj['h_cells']
        
        if t == 'rock':
            # Grey granite rock
            pygame.draw.rect(dis, (100, 110, 100), [rx, ry, rw, rh], border_radius=6)
            if rw >= 20 and rh >= 20:
                inner_rect = [rx + 3, ry + 3, rw - 6, rh - 6]
                pygame.draw.rect(dis, (70, 78, 70), inner_rect, border_radius=4)
                if rw > 20 or rh > 20:
                    highlight_rect = [rx + 5, ry + 5, rw - 12, rh - 12]
                    pygame.draw.rect(dis, (130, 140, 130), highlight_rect, border_radius=3)
        
        elif t == 'pond':
            # Water pond (Blue)
            pygame.draw.rect(dis, (41, 128, 185), [rx, ry, rw, rh], border_radius=10)
            pygame.draw.rect(dis, (100, 200, 255), [rx, ry, rw, rh], width=2, border_radius=10)
            if rw >= 40 and rh >= 40:
                pygame.draw.ellipse(dis, (52, 152, 219), [rx + 6, ry + 6, rw - 12, rh - 12])
                pygame.draw.ellipse(dis, (135, 206, 250), [rx + 12, ry + 12, rw - 24, rh - 24], width=1)
                pygame.draw.circle(dis, (39, 174, 96), (int(rx + 12), int(ry + 15)), 4)
                pygame.draw.circle(dis, (39, 174, 96), (int(rx + rw - 15), int(ry + rh - 15)), 3)
                
        elif t == 'log':
            # Wood log (Brown)
            pygame.draw.rect(dis, (139, 69, 19), [rx, ry, rw, rh], border_radius=5)
            pygame.draw.rect(dis, (101, 50, 14), [rx + 2, ry + 2, rw - 4, rh - 4], border_radius=4)
            if w_cells > h_cells:
                # Horizontal log
                pygame.draw.ellipse(dis, (222, 184, 135), [rx, ry + 1, 4, rh - 2])
                pygame.draw.ellipse(dis, (222, 184, 135), [rx + rw - 4, ry + 1, 4, rh - 2])
                pygame.draw.line(dis, (139, 69, 19), (rx + 6, ry + rh/2), (rx + rw - 8, ry + rh/2), 2)
            else:
                # Vertical log
                pygame.draw.ellipse(dis, (222, 184, 135), [rx + 1, ry, rw - 2, 4])
                pygame.draw.ellipse(dis, (222, 184, 135), [rx + 1, ry + rh - 4, rw - 2, 4])
                pygame.draw.line(dis, (139, 69, 19), (rx + rw/2, ry + 6), (rx + rw/2, ry + rh - 8), 2)
                
        elif t == 'tree':
            # Tree (trunk + canopy)
            if w_cells == 1 and h_cells == 2:
                # Trunk
                pygame.draw.rect(dis, (101, 50, 14), [rx + 6, ry + 16, 8, 24], border_radius=2)
                # Leaves canopy
                pygame.draw.circle(dis, (34, 139, 34), (int(rx + 10), int(ry + 10)), 12)
                pygame.draw.circle(dis, (46, 204, 113), (int(rx + 10), int(ry + 8)), 8)
            elif w_cells == 2 and h_cells == 2:
                # Trunk
                pygame.draw.rect(dis, (101, 50, 14), [rx + 14, ry + 20, 12, 20], border_radius=3)
                # Canopy
                pygame.draw.circle(dis, (34, 139, 34), (int(rx + 14), int(ry + 14)), 14)
                pygame.draw.circle(dis, (34, 139, 34), (int(rx + 26), int(ry + 14)), 14)
                pygame.draw.circle(dis, (46, 204, 113), (int(rx + 20), int(ry + 10)), 12)

def draw_food(x, y, block_size):
    center = (int(x + block_size/2), int(y + block_size/2))
    pygame.draw.circle(dis, FOOD_COLOR, center, int(block_size/2 - 2))
    pygame.draw.polygon(dis, (46, 204, 113), [
        (center[0], center[1]-8), 
        (center[0]+4, center[1]-12), 
        (center[0]+2, center[1]-5)
    ])

def message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, color)
    text_rect = mesg.get_rect(center=(WIDTH/2, HEIGHT/2 + y_offset))
    bg_rect = text_rect.copy()
    bg_rect.inflate_ip(20, 20)
    pygame.draw.rect(dis, (10, 25, 10, 180), bg_rect, border_radius=10)
    pygame.draw.rect(dis, (39, 174, 96), bg_rect, width=2, border_radius=10)
    dis.blit(mesg, text_rect)

def draw_button(msg, x, y, w, h, ic, ac, mouse_clicked, action=None):
    mouse = pygame.mouse.get_pos()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(dis, ac, (x, y, w, h), border_radius=10)
        if mouse_clicked and action != None:
            action()
    else:
        pygame.draw.rect(dis, ic, (x, y, w, h), border_radius=10)

    text_surf = btn_font.render(msg, True, (255, 255, 255))
    text_rect = text_surf.get_rect()
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    dis.blit(text_surf, text_rect)

def quit_game():
    global app_state
    app_state = "quit"

def change_state(new_state):
    global app_state
    app_state = new_state

def set_speed(speed):
    global SNAKE_SPEED
    SNAKE_SPEED = speed
    save_settings()

def select_snake(snake_id):
    global SNAKE_BODY, SNAKE_HEAD, current_snake_name, current_snake_id, app_state
    SNAKE_BODY = SNAKE_PROFILES[snake_id]["body"]
    SNAKE_HEAD = SNAKE_PROFILES[snake_id]["head"]
    current_snake_name = SNAKE_PROFILES[snake_id]["name"]
    current_snake_id = snake_id
    save_settings()
    app_state = "game"

def get_random_pos():
    x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
    y = round(random.randrange(PLAY_Y_START, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0
    return x, y

async def mainMenu():
    global app_state
    while app_state == "menu":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        dis.fill(BG_COLOR)
        message("JUNGLE SNAKE", TEXT_COLOR, -180)

        draw_button("START", 325, 180, 150, 50, (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: change_state("selection"))
        draw_button("SCORES", 325, 250, 150, 50, (41, 128, 185), (52, 152, 219), mouse_clicked, lambda: change_state("scores"))
        draw_button("SETTINGS", 325, 320, 150, 50, (211, 84, 0), (230, 126, 34), mouse_clicked, lambda: change_state("settings"))
        draw_button("EXIT", 325, 390, 150, 50, (192, 57, 43), (231, 76, 60), mouse_clicked, quit_game)

        pygame.display.update()
        await asyncio.sleep(0)

async def scoresMenu():
    global app_state
    while app_state == "scores":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        dis.fill(BG_COLOR)
        message("TOP 5 SCORES", TEXT_COLOR, -220)

        scores = load_scores()
        start_y = 150
        if not scores:
            try:
                msg = score_font.render("No scores yet!", True, (255, 255, 255))
                dis.blit(msg, (WIDTH/2 - msg.get_width()/2, 200))
            except: pass
        else:
            for i, s in enumerate(scores):
                try:
                    msg = score_font.render(f"{i+1}. {s['snake']} - Score: {s['score']}", True, (255, 255, 255))
                    bg_rect = msg.get_rect()
                    bg_rect.topleft = (WIDTH/2 - msg.get_width()/2, start_y + (i * 45))
                    bg_rect.inflate_ip(20, 10)
                    pygame.draw.rect(dis, (10, 25, 10, 180), bg_rect, border_radius=5)
                    dis.blit(msg, (WIDTH/2 - msg.get_width()/2, start_y + (i * 45)))
                except: pass

        draw_button("BACK", 350, 450, 100, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("menu"))

        pygame.display.update()
        await asyncio.sleep(0)

async def snakeSelectionMenu():
    global app_state
    while app_state == "selection":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        dis.fill(BG_COLOR)
        message("CHOOSE YOUR SNAKE", TEXT_COLOR, -180)

        draw_button("KING COBRA", 300, 200, 200, 50, SNAKE_PROFILES["cobra"]["body"], SNAKE_PROFILES["cobra"]["head"], mouse_clicked, lambda: select_snake("cobra"))
        draw_button("INLAND TAIPAN", 300, 270, 200, 50, SNAKE_PROFILES["taipan"]["body"], SNAKE_PROFILES["taipan"]["head"], mouse_clicked, lambda: select_snake("taipan"))
        draw_button("BLACK MAMBA", 300, 340, 200, 50, SNAKE_PROFILES["mamba"]["body"], SNAKE_PROFILES["mamba"]["head"], mouse_clicked, lambda: select_snake("mamba"))
        
        draw_button("BACK", 350, 420, 100, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("menu"))

        pygame.display.update()
        await asyncio.sleep(0)

async def settingsMenu():
    global app_state
    while app_state == "settings":
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        dis.fill(BG_COLOR)
        message("SETTINGS", TEXT_COLOR, -180)

        try:
            speed_msg = f"Current Speed: {SNAKE_SPEED}"
            speed_surf = font_style.render(speed_msg, True, (255, 255, 255))
            dis.blit(speed_surf, (WIDTH/2 - speed_surf.get_width()/2, HEIGHT/2 - 100))
        except: pass

        draw_button("V. SLOW", 120, 300, 100, 50, (22, 160, 133), (26, 188, 156), mouse_clicked, lambda: set_speed(5))
        draw_button("SLOW", 235, 300, 100, 50, (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: set_speed(10))
        draw_button("NORMAL", 350, 300, 100, 50, (211, 84, 0), (230, 126, 34), mouse_clicked, lambda: set_speed(15))
        draw_button("FAST", 465, 300, 100, 50, (192, 57, 43), (231, 76, 60), mouse_clicked, lambda: set_speed(20))
        draw_button("V. FAST", 580, 300, 100, 50, (142, 68, 173), (155, 89, 182), mouse_clicked, lambda: set_speed(25))
        
        draw_button("BACK", 350, 420, 100, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("menu"))

        pygame.display.update()
        await asyncio.sleep(0)

def is_opposite(dir1, dir2):
    return dir1[0] * dir2[0] + dir1[1] * dir2[1] < 0

async def gameLoop():
    global app_state
    game_over = False
    game_close = False

    x1 = round((WIDTH / 2) / 20.0) * 20.0
    y1 = round((HEIGHT / 2) / 20.0) * 20.0

    x1_change = 0
    y1_change = 0
    direction_queue = []

    snake_List = []
    prev_snake_List = []
    Length_of_snake = 1

    obstacles_data = []
    obstacles = []
    num_obstacles = 9
    
    types_pool = ['pond', 'pond', 'tree', 'tree', 'log', 'log', 'rock', 'rock', 'rock']
    
    for obj_type in types_pool:
        if obj_type == 'pond':
            w_cells, h_cells = 2, 2
        elif obj_type == 'tree':
            w_cells, h_cells = random.choice([(1, 2), (2, 2)])
        elif obj_type == 'log':
            w_cells, h_cells = random.choice([(2, 1), (1, 2)])
        else: # rock
            w_cells, h_cells = random.choice([(1, 1), (2, 1), (1, 2), (2, 2)])
            
        rw = w_cells * BLOCK_SIZE
        rh = h_cells * BLOCK_SIZE
        
        placed = False
        for _ in range(150):
            rx = round(random.randrange(BLOCK_SIZE, WIDTH - rw - BLOCK_SIZE) / 20.0) * 20.0
            ry = round(random.randrange(PLAY_Y_START + BLOCK_SIZE, HEIGHT - rh - BLOCK_SIZE) / 20.0) * 20.0
            
            too_close = False
            for cx in range(w_cells):
                for cy in range(h_cells):
                    px = rx + cx * BLOCK_SIZE
                    py = ry + cy * BLOCK_SIZE
                    dist_to_center = abs(px - x1) + abs(py - y1)
                    if dist_to_center < 120:
                        too_close = True
                        break
                if too_close:
                    break
                    
            if too_close:
                continue
                
            conflict = False
            for cx in range(-1, w_cells + 1):
                for cy in range(-1, h_cells + 1):
                    check_x = rx + cx * BLOCK_SIZE
                    check_y = ry + cy * BLOCK_SIZE
                    if [check_x, check_y] in obstacles:
                        conflict = True
                        break
                if conflict:
                    break
                    
            if not conflict:
                obstacles_data.append({
                    'type': obj_type,
                    'x': rx,
                    'y': ry,
                    'w_cells': w_cells,
                    'h_cells': h_cells,
                    'rw': rw,
                    'rh': rh
                })
                for cx in range(w_cells):
                    for cy in range(h_cells):
                        obstacles.append([rx + cx * BLOCK_SIZE, ry + cy * BLOCK_SIZE])
                placed = True
                break

    while True:
        foodx, foody = get_random_pos()
        if [foodx, foody] not in obstacles and (foodx != x1 or foody != y1):
            break

    last_move_time = pygame.time.get_ticks()

    while app_state == "game":
        while game_close == True:
            mouse_clicked = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True

            draw_game_background()
            draw_grid()
            draw_score(Length_of_snake - 1)
            
            message("GAME OVER!", (231, 76, 60), -50)

            draw_button("PLAY AGAIN", 250, 350, 140, 50, (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: change_state("restart_game"))
            draw_button("MAIN MENU", 410, 350, 140, 50, (211, 84, 0), (230, 126, 34), mouse_clicked, lambda: change_state("menu"))

            pygame.display.update()
            await asyncio.sleep(0)

            if app_state != "game":
                if app_state == "restart_game":
                    change_state("game") 
                return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                proposed_dir = None
                if event.key == pygame.K_LEFT:
                    proposed_dir = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT:
                    proposed_dir = (BLOCK_SIZE, 0)
                elif event.key == pygame.K_UP:
                    proposed_dir = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN:
                    proposed_dir = (0, BLOCK_SIZE)

                if proposed_dir is not None:
                    if direction_queue:
                        ref_dir = direction_queue[-1]
                    else:
                        ref_dir = (x1_change, y1_change)
                    
                    if not is_opposite(proposed_dir, ref_dir):
                        if len(direction_queue) < 2:
                            direction_queue.append(proposed_dir)

        # Non-blocking timer for snake speed
        now = pygame.time.get_ticks()
        if now - last_move_time > (1000 / SNAKE_SPEED):
            last_move_time = now
            
            # Save previous state for smooth interpolation
            prev_snake_List = [list(pos) for pos in snake_List]
            
            if direction_queue:
                x1_change, y1_change = direction_queue.pop(0)
            
            # Boundary collision
            if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < PLAY_Y_START:
                save_score(Length_of_snake - 1, current_snake_name)
                game_close = True
                
            x1 += x1_change
            y1 += y1_change

            # Obstacle collision
            if not game_close and [x1, y1] in obstacles:
                save_score(Length_of_snake - 1, current_snake_name)
                game_close = True

            snake_Head = []
            snake_Head.append(x1)
            snake_Head.append(y1)
            snake_List.append(snake_Head)
            
            if len(snake_List) > Length_of_snake:
                del snake_List[0]

            # Self collision
            for x in snake_List[:-1]:
                if x == snake_Head:
                    if not game_close:
                        save_score(Length_of_snake - 1, current_snake_name)
                        game_close = True
                        
            if x1 == foodx and y1 == foody:
                while True:
                    foodx, foody = get_random_pos()
                    if [foodx, foody] not in obstacles and [foodx, foody] not in snake_List:
                        break
                Length_of_snake += 1

        # Calculate interpolation factor
        step_duration = 1000.0 / SNAKE_SPEED
        t = (now - last_move_time) / step_duration
        t = max(0.0, min(1.0, t))

        draw_game_background()
        draw_grid()
        
        draw_food(foodx, foody, BLOCK_SIZE)
        draw_obstacles(BLOCK_SIZE, obstacles_data)
        draw_snake(BLOCK_SIZE, snake_List, prev_snake_List, t, x1_change, y1_change)
        draw_score(Length_of_snake - 1)

        pygame.display.update()
        await asyncio.sleep(0)

async def main():
    try:
        global app_state
        load_settings()
        while app_state != "quit":
            if app_state == "menu":
                await mainMenu()
            elif app_state == "selection":
                await snakeSelectionMenu()
            elif app_state == "scores":
                await scoresMenu()
            elif app_state == "settings":
                await settingsMenu()
            elif app_state == "game":
                await gameLoop()
            
            await asyncio.sleep(0)
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        dis.fill((200, 0, 0))
        try:
            sys_font = pygame.font.Font(None, 20)
            y = 10
            for line in err.split('\n'):
                dis.blit(sys_font.render(line, True, (255, 255, 255)), (10, y))
                y += 20
        except:
            pass
        pygame.display.update()
        while True:
            await asyncio.sleep(0)

    return

if __name__ == '__main__':
    asyncio.run(main())
