import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 300, 450  # Adjusted size
FPS = 60
BACKGROUND_COLOR = (65, 65, 65)  # Background color (#414141)
OBSTACLE_COLOR = (0, 60, 98)  # Obstacle color (#003c62)
OBSTACLE_GAP = 200  # Adjusted for smaller window
OBSTACLE_WIDTH = 100  # Adjusted for smaller window
PLAYER_SPEED = 100  # Adjusted for smaller window
LANE_LINE_COLOR = (200, 200, 200)
DISTANCE_TEXT_COLOR = (255, 255, 255)

# Lane positions and widths
LANE_WIDTH = WIDTH // 3
LANE_1_X = 0
LANE_2_X = LANE_WIDTH
LANE_3_X = LANE_WIDTH * 2

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Runner")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Game state variables
game_over = False

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.moving = 0  # 0 for not moving, 1 for left, 2 for right

    def move(self, direction):
        if direction == 1 and self.rect.left - PLAYER_SPEED >= 0:  # Move left
            self.rect.move_ip(-PLAYER_SPEED, 0)
        elif direction == 2 and self.rect.right + PLAYER_SPEED <= WIDTH:  # Move right
            self.rect.move_ip(PLAYER_SPEED, 0)

    def draw(self):
        pygame.draw.rect(screen, (0, 128, 255), self.rect)

class Obstacle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, OBSTACLE_WIDTH, 100)

    def move(self):
        self.rect.move_ip(0, 5)

    def draw(self):
        pygame.draw.rect(screen, OBSTACLE_COLOR, self.rect)

# Create player object
player = Player(LANE_2_X + (LANE_WIDTH // 2), HEIGHT - 50)

# Obstacle variables
obstacles = []

def draw_dotted_lines():
    for x in range(LANE_WIDTH, WIDTH, LANE_WIDTH):
        pygame.draw.line(screen, LANE_LINE_COLOR, (x, 0), (x, HEIGHT), 1)

def spawn_obstacle_row(previous_row_y):
    lanes = [1, 2, 3]
    random.shuffle(lanes)

    spawned_obstacles = 0
    y_coordinate = previous_row_y - OBSTACLE_GAP
    obstacle_positions = []

    for lane in lanes:
        if spawned_obstacles >= 2:
            break

        overlap = any(
            obstacle.rect.colliderect(pygame.Rect((lane - 1) * LANE_WIDTH, y_coordinate, OBSTACLE_WIDTH, 100))
            for obstacle in obstacle_positions
        )

        if not overlap:
            obstacle = Obstacle((lane - 1) * LANE_WIDTH, y_coordinate)
            obstacles.append(obstacle)
            obstacle_positions.append(obstacle)
            spawned_obstacles += 1

# Function to display text on the screen
def display_text(text, x, y, size=36, color=(255, 0, 0)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

# Variables to control obstacle row spawning
next_row_time = 0
current_row_y = 0
distance = 0
distance_increase_speed = 0.5

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.move(1)  # Move left
            elif event.key == pygame.K_RIGHT:
                player.move(2)  # Move right

    if not game_over:
        # Increase the distance tracker at half the speed
        distance += distance_increase_speed

        # Spawn obstacle rows
        if pygame.time.get_ticks() > next_row_time:
            spawn_obstacle_row(current_row_y)
            current_row_y -= OBSTACLE_GAP  # Adjust the y-coordinate for the next row
            next_row_time = pygame.time.get_ticks() + OBSTACLE_GAP

        # Move obstacles
        for obstacle in obstacles:
            obstacle.move()

        # Remove off-screen obstacles
        obstacles = [obstacle for obstacle in obstacles if obstacle.rect.y < HEIGHT]

        # Collision detection using pygame's colliderect function
        for obstacle in obstacles:
            if player.rect.colliderect(obstacle.rect):
                game_over = True

    # Clear the screen with the background color
    screen.fill(BACKGROUND_COLOR)

    # Draw dotted lines
    draw_dotted_lines()

    # Draw game elements
    for obstacle in obstacles:
        obstacle.draw()
    player.draw()

    if game_over:
        # Display "FAIL" text
        display_text("FAIL", WIDTH // 2, HEIGHT // 2)

    # Draw distance tracker above other elements with white color
    display_text(f"Distance: {int(distance)}", WIDTH // 2, 50, color=DISTANCE_TEXT_COLOR)

    # Update the display
    pygame.display.update()

    # Control the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
