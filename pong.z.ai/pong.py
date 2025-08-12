import pygame
import math
import random
import numpy as np
from pygame import gfxdraw

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
BALL_SIZE = 12
PADDLE_SPEED = 6
BALL_SPEED = 5

# PS1-style colors (limited palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

class SoundGenerator:
    """Generate retro PS1-style sound effects"""
    
    @staticmethod
    def generate_tone(frequency, duration, sample_rate=22050):
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        for i in range(frames):
            arr[i] = 4096 * np.sin(2 * np.pi * frequency * i / sample_rate)
        return arr
    
    @staticmethod
    def generate_bounce_sound():
        # PS1-style bounce sound
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            # Frequency sweep for bounce effect
            freq = 800 * (1 - i / frames) + 200
            arr[i] = 4096 * np.sin(2 * np.pi * freq * i / sample_rate) * (1 - i / frames)
        
        # Convert to pygame sound
        arr = arr.astype(np.int16)
        arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(arr)
    
    @staticmethod
    def generate_score_sound():
        # PS1-style score sound
        duration = 0.3
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            # Ascending tone
            freq = 400 + (i / frames) * 400
            arr[i] = 4096 * np.sin(2 * np.pi * freq * i / sample_rate)
        
        arr = arr.astype(np.int16)
        arr = np.repeat(arr.reshape(frames, 1), 2, axis=1)
        return pygame.sndarray.make_sound(arr)

