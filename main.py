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

# --- Fonts ---
try:
    font_style = pygame.font.Font("Roboto.ttf", 50)
    score_font = pygame.font.Font("Roboto.ttf", 24)
    btn_font = pygame.font.Font("Roboto.ttf", 25)
except:
    pass

def load_scores():
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
    try:
        with open(SCORE_FILE, "w") as f:
            json.dump(scores, f)
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

def draw_snake(block_size, snake_list, x_change=0, y_change=0):
    for i, x in enumerate(snake_list):
        rect = [x[0], x[1], block_size, block_size]
        is_head = (i == len(snake_list) - 1)
        is_tail = (i == 0)
        
        dx, dy = 0, -1
        if len(snake_list) > 1:
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
                    hood_rect = [x[0] - 5, x[1] - 8, block_size, block_size + 16]
                elif dx < 0:
                    hood_rect = [x[0] + 5, x[1] - 8, block_size, block_size + 16]
                elif dy > 0:
                    hood_rect = [x[0] - 8, x[1] - 5, block_size + 16, block_size]
                elif dy < 0:
                    hood_rect = [x[0] - 8, x[1] + 5, block_size + 16, block_size]
                
                if hood_rect:
                    pygame.draw.ellipse(dis, hood_color, hood_rect)

            pygame.draw.rect(dis, SNAKE_HEAD, rect, border_radius=6)
            
            eye_radius = 3
            cx, cy = x[0] + block_size/2, x[1] + block_size/2
            
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
                pygame.draw.rect(dis, SNAKE_BODY, [x[0]+4, x[1]+4, block_size-8, block_size-8], border_radius=4)
            else:
                pygame.draw.rect(dis, SNAKE_BODY, rect, border_radius=4)
            
            if current_snake_id == "cobra" and i % 2 == 0:
                pygame.draw.rect(dis, (238, 203, 50), [x[0]+6, x[1]+6, block_size-12, block_size-12], border_radius=2)
            elif current_snake_id == "taipan":
                if dx != 0:
                    pygame.draw.line(dis, (65, 85, 27), (x[0], x[1] + block_size/2), (x[0] + block_size, x[1] + block_size/2), 3)
                else:
                    pygame.draw.line(dis, (65, 85, 27), (x[0] + block_size/2, x[1]), (x[0] + block_size/2, x[1] + block_size), 3)
            elif current_snake_id == "mamba":
                pygame.draw.circle(dis, (80, 80, 80), (int(x[0]+block_size/2), int(x[1]+block_size/2)), 2)

def draw_obstacles(block_size, obstacles):
    for obs in obstacles:
        center = (int(obs[0] + block_size/2), int(obs[1] + block_size/2))
        pygame.draw.circle(dis, OBSTACLE_COLOR, center, int(block_size/2 - 1))
        pygame.draw.circle(dis, OBSTACLE_INNER, center, int(block_size/3 - 1))

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

def select_snake(snake_id):
    global SNAKE_BODY, SNAKE_HEAD, current_snake_name, current_snake_id, app_state
    SNAKE_BODY = SNAKE_PROFILES[snake_id]["body"]
    SNAKE_HEAD = SNAKE_PROFILES[snake_id]["head"]
    current_snake_name = SNAKE_PROFILES[snake_id]["name"]
    current_snake_id = snake_id
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

        draw_button("SLOW", 225, 300, 100, 50, (39, 174, 96), (46, 204, 113), mouse_clicked, lambda: set_speed(10))
        draw_button("NORMAL", 350, 300, 100, 50, (211, 84, 0), (230, 126, 34), mouse_clicked, lambda: set_speed(15))
        draw_button("FAST", 475, 300, 100, 50, (192, 57, 43), (231, 76, 60), mouse_clicked, lambda: set_speed(25))
        
        draw_button("BACK", 350, 420, 100, 50, (127, 140, 141), (149, 165, 166), mouse_clicked, lambda: change_state("menu"))

        pygame.display.update()
        await asyncio.sleep(0)

async def gameLoop():
    global app_state
    game_over = False
    game_close = False

    x1 = round((WIDTH / 2) / 20.0) * 20.0
    y1 = round((HEIGHT / 2) / 20.0) * 20.0

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    num_obstacles = 15
    obstacles = []
    for _ in range(num_obstacles):
        while True:
            obs_x, obs_y = get_random_pos()
            dist_to_center = abs(obs_x - x1) + abs(obs_y - y1)
            if dist_to_center > 100:
                obstacles.append([obs_x, obs_y])
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

            dis.fill(BG_COLOR)
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
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0

        # Non-blocking timer for snake speed
        now = pygame.time.get_ticks()
        if now - last_move_time > (1000 / SNAKE_SPEED):
            last_move_time = now
            
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

        dis.fill(BG_COLOR)
        draw_grid()
        
        draw_food(foodx, foody, BLOCK_SIZE)
        draw_obstacles(BLOCK_SIZE, obstacles)
        draw_snake(BLOCK_SIZE, snake_List, x1_change, y1_change)
        draw_score(Length_of_snake - 1)

        pygame.display.update()
        await asyncio.sleep(0)

async def main():
    try:
        global app_state
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
