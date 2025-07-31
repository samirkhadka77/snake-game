import pygame
import sys
import random
import numpy as np

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
GREEN_HEAD = (0, 255, 0)
GREEN_BODY = (0, 155, 0)
RED = (255, 0, 0)
GRAY = (40, 40, 40)
WHITE = (255, 255, 255)

FONT_SMALL = pygame.font.SysFont("Arial", 20)
FONT_MEDIUM = pygame.font.SysFont("Arial", 28)
FONT_LARGE = pygame.font.SysFont("Arial", 36)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nokia Snake Classic")

clock = pygame.time.Clock()


def make_beep_sound(frequency=440, duration=100):
    sample_rate = 44100
    n_samples = int(sample_rate * duration / 1000)
    t = np.linspace(0, duration / 1000, n_samples, False)
    tone = np.sin(frequency * 2 * np.pi * t)
    audio = (tone * 32767).astype(np.int16)  # Mono 1D array

    # Convert to 2D stereo by duplicating the audio channel
    stereo_audio = np.column_stack([audio, audio])

    sound = pygame.sndarray.make_sound(stereo_audio)
    return sound


eat_sound = make_beep_sound(1000, 100)
gameover_sound = make_beep_sound(300, 500)

def play_eat_sound():
    eat_sound.play()

def play_gameover_sound():
    gameover_sound.play()

def draw_rounded_rect(surface, color, rect, radius=5):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH//2, GRID_HEIGHT//2),
                          (GRID_WIDTH//2 - 1, GRID_HEIGHT//2),
                          (GRID_WIDTH//2 - 2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.grow = False

    def move(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Boundary collision = game over
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            return False

        # Self collision = game over
        if new_head in self.positions:
            return False

        self.positions.insert(0, new_head)
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        return True

    def change_direction(self, new_dir):
        if (new_dir[0]*-1, new_dir[1]*-1) == self.direction:
            return
        self.direction = new_dir

    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            x, y = pos
            rect = (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if i == 0:
                draw_rounded_rect(surface, GREEN_HEAD, rect, radius=6)
            else:
                draw_rounded_rect(surface, GREEN_BODY, rect, radius=4)

class Food:
    def __init__(self, snake_positions):
        self.position = (0, 0)
        self.randomize(snake_positions)

    def randomize(self, snake_positions):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_positions:
                self.position = (x, y)
                break

    def draw(self, surface):
        x, y = self.position
        rect = (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        draw_rounded_rect(surface, RED, rect, radius=5)

def draw_grid(surface):
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, GRAY, (0, y), (WIDTH, y))

def draw_text(surface, text, font, pos, color=WHITE):
    label = font.render(text, True, color)
    surface.blit(label, pos)

def game_over_screen(score):
    play_gameover_sound()
    screen.fill(BLACK)
    draw_text(screen, "Game Over!", FONT_LARGE, (WIDTH//2 - 100, HEIGHT//3), RED)
    draw_text(screen, f"Your Score: {score}", FONT_MEDIUM, (WIDTH//2 - 80, HEIGHT//3 + 60))
    draw_text(screen, "Press R to Restart or Q to Quit", FONT_SMALL, (WIDTH//2 - 130, HEIGHT//3 + 120))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    snake = Snake()
    food = Food(snake.positions)
    score = 0
    speed = 10

    running = True
    while running:
        clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()

        alive = snake.move()
        if not alive:
            restart = game_over_screen(score)
            if restart:
                main()
            else:
                break

        if snake.positions[0] == food.position:
            play_eat_sound()
            snake.grow = True
            score += 1
            food.randomize(snake.positions)

        screen.fill(BLACK)
        draw_grid(screen)
        snake.draw(screen)
        food.draw(screen)
        draw_text(screen, f"Score: {score}", FONT_SMALL, (10, 10))
        pygame.display.flip()

if __name__ == "__main__":
    main()
