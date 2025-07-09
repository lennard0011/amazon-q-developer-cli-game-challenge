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
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GOLD = (255, 215, 0)

# Game settings
FROG_SIZE = 30
CAR_WIDTH = 60
CAR_HEIGHT = 30
FROG_SPEED = 40
CAR_SPEED = 3
ROAD_LANES = 5
LANE_HEIGHT = 80

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type  # 0=speed, 1=invincibility, 2=extra_life, 3=slow_cars, 4=jump_boost
        self.size = 20
        self.collected = False
        self.animation_time = 0
        self.spawn_time = time.time()
        self.duration = 30  # seconds before disappearing
        
        # Power-up specific properties
        self.colors = {
            0: CYAN,      # Speed boost
            1: GOLD,      # Invincibility
            2: PINK,      # Extra life
            3: PURPLE,    # Slow cars
            4: ORANGE     # Jump boost
        }
        
        self.names = {
            0: "SPEED",
            1: "SHIELD",
            2: "LIFE",
            3: "SLOW",
            4: "JUMP"
        }
    
    def update(self):
        self.animation_time += 1
        # Check if power-up should disappear
        if time.time() - self.spawn_time > self.duration:
            return False
        return True
    
    def draw(self, screen):
        if self.collected:
            return
            
        # Pulsing animation
        pulse = math.sin(self.animation_time * 0.2) * 0.3 + 0.7
        current_size = int(self.size * pulse)
        
        color = self.colors[self.power_type]
        
        # Draw outer glow
        for i in range(3):
            glow_color = (*color, 50 - i * 15)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), current_size + i * 3)
        
        # Draw main power-up
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), current_size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), current_size, 2)
        
        # Draw icon based on type
        if self.power_type == 0:  # Speed
            # Lightning bolt
            points = [
                (self.x - 5, self.y - 8),
                (self.x + 2, self.y - 2),
                (self.x - 2, self.y + 2),
                (self.x + 5, self.y + 8)
            ]
            pygame.draw.lines(screen, WHITE, False, points, 3)
        elif self.power_type == 1:  # Invincibility
            # Shield
            pygame.draw.polygon(screen, WHITE, [
                (self.x, self.y - 8),
                (self.x - 6, self.y - 4),
                (self.x - 6, self.y + 4),
                (self.x, self.y + 8),
                (self.x + 6, self.y + 4),
                (self.x + 6, self.y - 4)
            ])
        elif self.power_type == 2:  # Extra life
            # Heart
            pygame.draw.circle(screen, WHITE, (int(self.x - 3), int(self.y - 2)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x + 3), int(self.y - 2)), 3)
            pygame.draw.polygon(screen, WHITE, [
                (self.x - 6, self.y),
                (self.x, self.y + 6),
                (self.x + 6, self.y)
            ])
        elif self.power_type == 3:  # Slow cars
            # Clock
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 6, 2)
            pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x, self.y - 4), 2)
            pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x + 3, self.y), 2)
        elif self.power_type == 4:  # Jump boost
            # Arrow up
            pygame.draw.polygon(screen, WHITE, [
                (self.x, self.y - 6),
                (self.x - 4, self.y - 2),
                (self.x - 2, self.y - 2),
                (self.x - 2, self.y + 6),
                (self.x + 2, self.y + 6),
                (self.x + 2, self.y - 2),
                (self.x + 4, self.y - 2)
            ])
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
    
    def collect(self):
        self.collected = True

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
            # Power-up collect sound
            self.create_powerup_sound()
            # Power-up activate sound
            self.create_activate_sound()
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
        
    def create_powerup_sound(self):
        # Create power-up collect sound
        duration = 0.2
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            freq = 600 + math.sin(i * 0.01) * 200
            wave = 3000 * math.sin(2 * math.pi * freq * i / sample_rate)
            wave *= (1 - i / frames)  # Fade out
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        self.sounds['powerup'] = sound
        
    def create_activate_sound(self):
        # Create power-up activation sound
        duration = 0.4
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            freq = 300 + (i / frames) * 300
            wave = 2500 * math.sin(2 * math.pi * freq * i / sample_rate)
            wave *= math.sin(math.pi * i / frames)  # Envelope
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        self.sounds['activate'] = sound
        
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
            
    def add_powerup_effect(self, x, y, color, count=15):
        for _ in range(count):
            vel_x = random.uniform(-2, 2)
            vel_y = random.uniform(-3, -1)
            self.particles.append(Particle(x, y, color, vel_x, vel_y, random.randint(40, 80)))
            
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
        
        # Power-up effects
        self.speed_boost = False
        self.speed_boost_end = 0
        self.invincible = False
        self.invincible_end = 0
        self.jump_boost = False
        self.jump_boost_end = 0
        self.jump_boost_uses = 0
        
    def apply_powerup(self, power_type):
        current_time = time.time()
        
        if power_type == 0:  # Speed boost
            self.speed_boost = True
            self.speed_boost_end = current_time + 10  # 10 seconds
        elif power_type == 1:  # Invincibility
            self.invincible = True
            self.invincible_end = current_time + 8  # 8 seconds
        elif power_type == 4:  # Jump boost
            self.jump_boost = True
            self.jump_boost_end = current_time + 15  # 15 seconds
            self.jump_boost_uses = 3  # 3 double jumps
        
    def update_powerups(self):
        current_time = time.time()
        
        # Update speed boost
        if self.speed_boost and current_time > self.speed_boost_end:
            self.speed_boost = False
            
        # Update invincibility
        if self.invincible and current_time > self.invincible_end:
            self.invincible = False
            
        # Update jump boost
        if self.jump_boost and current_time > self.jump_boost_end:
            self.jump_boost = False
            self.jump_boost_uses = 0
        
    def move_up(self):
        move_distance = FROG_SPEED * 2 if self.speed_boost else FROG_SPEED
        
        if self.y > LANE_HEIGHT:
            self.y -= move_distance
            self.direction = 0
            self.hop_animation = 10
            return True
        return False
            
    def move_down(self):
        move_distance = FROG_SPEED * 2 if self.speed_boost else FROG_SPEED
        
        if self.y < SCREEN_HEIGHT - LANE_HEIGHT:
            self.y += move_distance
            self.direction = 2
            self.hop_animation = 10
            return True
        return False
            
    def move_left(self):
        move_distance = FROG_SPEED * 2 if self.speed_boost else FROG_SPEED
        
        if self.x > self.size // 2:
            self.x -= move_distance
            self.direction = 3
            self.hop_animation = 10
            return True
        return False
            
    def move_right(self):
        move_distance = FROG_SPEED * 2 if self.speed_boost else FROG_SPEED
        
        if self.x < SCREEN_WIDTH - self.size // 2:
            self.x += move_distance
            self.direction = 1
            self.hop_animation = 10
            return True
        return False
    
    def reset_position(self):
        self.x = SCREEN_WIDTH // 2
        self.y = self.start_y
        self.hop_animation = 0
        # Keep power-ups when respawning
        
    def update(self):
        self.animation_time += 1
        if self.hop_animation > 0:
            self.hop_animation -= 1
        self.update_powerups()
        
    def draw(self, screen):
        # Calculate hop offset
        hop_offset = 0
        if self.hop_animation > 0:
            hop_offset = -int(5 * math.sin(math.pi * (10 - self.hop_animation) / 10))
        
        frog_y = int(self.y + hop_offset)
        
        # Draw frog body (more detailed)
        body_color = GREEN
        
        # Color changes based on power-ups
        if self.invincible:
            # Flashing golden color
            if int(self.animation_time / 5) % 2:
                body_color = GOLD
        elif self.speed_boost:
            body_color = CYAN
        elif self.jump_boost:
            body_color = ORANGE
        elif self.hop_animation > 0:
            body_color = (min(255, GREEN[0] + 30), min(255, GREEN[1] + 30), GREEN[2])
            
        # Draw invincibility shield
        if self.invincible:
            shield_radius = self.size + 5 + int(3 * math.sin(self.animation_time * 0.3))
            pygame.draw.circle(screen, GOLD, (int(self.x), frog_y), shield_radius, 3)
            
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
        self.original_speed = speed
        self.color = color
        self.car_type = car_type  # 0=car, 1=truck, 2=sports car
        self.wheel_rotation = 0
        self.slow_effect = False
        self.slow_end_time = 0
        
        # Adjust size based on car type
        if car_type == 1:  # Truck
            self.width = CAR_WIDTH + 20
            self.height = CAR_HEIGHT + 5
        elif car_type == 2:  # Sports car
            self.width = CAR_WIDTH - 10
            self.height = CAR_HEIGHT - 5
    
    def apply_slow_effect(self, duration=8):
        self.slow_effect = True
        self.slow_end_time = time.time() + duration
        self.speed = self.original_speed * 0.3  # Slow to 30% speed
        
    def update(self):
        # Check if slow effect should end
        if self.slow_effect and time.time() > self.slow_end_time:
            self.slow_effect = False
            self.speed = self.original_speed
            
        self.x += self.speed
        self.wheel_rotation += abs(self.speed) * 0.2
        
        # Reset car position when it goes off screen
        if self.speed > 0 and self.x > SCREEN_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH + self.width
            
    def draw(self, screen):
        car_rect = pygame.Rect(self.x, self.y - self.height // 2, self.width, self.height)
        
        # Draw car body (tinted if slowed)
        car_color = self.color
        if self.slow_effect:
            # Add blue tint for slow effect
            car_color = tuple(min(255, c + 50) if i == 2 else max(0, c - 30) for i, c in enumerate(self.color))
        
        pygame.draw.rect(screen, car_color, car_rect)
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
        
        # Draw slow effect indicator
        if self.slow_effect:
            # Draw blue particles around car
            for i in range(3):
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                pygame.draw.circle(screen, BLUE, 
                                 (int(self.x + self.width//2 + offset_x), 
                                  int(self.y + offset_y)), 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height // 2, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Frogger with Power-ups!")
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
        self.score = 0
        
        # Create frog
        self.frog = Frog(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        
        # Create cars
        self.cars = []
        self.create_cars()
        
        # Power-ups
        self.powerups = []
        self.last_powerup_spawn = time.time()
        self.powerup_spawn_interval = 15  # seconds
        self.active_powerup_effects = []
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        
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
    
    def spawn_powerup(self):
        # Spawn power-up in a safe location
        safe_zones = [
            (random.randint(50, SCREEN_WIDTH - 50), random.randint(20, LANE_HEIGHT - 20)),
            (random.randint(50, SCREEN_WIDTH - 50), random.randint(SCREEN_HEIGHT - LANE_HEIGHT + 20, SCREEN_HEIGHT - 50))
        ]
        
        # Also spawn on road (more risky but accessible)
        for lane in range(ROAD_LANES):
            lane_y = LANE_HEIGHT + (lane + 1) * LANE_HEIGHT
            safe_zones.append((random.randint(100, SCREEN_WIDTH - 100), lane_y))
        
        spawn_pos = random.choice(safe_zones)
        power_type = random.randint(0, 4)  # 5 different power-up types
        
        self.powerups.append(PowerUp(spawn_pos[0], spawn_pos[1], power_type))
        self.last_powerup_spawn = time.time()
    
    def check_powerup_collection(self):
        frog_rect = self.frog.get_rect()
        for powerup in self.powerups[:]:  # Use slice to avoid modification during iteration
            if not powerup.collected and frog_rect.colliderect(powerup.get_rect()):
                self.collect_powerup(powerup)
                
    def collect_powerup(self, powerup):
        powerup.collect()
        self.sound_manager.play('powerup')
        
        # Create particle effect
        self.particle_system.add_powerup_effect(powerup.x, powerup.y, powerup.colors[powerup.power_type])
        
        # Apply power-up effect
        if powerup.power_type == 0:  # Speed boost
            self.frog.apply_powerup(0)
            self.add_powerup_message("SPEED BOOST!", CYAN)
        elif powerup.power_type == 1:  # Invincibility
            self.frog.apply_powerup(1)
            self.add_powerup_message("INVINCIBLE!", GOLD)
        elif powerup.power_type == 2:  # Extra life
            self.lives += 1
            self.add_powerup_message("EXTRA LIFE!", PINK)
        elif powerup.power_type == 3:  # Slow cars
            for car in self.cars:
                car.apply_slow_effect()
            self.add_powerup_message("CARS SLOWED!", PURPLE)
        elif powerup.power_type == 4:  # Jump boost
            self.frog.apply_powerup(4)
            self.add_powerup_message("JUMP BOOST!", ORANGE)
            
        self.sound_manager.play('activate')
        self.score += 100  # Bonus points for collecting power-up
        
        # Remove collected power-up
        self.powerups.remove(powerup)
    
    def add_powerup_message(self, message, color):
        self.active_powerup_effects.append({
            'message': message,
            'color': color,
            'time': time.time(),
            'duration': 3.0
        })
    
    def check_collision(self):
        if self.frog.invincible:
            return False
            
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
        time_score = int(time.time() - self.start_time)
        return self.score + max(0, 1000 - time_score * 10)  # Bonus for speed
    
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
        
        # Draw score
        score_text = self.font.render(f"Score: {self.get_score()}", True, WHITE)
        score_shadow = self.font.render(f"Score: {self.get_score()}", True, BLACK)
        self.screen.blit(score_shadow, (SCREEN_WIDTH - 149, 11))
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw time
        time_text = self.small_font.render(f"Time: {int(time.time() - self.start_time)}s", True, WHITE)
        time_shadow = self.small_font.render(f"Time: {int(time.time() - self.start_time)}s", True, BLACK)
        self.screen.blit(time_shadow, (SCREEN_WIDTH - 149, 41))
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 40))
        
        # Draw active power-up status
        y_offset = 70
        if self.frog.speed_boost:
            remaining = max(0, int(self.frog.speed_boost_end - time.time()))
            boost_text = self.tiny_font.render(f"SPEED: {remaining}s", True, CYAN)
            self.screen.blit(boost_text, (10, y_offset))
            y_offset += 20
            
        if self.frog.invincible:
            remaining = max(0, int(self.frog.invincible_end - time.time()))
            shield_text = self.tiny_font.render(f"SHIELD: {remaining}s", True, GOLD)
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 20
            
        if self.frog.jump_boost:
            remaining = max(0, int(self.frog.jump_boost_end - time.time()))
            jump_text = self.tiny_font.render(f"JUMP: {remaining}s ({self.frog.jump_boost_uses} uses)", True, ORANGE)
            self.screen.blit(jump_text, (10, y_offset))
            y_offset += 20
        
        # Draw power-up messages
        current_time = time.time()
        for effect in self.active_powerup_effects[:]:
            if current_time - effect['time'] > effect['duration']:
                self.active_powerup_effects.remove(effect)
            else:
                alpha = 1.0 - (current_time - effect['time']) / effect['duration']
                message_y = SCREEN_HEIGHT // 2 - 50
                message_text = self.font.render(effect['message'], True, effect['color'])
                message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, message_y))
                self.screen.blit(message_text, message_rect)
        
        # Draw instructions
        if not self.game_over and not self.won:
            instruction_text = self.small_font.render("Arrow keys to move • Collect power-ups!", True, WHITE)
            instruction_shadow = self.small_font.render("Arrow keys to move • Collect power-ups!", True, BLACK)
            self.screen.blit(instruction_shadow, (11, SCREEN_HEIGHT - 29))
            self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.won:
            title_text = self.font.render("CONGRATULATIONS!", True, GREEN)
            subtitle_text = self.font.render(f"Final Score: {self.get_score()}", True, WHITE)
        else:
            title_text = self.font.render("GAME OVER", True, RED)
            subtitle_text = self.font.render(f"Final Score: {self.get_score()}", True, WHITE)
        
        restart_text = self.small_font.render("Press SPACE to play again or ESC to quit", True, WHITE)
        
        # Center the text with shadow effect
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Draw shadows
        title_shadow = self.font.render("CONGRATULATIONS!" if self.won else "GAME OVER", True, BLACK)
        subtitle_shadow = self.font.render(f"Final Score: {self.get_score()}", True, BLACK)
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
        self.score = 0
        self.frog.reset_position()
        
        # Reset power-ups
        self.powerups.clear()
        self.active_powerup_effects.clear()
        self.last_powerup_spawn = time.time()
        
        # Reset frog power-ups
        self.frog.speed_boost = False
        self.frog.invincible = False
        self.frog.jump_boost = False
        
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
                
                # Update power-ups
                for powerup in self.powerups[:]:
                    if not powerup.update():
                        self.powerups.remove(powerup)
                
                # Spawn new power-ups
                if time.time() - self.last_powerup_spawn > self.powerup_spawn_interval:
                    self.spawn_powerup()
                
                # Check power-up collection
                self.check_powerup_collection()
                
                # Check for collision
                if self.check_collision():
                    self.handle_collision()
                
                # Check for win
                if self.check_win():
                    self.won = True
                    self.sound_manager.play('victory')
                    self.particle_system.add_explosion(self.frog.x, self.frog.y, GREEN, 20)
                    self.score += 500  # Bonus for winning
            
            # Update screen shake
            if self.screen_shake > 0:
                self.screen_shake -= 1
            
            # Calculate screen offset for shake effect
            shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            
            # Draw everything
            self.screen.fill(BLACK)
            
            self.draw_background()
            self.draw_road()
            
            # Draw power-ups
            for powerup in self.powerups:
                powerup.draw(self.screen)
            
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
