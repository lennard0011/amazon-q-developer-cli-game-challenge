import pygame
import random
import time
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
GRAY = (105, 105, 105)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)
BROWN = (139, 69, 19)

# Game settings
FROG_SIZE = 30
CAR_WIDTH = 60
CAR_HEIGHT = 30
FROG_SPEED = 40
CAR_SPEED = 3
ROAD_LANES = 5
LANE_HEIGHT = 80

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        # Create simple sound effects using pygame's built-in sound generation
        try:
            # Hop sound - short beep
            self.create_hop_sound()
            # Collision sound - crash
            self.create_collision_sound()
            # Victory sound - ascending notes
            self.create_victory_sound()
            # Background ambience
            self.create_ambient_sound()
        except:
            print("Sound initialization failed - continuing without sound")
            
    def create_hop_sound(self):
        # Create a short hop sound
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 4096 * math.sin(2 * math.pi * 800 * i / sample_rate)
            wave *= (1 - i / frames)  # Fade out
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        self.sounds['hop'] = sound
        
    def create_collision_sound(self):
        # Create a crash sound
        duration = 0.3
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            # Mix of frequencies for crash effect
            wave = 2048 * (random.random() - 0.5)  # White noise
            wave *= (1 - i / frames)  # Fade out
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        self.sounds['collision'] = sound
        
    def create_victory_sound(self):
        # Create a victory sound - ascending notes
        duration = 0.8
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            freq = 400 + (i / frames) * 400  # Rising frequency
            wave = 2048 * math.sin(2 * math.pi * freq * i / sample_rate)
            wave *= math.sin(math.pi * i / frames)  # Envelope
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        self.sounds['victory'] = sound
        
    def create_ambient_sound(self):
        # Create subtle ambient sound
        duration = 2.0
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            # Low frequency rumble
            wave = 512 * math.sin(2 * math.pi * 60 * i / sample_rate)
            wave += 256 * math.sin(2 * math.pi * 120 * i / sample_rate)
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        self.sounds['ambient'] = sound
        
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, life=60):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity
        self.life -= 1
        
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
            
    def is_alive(self):
        return self.life > 0

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_explosion(self, x, y, color, count=10):
        for _ in range(count):
            vel_x = random.uniform(-3, 3)
            vel_y = random.uniform(-5, -1)
            self.particles.append(Particle(x, y, color, vel_x, vel_y, random.randint(30, 60)))
            
    def add_dust(self, x, y, count=5):
        for _ in range(count):
            vel_x = random.uniform(-1, 1)
            vel_y = random.uniform(-2, 0)
            self.particles.append(Particle(x, y, BROWN, vel_x, vel_y, random.randint(20, 40)))
            
    def update(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
            
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

class Frog:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = FROG_SIZE
        self.start_y = y
        self.animation_time = 0
        self.hop_animation = 0
        self.direction = 0  # 0=up, 1=right, 2=down, 3=left
        
    def move_up(self):
        if self.y > LANE_HEIGHT:
            self.y -= FROG_SPEED
            self.direction = 0
            self.hop_animation = 10
            return True
        return False
            
    def move_down(self):
        if self.y < SCREEN_HEIGHT - LANE_HEIGHT:
            self.y += FROG_SPEED
            self.direction = 2
            self.hop_animation = 10
            return True
        return False
            
    def move_left(self):
        if self.x > self.size // 2:
            self.x -= FROG_SPEED
            self.direction = 3
            self.hop_animation = 10
            return True
        return False
            
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.size // 2:
            self.x += FROG_SPEED
            self.direction = 1
            self.hop_animation = 10
            return True
        return False
    
    def reset_position(self):
        self.x = SCREEN_WIDTH // 2
        self.y = self.start_y
        self.hop_animation = 0
        
    def update(self):
        self.animation_time += 1
        if self.hop_animation > 0:
            self.hop_animation -= 1
        
    def draw(self, screen):
        # Calculate hop offset
        hop_offset = 0
        if self.hop_animation > 0:
            hop_offset = -int(5 * math.sin(math.pi * (10 - self.hop_animation) / 10))
        
        frog_y = int(self.y + hop_offset)
        
        # Draw frog body (more detailed)
        body_color = GREEN
        if self.hop_animation > 0:
            body_color = (min(255, GREEN[0] + 30), min(255, GREEN[1] + 30), GREEN[2])
            
        # Main body
        pygame.draw.ellipse(screen, body_color, 
                          (self.x - self.size//2, frog_y - self.size//3, 
                           self.size, self.size//1.5))
        
        # Eyes
        eye_offset = 8
        if self.direction == 1:  # Right
            eye1_pos = (int(self.x + 5), int(frog_y - 8))
            eye2_pos = (int(self.x + 5), int(frog_y + 2))
        elif self.direction == 3:  # Left
            eye1_pos = (int(self.x - 5), int(frog_y - 8))
            eye2_pos = (int(self.x - 5), int(frog_y + 2))
        else:  # Up/Down
            eye1_pos = (int(self.x - eye_offset), int(frog_y - 8))
            eye2_pos = (int(self.x + eye_offset), int(frog_y - 8))
            
        # Eye whites
        pygame.draw.circle(screen, WHITE, eye1_pos, 5)
        pygame.draw.circle(screen, WHITE, eye2_pos, 5)
        
        # Eye pupils
        pygame.draw.circle(screen, BLACK, eye1_pos, 3)
        pygame.draw.circle(screen, BLACK, eye2_pos, 3)
        
        # Legs (simple)
        leg_color = DARK_GREEN
        if self.direction == 0 or self.direction == 2:  # Up/Down
            # Side legs
            pygame.draw.ellipse(screen, leg_color,
                              (self.x - self.size//2 - 5, frog_y - 5, 8, 10))
            pygame.draw.ellipse(screen, leg_color,
                              (self.x + self.size//2 - 3, frog_y - 5, 8, 10))
        
        # Mouth
        if random.randint(0, 120) == 0:  # Occasional blink/mouth movement
            pygame.draw.arc(screen, BLACK, 
                          (self.x - 6, frog_y + 2, 12, 8), 0, math.pi, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, 
                          self.size, self.size)

class Car:
    def __init__(self, x, y, speed, color, car_type=0):
        self.x = x
        self.y = y
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.speed = speed
        self.color = color
        self.car_type = car_type  # 0=car, 1=truck, 2=sports car
        self.wheel_rotation = 0
        
        # Adjust size based on car type
        if car_type == 1:  # Truck
            self.width = CAR_WIDTH + 20
            self.height = CAR_HEIGHT + 5
        elif car_type == 2:  # Sports car
            self.width = CAR_WIDTH - 10
            self.height = CAR_HEIGHT - 5
        
    def update(self):
        self.x += self.speed
        self.wheel_rotation += abs(self.speed) * 0.2
        
        # Reset car position when it goes off screen
        if self.speed > 0 and self.x > SCREEN_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH + self.width
            
    def draw(self, screen):
        car_rect = pygame.Rect(self.x, self.y - self.height // 2, self.width, self.height)
        
        # Draw car body
        pygame.draw.rect(screen, self.color, car_rect)
        pygame.draw.rect(screen, BLACK, car_rect, 2)
        
        # Draw car details based on type
        if self.car_type == 0:  # Regular car
            # Windows
            pygame.draw.rect(screen, WHITE, 
                           (self.x + 5, self.y - self.height // 2 + 3, 15, 8))
            pygame.draw.rect(screen, WHITE, 
                           (self.x + self.width - 20, self.y - self.height // 2 + 3, 15, 8))
            # Headlights
            if self.speed < 0:  # Moving left, headlights on left
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.x + 5), int(self.y)), 3)
            else:  # Moving right, headlights on right
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.x + self.width - 5), int(self.y)), 3)
                                 
        elif self.car_type == 1:  # Truck
            # Cab windows
            pygame.draw.rect(screen, WHITE, 
                           (self.x + 5, self.y - self.height // 2 + 2, 12, 10))
            # Cargo area
            pygame.draw.rect(screen, DARK_GRAY, 
                           (self.x + 25, self.y - self.height // 2, 
                            self.width - 30, self.height))
                            
        elif self.car_type == 2:  # Sports car
            # Sleek windows
            pygame.draw.polygon(screen, WHITE, [
                (self.x + 8, self.y - self.height // 2 + 2),
                (self.x + 20, self.y - self.height // 2 + 2),
                (self.x + 18, self.y + self.height // 2 - 2),
                (self.x + 10, self.y + self.height // 2 - 2)
            ])
            # Racing stripes
            pygame.draw.rect(screen, WHITE, 
                           (self.x + self.width//2 - 1, self.y - self.height//2, 
                            2, self.height))
        
        # Draw wheels
        wheel_y = self.y + self.height // 2 - 3
        wheel1_x = self.x + 8
        wheel2_x = self.x + self.width - 8
        
        pygame.draw.circle(screen, BLACK, (int(wheel1_x), int(wheel_y)), 4)
        pygame.draw.circle(screen, BLACK, (int(wheel2_x), int(wheel_y)), 4)
        pygame.draw.circle(screen, DARK_GRAY, (int(wheel1_x), int(wheel_y)), 2)
        pygame.draw.circle(screen, DARK_GRAY, (int(wheel2_x), int(wheel_y)), 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height // 2, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Frogger - Cross the Street!")
        self.clock = pygame.time.Clock()
        
        # Initialize systems
        self.sound_manager = SoundManager()
        self.particle_system = ParticleSystem()
        
        # Game state
        self.lives = 3
        self.start_time = time.time()
        self.game_over = False
        self.won = False
        self.screen_shake = 0
        
        # Create frog
        self.frog = Frog(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        
        # Create cars
        self.cars = []
        self.create_cars()
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Background elements
        self.trees = self.create_trees()
        
    def create_trees(self):
        trees = []
        # Add trees in safe zones
        for i in range(10):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(10, LANE_HEIGHT - 20)
            trees.append((x, y))
        for i in range(8):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(SCREEN_HEIGHT - LANE_HEIGHT + 10, SCREEN_HEIGHT - 20)
            trees.append((x, y))
        return trees
        
    def create_cars(self):
        colors = [RED, BLUE, YELLOW, WHITE, ORANGE, PURPLE]
        
        for lane in range(ROAD_LANES):
            lane_y = LANE_HEIGHT + (lane + 1) * LANE_HEIGHT
            
            # Alternate direction for each lane
            if lane % 2 == 0:
                speed = random.uniform(2, 4)
                num_cars = random.randint(2, 4)
            else:
                speed = -random.uniform(2, 4)
                num_cars = random.randint(2, 4)
                
            for i in range(num_cars):
                if speed > 0:
                    x = -CAR_WIDTH - i * 200
                else:
                    x = SCREEN_WIDTH + i * 200
                    
                color = random.choice(colors)
                car_type = random.randint(0, 2)
                self.cars.append(Car(x, lane_y, speed, color, car_type))
    
    def check_collision(self):
        frog_rect = self.frog.get_rect()
        for car in self.cars:
            if frog_rect.colliderect(car.get_rect()):
                return True
        return False
    
    def check_win(self):
        return self.frog.y <= LANE_HEIGHT
    
    def handle_collision(self):
        self.sound_manager.play('collision')
        self.particle_system.add_explosion(self.frog.x, self.frog.y, RED, 15)
        self.screen_shake = 10
        self.lives -= 1
        self.frog.reset_position()
        
        if self.lives <= 0:
            self.game_over = True
    
    def get_score(self):
        return int(time.time() - self.start_time)
    
    def draw_background(self):
        # Draw gradient sky
        for y in range(LANE_HEIGHT):
            color_ratio = y / LANE_HEIGHT
            sky_color = (
                int(135 + (200 - 135) * color_ratio),
                int(206 + (230 - 206) * color_ratio),
                int(235 + (255 - 235) * color_ratio)
            )
            pygame.draw.line(self.screen, sky_color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw trees
        for tree_x, tree_y in self.trees:
            # Tree trunk
            pygame.draw.rect(self.screen, BROWN, (tree_x - 3, tree_y, 6, 15))
            # Tree leaves
            pygame.draw.circle(self.screen, DARK_GREEN, (tree_x, tree_y - 5), 8)
            pygame.draw.circle(self.screen, GREEN, (tree_x, tree_y - 5), 6)
    
    def draw_road(self):
        # Draw grass areas
        grass_color = GREEN
        pygame.draw.rect(self.screen, grass_color, (0, 0, SCREEN_WIDTH, LANE_HEIGHT))
        pygame.draw.rect(self.screen, grass_color, 
                        (0, SCREEN_HEIGHT - LANE_HEIGHT, SCREEN_WIDTH, LANE_HEIGHT))
        
        # Draw road with texture
        for lane in range(ROAD_LANES):
            lane_y = LANE_HEIGHT + lane * LANE_HEIGHT
            
            # Alternate road colors slightly
            road_color = GRAY if lane % 2 == 0 else DARK_GRAY
            pygame.draw.rect(self.screen, road_color, 
                           (0, lane_y, SCREEN_WIDTH, LANE_HEIGHT))
            
            # Draw lane dividers
            if lane < ROAD_LANES - 1:
                for x in range(0, SCREEN_WIDTH, 40):
                    pygame.draw.rect(self.screen, WHITE, 
                                   (x, lane_y + LANE_HEIGHT - 2, 20, 4))
        
        # Draw road edges
        pygame.draw.rect(self.screen, WHITE, 
                        (0, LANE_HEIGHT - 2, SCREEN_WIDTH, 4))
        pygame.draw.rect(self.screen, WHITE, 
                        (0, LANE_HEIGHT + ROAD_LANES * LANE_HEIGHT - 2, SCREEN_WIDTH, 4))
    
    def draw_ui(self):
        # Draw lives with heart icons
        for i in range(self.lives):
            heart_x = 20 + i * 30
            heart_y = 20
            # Simple heart shape
            pygame.draw.circle(self.screen, RED, (heart_x - 5, heart_y), 8)
            pygame.draw.circle(self.screen, RED, (heart_x + 5, heart_y), 8)
            pygame.draw.polygon(self.screen, RED, [
                (heart_x - 12, heart_y + 3),
                (heart_x, heart_y + 15),
                (heart_x + 12, heart_y + 3)
            ])
        
        # Draw score (time) with better styling
        score_text = self.font.render(f"Time: {self.get_score()}s", True, WHITE)
        score_shadow = self.font.render(f"Time: {self.get_score()}s", True, BLACK)
        self.screen.blit(score_shadow, (SCREEN_WIDTH - 149, 11))
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw instructions
        if not self.game_over and not self.won:
            instruction_text = self.small_font.render("Use ARROW KEYS to move. Reach the top!", True, WHITE)
            instruction_shadow = self.small_font.render("Use ARROW KEYS to move. Reach the top!", True, BLACK)
            self.screen.blit(instruction_shadow, (11, SCREEN_HEIGHT - 29))
            self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.won:
            title_text = self.font.render("CONGRATULATIONS!", True, GREEN)
            subtitle_text = self.font.render(f"You crossed in {self.get_score()} seconds!", True, WHITE)
        else:
            title_text = self.font.render("GAME OVER", True, RED)
            subtitle_text = self.font.render("You ran out of lives!", True, WHITE)
        
        restart_text = self.small_font.render("Press SPACE to play again or ESC to quit", True, WHITE)
        
        # Center the text with shadow effect
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Draw shadows
        title_shadow = self.font.render("CONGRATULATIONS!" if self.won else "GAME OVER", True, BLACK)
        subtitle_shadow = self.font.render(f"You crossed in {self.get_score()} seconds!" if self.won else "You ran out of lives!", True, BLACK)
        restart_shadow = self.small_font.render("Press SPACE to play again or ESC to quit", True, BLACK)
        
        self.screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(subtitle_shadow, (subtitle_rect.x + 2, subtitle_rect.y + 2))
        self.screen.blit(restart_shadow, (restart_rect.x + 2, restart_rect.y + 2))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.lives = 3
        self.start_time = time.time()
        self.game_over = False
        self.won = False
        self.screen_shake = 0
        self.frog.reset_position()
        
        # Reset cars
        self.cars.clear()
        self.create_cars()
        
        # Clear particles
        self.particle_system.particles.clear()
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_over or self.won:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        moved = False
                        if event.key == pygame.K_UP:
                            moved = self.frog.move_up()
                        elif event.key == pygame.K_DOWN:
                            moved = self.frog.move_down()
                        elif event.key == pygame.K_LEFT:
                            moved = self.frog.move_left()
                        elif event.key == pygame.K_RIGHT:
                            moved = self.frog.move_right()
                        
                        if moved:
                            self.sound_manager.play('hop')
                            self.particle_system.add_dust(self.frog.x, self.frog.y + 15)
            
            if not self.game_over and not self.won:
                # Update frog
                self.frog.update()
                
                # Update cars
                for car in self.cars:
                    car.update()
                
                # Update particles
                self.particle_system.update()
                
                # Check for collision
                if self.check_collision():
                    self.handle_collision()
                
                # Check for win
                if self.check_win():
                    self.won = True
                    self.sound_manager.play('victory')
                    self.particle_system.add_explosion(self.frog.x, self.frog.y, GREEN, 20)
            
            # Update screen shake
            if self.screen_shake > 0:
                self.screen_shake -= 1
            
            # Calculate screen offset for shake effect
            shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            
            # Draw everything
            self.screen.fill(BLACK)
            
            # Create a surface for the main game to apply shake effect
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            
            self.draw_background()
            self.draw_road()
            
            # Draw cars
            for car in self.cars:
                car.draw(self.screen)
            
            # Draw particles
            self.particle_system.draw(self.screen)
            
            # Draw frog
            if not self.game_over:
                self.frog.draw(self.screen)
            
            # Apply screen shake
            if self.screen_shake > 0:
                temp_surface = self.screen.copy()
                self.screen.fill(BLACK)
                self.screen.blit(temp_surface, (shake_x, shake_y))
            
            # Draw UI (not affected by shake)
            self.draw_ui()
            
            # Draw game over screen
            if self.game_over or self.won:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