class PS1Renderer:
    """PS1-style rendering with low-poly aesthetic"""
    
    def __init__(self, screen):
        self.screen = screen
        self.scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.scanline_surface.set_alpha(30)
        
        # Create scanlines
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(self.scanline_surface, BLACK, (0, y), (SCREEN_WIDTH, y))
    
    def draw_paddle(self, x, y, color=WHITE):
        # PS1-style paddle with pixelated edges
        paddle_rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(self.screen, color, paddle_rect)
        
        # Add PS1-style pixelation effect
        for i in range(0, PADDLE_HEIGHT, 4):
            pygame.draw.line(self.screen, BLACK, (x, y + i), (x + PADDLE_WIDTH, y + i))
    
    def draw_ball(self, x, y, color=WHITE):
        # PS1-style ball with low-poly look
        ball_rect = pygame.Rect(x - BALL_SIZE//2, y - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        pygame.draw.rect(self.screen, color, ball_rect)
        
        # Add pixelation
        pygame.draw.circle(self.screen, color, (x, y), BALL_SIZE//2)
        
        # PS1-style motion blur effect
        if hasattr(self, 'prev_ball_x'):
            blur_alpha = 100
            blur_surface = pygame.Surface((BALL_SIZE, BALL_SIZE))
            blur_surface.set_alpha(blur_alpha)
            blur_surface.fill(color)
            self.screen.blit(blur_surface, (self.prev_ball_x - BALL_SIZE//2, self.prev_ball_y - BALL_SIZE//2))
    
    def draw_background(self):
        # PS1-style background with subtle pattern
        self.screen.fill(BLACK)
        
        # Draw subtle grid pattern
        for x in range(0, SCREEN_WIDTH, 32):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 32):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))
    
    def draw_ui(self, score1, score2):
        # PS1-style UI
        font = pygame.font.Font(None, 48)
        
        # Draw scores with PS1-style font
        score1_text = font.render(str(score1), True, GREEN)
        score2_text = font.render(str(score2), True, BLUE)
        
        self.screen.blit(score1_text, (SCREEN_WIDTH//4 - score1_text.get_width()//2, 50))
        self.screen.blit(score2_text, (3*SCREEN_WIDTH//4 - score2_text.get_width()//2, 50))
        
        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH//2 - 2, y, 4, 10))
    
    def apply_ps1_effects(self):
        # Apply CRT-like scanlines
        self.screen.blit(self.scanline_surface, (0, 0))
        
        # Add slight color distortion
        color_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        color_surface.set_alpha(10)
        color_surface.fill((random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)))
        self.screen.blit(color_surface, (0, 0))

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.color = WHITE
    
    def move_up(self):
        if self.y > 0:
            self.y -= self.speed
    
    def move_down(self):
        if self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Ball:
    def __init__(self):
        self.reset()
        self.size = BALL_SIZE
        self.color = WHITE
        self.trail = []  # For PS1-style motion trail
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.vy = random.uniform(-BALL_SPEED/2, BALL_SPEED/2)
        self.trail = []
    
    def update(self):
        # Store previous position for trail effect
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off top and bottom walls
        if self.y <= self.size//2 or self.y >= SCREEN_HEIGHT - self.size//2:
            self.vy = -self.vy
            return "wall"
        
        return None
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PS1-Style Pong - 60fps")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game objects
        self.paddle1 = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()
        
        # Scores
        self.score1 = 0
        self.score2 = 0
        
        # Renderer
        self.renderer = PS1Renderer(self.screen)
        
        # Sound effects (sfxx=true)
        self.bounce_sound = SoundGenerator.generate_bounce_sound()
        self.score_sound = SoundGenerator.generate_score_sound()
        
        # Physics timing
        self.physics_accumulator = 0.0
        self.physics_timestep = 1.0 / FPS
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.ball.reset()
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Player 1 controls (W/S)
        if keys[pygame.K_w]:
            self.paddle1.move_up()
        if keys[pygame.K_s]:
            self.paddle1.move_down()
        
        # Player 2 controls (UP/DOWN arrows)
        if keys[pygame.K_UP]:
            self.paddle2.move_up()
        if keys[pygame.K_DOWN]:
            self.paddle2.move_down()
    
    def update_physics(self, dt):
        # Fixed timestep physics for 60fps
        self.physics_accumulator += dt
        
        while self.physics_accumulator >= self.physics_timestep:
            # Update ball
            collision = self.ball.update()
            
            if collision == "wall":
                self.bounce_sound.play()
            
            # Check paddle collisions
            ball_rect = self.ball.get_rect()
            paddle1_rect = self.paddle1.get_rect()
            paddle2_rect = self.paddle2.get_rect()
            
            if ball_rect.colliderect(paddle1_rect) and self.ball.vx < 0:
                self.ball.vx = -self.ball.vx
                self.ball.x = paddle1_rect.right + self.ball.size//2
                # Add spin based on paddle hit location
                hit_pos = (self.ball.y - self.paddle1.y) / self.paddle1.height
                self.ball.vy = (hit_pos - 0.5) * BALL_SPEED
                self.bounce_sound.play()
            
            if ball_rect.colliderect(paddle2_rect) and self.ball.vx > 0:
                self.ball.vx = -self.ball.vx
                self.ball.x = paddle2_rect.left - self.ball.size//2
                # Add spin based on paddle hit location
                hit_pos = (self.ball.y - self.paddle2.y) / self.paddle2.height
                self.ball.vy = (hit_pos - 0.5) * BALL_SPEED
                self.bounce_sound.play()
            
            # Check scoring
            if self.ball.x < 0:
                self.score2 += 1
                self.score_sound.play()
                self.ball.reset()
            elif self.ball.x > SCREEN_WIDTH:
                self.score1 += 1
                self.score_sound.play()
                self.ball.reset()
            
            self.physics_accumulator -= self.physics_timestep
    
    def render(self):
        # PS1-style rendering
        self.renderer.draw_background()
        
        # Draw game objects
        self.renderer.draw_paddle(self.paddle1.x, self.paddle1.y, GREEN)
        self.renderer.draw_paddle(self.paddle2.x, self.paddle2.y, BLUE)
        
        # Draw ball with trail effect
        for i, (x, y) in enumerate(self.ball.trail):
            alpha = int(255 * (i + 1) / len(self.ball.trail) * 0.3)
            trail_surface = pygame.Surface((self.ball.size, self.ball.size))
            trail_surface.set_alpha(alpha)
            trail_surface.fill(WHITE)
            self.screen.blit(trail_surface, (x - self.ball.size//2, y - self.ball.size//2))
        
        self.renderer.draw_ball(self.ball.x, self.ball.y, YELLOW)
        
        # Draw UI
        self.renderer.draw_ui(self.score1, self.score2)
        
        # Apply PS1 visual effects
        self.renderer.apply_ps1_effects()
        
        # Store previous ball position for blur effect
        self.renderer.prev_ball_x = self.ball.x
        self.renderer.prev_ball_y = self.ball.y
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.handle_input()
            self.update_physics(dt)
            self.render()
            
            pygame.display.flip()
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    print("PS1-Style Pong Game")
    print("===================")
    print("Controls:")
    print("Player 1: W/S keys")
    print("Player 2: UP/DOWN arrow keys")
    print("SPACE: Reset ball")
    print("ESC: Exit")
    print("\nStarting game...")
    
    game = PongGame()
    game.run()
