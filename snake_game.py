import pygame
import time
import random

pygame.init()

# Define Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Display Dimensions
WIDTH = 800
HEIGHT = 600

dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game with Obstacles')

clock = pygame.time.Clock()

BLOCK_SIZE = 20
SNAKE_SPEED = 15

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def your_score(score):
    value = score_font.render("Score: " + str(score), True, YELLOW)
    dis.blit(value, [0, 0])

def our_snake(block_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, GREEN, [x[0], x[1], block_size, block_size])

def draw_obstacles(block_size, obstacles):
    for obs in obstacles:
        pygame.draw.rect(dis, BLUE, [obs[0], obs[1], block_size, block_size])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [WIDTH / 6, HEIGHT / 3])

def gameLoop():
    game_over = False
    game_close = False

    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    # Generate obstacles
    num_obstacles = 15
    obstacles = []
    for _ in range(num_obstacles):
        while True:
            obs_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
            obs_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0
            # Ensure not on start position or too close to center
            if not (WIDTH / 2 - 40 <= obs_x <= WIDTH / 2 + 40 and HEIGHT / 2 - 40 <= obs_y <= HEIGHT / 2 + 40):
                obstacles.append([obs_x, obs_y])
                break

    # Initial food spawn
    while True:
        foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
        foody = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0
        if [foodx, foody] not in obstacles and (foodx != WIDTH / 2 or foody != HEIGHT / 2):
            break

    while not game_over:

        while game_close == True:
            dis.fill(BLACK)
            message("You Lost! Press C-Play Again or Q-Quit", RED)
            your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()
                        return # Exit the current loop completely to restart

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
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

        # Boundary checks
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True
            
        x1 += x1_change
        y1 += y1_change

        # Obstacle collision check
        if [x1, y1] in obstacles:
            game_close = True

        dis.fill(BLACK)
        pygame.draw.rect(dis, RED, [foodx, foody, BLOCK_SIZE, BLOCK_SIZE])
        draw_obstacles(BLOCK_SIZE, obstacles)
        
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(BLOCK_SIZE, snake_List)
        your_score(Length_of_snake - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            while True:
                foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
                foody = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0
                if [foodx, foody] not in obstacles and [foodx, foody] not in snake_List:
                    break
            Length_of_snake += 1

        clock.tick(SNAKE_SPEED)

    pygame.quit()
    quit()

if __name__ == '__main__':
    gameLoop()
