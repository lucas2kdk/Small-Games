import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

# Get the screen size
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Set up the game window
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FULLSCREEN)
pygame.display.set_caption('Multiplayer Pong')

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Set up paddles
PADDLE_WIDTH = int(SCREEN_WIDTH * 0.01)
PADDLE_HEIGHT = int(SCREEN_HEIGHT * 0.15)
PADDLE_VELOCITY = int(SCREEN_HEIGHT * 0.01)
player1_controls = {K_w: 'up', K_s: 'down'}
player2_controls = {K_i: 'up', K_k: 'down'}
player1_paddle = pygame.Rect(0, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2_paddle = pygame.Rect(SCREEN_WIDTH - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Set up the ball
BALL_RADIUS = int(SCREEN_WIDTH * 0.01)
BALL_VELOCITY_X = int(SCREEN_WIDTH * 0.005)
BALL_VELOCITY_Y = int(SCREEN_HEIGHT * 0.005)
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_RADIUS, SCREEN_HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_velocity_x = BALL_VELOCITY_X * random.choice((1, -1))
ball_velocity_y = BALL_VELOCITY_Y * random.choice((1, -1))

# Set up the font
font = pygame.font.Font(None, int(SCREEN_WIDTH * 0.2))

# Set up scores
player1_score = 0
player2_score = 0
score_transition_timer = 0
SCORE_TRANSITION_DURATION = 1000  # milliseconds

# Set up particles
PARTICLE_SIZE = int(SCREEN_WIDTH * 0.02)
NUM_PARTICLES = 100
particles = []

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((PARTICLE_SIZE, PARTICLE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (PARTICLE_SIZE // 2, PARTICLE_SIZE // 2), PARTICLE_SIZE // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = random.uniform(-5, 5)
        self.vel_y = random.uniform(-5, 5)
        self.fade_rate = random.randint(5, 10)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.image.set_alpha(self.image.get_alpha() - self.fade_rate)
        if self.image.get_alpha() <= 0:
            self.kill()

# Set up the clock
clock = pygame.time.Clock()

# Function to reset the game
def reset_game():
    global ball_velocity_x, ball_velocity_y, ball, score_transition_timer
    ball_velocity_x = BALL_VELOCITY_X * random.choice((1, -1))
    ball_velocity_y = BALL_VELOCITY_Y * random.choice((1, -1))
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    score_transition_timer = pygame.time.get_ticks()

# Function to handle score transition
def handle_score_transition():
    global player1_score_text, player2_score_text, score_transition_timer
    if score_transition_timer > 0:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - score_transition_timer
        if elapsed_time >= SCORE_TRANSITION_DURATION:
            score_transition_timer = 0
        else:
            alpha = int((elapsed_time / SCORE_TRANSITION_DURATION) * 255)
            player1_score_text.set_alpha(alpha)
            player2_score_text.set_alpha(alpha)

# Function to interpolate between two values
def interpolate_value(start, end, progress):
    return int(start + (end - start) * progress)

# Game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

    # Move paddles
    keys = pygame.key.get_pressed()
    if keys[K_w] and player1_paddle.top > 0:
        player1_paddle.y -= PADDLE_VELOCITY
    if keys[K_s] and player1_paddle.bottom < SCREEN_HEIGHT:
        player1_paddle.y += PADDLE_VELOCITY
    if keys[K_i] and player2_paddle.top > 0:
        player2_paddle.y -= PADDLE_VELOCITY
    if keys[K_k] and player2_paddle.bottom < SCREEN_HEIGHT:
        player2_paddle.y += PADDLE_VELOCITY

    # Move the ball
    ball.x += ball_velocity_x
    ball.y += ball_velocity_y

    # Ball collision with paddles
    if ball.colliderect(player1_paddle) or ball.colliderect(player2_paddle):
        ball_velocity_x *= -1

        # Clear particles when the ball hits the paddles
        particles.clear()

    # Ball collision with walls
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_velocity_y *= -1

    # Ball out of bounds
    if ball.left <= 0:
        player2_score += 1
        reset_game()
    if ball.right >= SCREEN_WIDTH:
        player1_score += 1
        reset_game()

    # Update particles
    for particle in particles:
        particle.update()

    # Remove faded particles
    particles = [particle for particle in particles if particle.image.get_alpha() > 0]

    # Handle score transition
    handle_score_transition()

    # Update score surfaces
    player1_score_text = font.render(str(player1_score), True, GRAY)
    player2_score_text = font.render(str(player2_score), True, GRAY)

    # Draw the game elements
    window.fill(BLACK)
    pygame.draw.rect(window, WHITE, player1_paddle)
    pygame.draw.rect(window, WHITE, player2_paddle)
    pygame.draw.circle(window, WHITE, ball.center, BALL_RADIUS)

    # Draw scores as large numbers in the center of the screen
    player1_score_text_rect = player1_score_text.get_rect(center=(SCREEN_WIDTH // 2 - player1_score_text.get_width() // 2 - 20, SCREEN_HEIGHT // 2))
    player2_score_text_rect = player2_score_text.get_rect(center=(SCREEN_WIDTH // 2 + player2_score_text.get_width() // 2 + 20, SCREEN_HEIGHT // 2))

    # Morph transition effect for the scores
    if score_transition_timer > 0:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - score_transition_timer
        t = min(1, elapsed_time / SCORE_TRANSITION_DURATION)
        morphed_digit1 = int(str(player1_score)[-1])
        morphed_digit2 = int(str(player1_score + 1)[-1])
        morphed_value = interpolate_value(morphed_digit1, morphed_digit2, t)
        morphed_score_text = font.render(str(morphed_value), True, GRAY)
        morphed_score_text_rect = morphed_score_text.get_rect(center=player1_score_text_rect.center)
        window.blit(morphed_score_text, morphed_score_text_rect)
    else:
        window.blit(player1_score_text, player1_score_text_rect)

    window.blit(player2_score_text, player2_score_text_rect)

    # Draw a white line down the middle
    pygame.draw.line(window, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 1)

    # Draw particles
    for particle in particles:
        window.blit(particle.image, particle.rect)

    # Update the game display
    pygame.display.update()

    # Limit frames per second
    clock.tick(60)

# Quit the game
pygame.quit()
