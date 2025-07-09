import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Game settings
FROG_SIZE = 30
CAR_WIDTH = 60
CAR_HEIGHT = 30
FROG_SPEED = 40
CAR_SPEED = 3
ROAD_LANES = 5
LANE_HEIGHT = 80

class Frog:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = FROG_SIZE
        self.start_y = y
        
    def move_up(self):
        if self.y > LANE_HEIGHT:
            self.y -= FROG_SPEED
            
    def move_down(self):
        if self.y < SCREEN_HEIGHT - LANE_HEIGHT:
            self.y += FROG_SPEED
            
    def move_left(self):
        if self.x > self.size // 2:
            self.x -= FROG_SPEED
            
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.size // 2:
            self.x += FROG_SPEED
    
    def reset_position(self):
        self.x = SCREEN_WIDTH // 2
        self.y = self.start_y
        
    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.size // 2)
        # Draw simple frog eyes
        pygame.draw.circle(screen, BLACK, (int(self.x - 8), int(self.y - 8)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + 8), int(self.y - 8)), 3)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, 
                          self.size, self.size)

class Car:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.speed = speed
        self.color = color
        
    def update(self):
        self.x += self.speed
        # Reset car position when it goes off screen
        if self.speed > 0 and self.x > SCREEN_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH + self.width
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y - self.height // 2, self.width, self.height))
        # Draw simple car details
        pygame.draw.rect(screen, WHITE, 
                        (self.x + 5, self.y - self.height // 2 + 5, 15, 8))
        pygame.draw.rect(screen, WHITE, 
                        (self.x + self.width - 20, self.y - self.height // 2 + 5, 15, 8))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y - self.height // 2, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Frogger - Cross the Street!")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.lives = 3
        self.start_time = time.time()
        self.game_over = False
        self.won = False
        
        # Create frog
        self.frog = Frog(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        
        # Create cars
        self.cars = []
        self.create_cars()
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def create_cars(self):
        colors = [RED, BLUE, YELLOW, WHITE]
        
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
                self.cars.append(Car(x, lane_y, speed, color))
    
    def check_collision(self):
        frog_rect = self.frog.get_rect()
        for car in self.cars:
            if frog_rect.colliderect(car.get_rect()):
                return True
        return False
    
    def check_win(self):
        return self.frog.y <= LANE_HEIGHT
    
    def handle_collision(self):
        self.lives -= 1
        self.frog.reset_position()
        
        if self.lives <= 0:
            self.game_over = True
    
    def get_score(self):
        return int(time.time() - self.start_time)
    
    def draw_road(self):
        # Draw grass areas
        pygame.draw.rect(self.screen, GREEN, (0, 0, SCREEN_WIDTH, LANE_HEIGHT))
        pygame.draw.rect(self.screen, GREEN, 
                        (0, SCREEN_HEIGHT - LANE_HEIGHT, SCREEN_WIDTH, LANE_HEIGHT))
        
        # Draw road
        for lane in range(ROAD_LANES):
            lane_y = LANE_HEIGHT + lane * LANE_HEIGHT
            pygame.draw.rect(self.screen, GRAY, 
                           (0, lane_y, SCREEN_WIDTH, LANE_HEIGHT))
            
            # Draw lane dividers
            if lane < ROAD_LANES - 1:
                for x in range(0, SCREEN_WIDTH, 40):
                    pygame.draw.rect(self.screen, WHITE, 
                                   (x, lane_y + LANE_HEIGHT - 2, 20, 4))
    
    def draw_ui(self):
        # Draw lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 10))
        
        # Draw score (time)
        score_text = self.font.render(f"Time: {self.get_score()}s", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw instructions
        if not self.game_over and not self.won:
            instruction_text = self.small_font.render("Use ARROW KEYS to move. Reach the top!", True, WHITE)
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
        
        # Center the text
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.lives = 3
        self.start_time = time.time()
        self.game_over = False
        self.won = False
        self.frog.reset_position()
        
        # Reset cars
        self.cars.clear()
        self.create_cars()
    
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
                        if event.key == pygame.K_UP:
                            self.frog.move_up()
                        elif event.key == pygame.K_DOWN:
                            self.frog.move_down()
                        elif event.key == pygame.K_LEFT:
                            self.frog.move_left()
                        elif event.key == pygame.K_RIGHT:
                            self.frog.move_right()
            
            if not self.game_over and not self.won:
                # Update cars
                for car in self.cars:
                    car.update()
                
                # Check for collision
                if self.check_collision():
                    self.handle_collision()
                
                # Check for win
                if self.check_win():
                    self.won = True
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_road()
            
            # Draw cars
            for car in self.cars:
                car.draw(self.screen)
            
            # Draw frog
            if not self.game_over and not self.won:
                self.frog.draw(self.screen)
            
            # Draw UI
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
