import pygame
import random

pygame.init()

# Initialize the mixer for sound
pygame.mixer.init()


# Initialize the mixer for sound
pygame.mixer.init()

# Load and play background music on a loop
pygame.mixer.music.load("background_music.mp3")  # Replace with your actual music file
pygame.mixer.music.set_volume(0.5)  # Adjust volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # -1 makes it loop indefinitely


# Load and laser sfx
laser_sound = pygame.mixer.Sound("laser_shot.mp3")  # Replace with your actual sound file

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Galactic Overrun")

# Load and scale spaceship image
spaceIng = pygame.image.load("Spaceship.png")
spaceIng = pygame.transform.scale(spaceIng, (50, 50))
spaceX = 300
spaceY = 450
space_speed = 1  # Movement speed

# Load alien image
playerIng = pygame.image.load("alien.png")
playerIng = pygame.transform.scale(playerIng, (50, 50))

# Enemy setup
aliens = []
max_aliens = 30  # Cap of maximum aliens allowed at a time
lives = 5  # Starting lives
alien_hit_count = 0  # Count of aliens that have reached the bottom

# Alien bullet setup
alien_bullets = []
alien_bullet_speed = 3

def spawn_aliens(num_aliens):
    current_aliens = len(aliens)
    available_space = max_aliens - current_aliens
    num_aliens_to_spawn = min(num_aliens, available_space)  # Ensure we don't exceed the cap

    for _ in range(num_aliens_to_spawn):
        alienX = random.randint(50, 750)  # Random X position
        alienY = random.randint(20, 100)  # Random Y start position
        alien_speed = random.uniform(0.1, 0.1)  # Random speed for variation, changed to set speed
        shoot_timer = random.randint(60, 180)  # Random shooting interval (1-3 seconds)
        aliens.append([alienX, alienY, alien_speed, shoot_timer])  # Add new alien with timer

def draw_aliens():
    for alien in aliens:
        screen.blit(playerIng, (alien[0], alien[1]))

# Bullet setup
bullet_speed = 7
bullets = []

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 10
        self.speed = bullet_speed

    def move(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))

    def collides_with(self, alien):
        alien_rect = pygame.Rect(alien[0], alien[1], 50, 50)  # Alien rectangle
        bullet_rect = pygame.Rect(self.x, self.y, self.width, self.height)  # Bullet rectangle
        return bullet_rect.colliderect(alien_rect)  # Check collision

def shoot_bullet():
    laser_sound.play()  # Laser sfx play
    bullet = Bullet(spaceX + 22, spaceY)  # Spawn bullet from spaceship
    bullets.append(bullet)

# Alien bullet class
class AlienBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 10
        self.speed = alien_bullet_speed

    def move(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))

    def collides_with_spaceship(self):
        spaceship_rect = pygame.Rect(spaceX, spaceY, 50, 50)
        bullet_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return bullet_rect.colliderect(spaceship_rect)

def update_alien_bullets():
    global lives
    for bullet in alien_bullets[:]:
        bullet.move()
        if bullet.y > 600:  # Remove if it goes off-screen
            alien_bullets.remove(bullet)
        elif bullet.collides_with_spaceship():
            alien_bullets.remove(bullet)
            lives -= 1  # Reduce lives if hit

def draw_alien_bullets():
    for bullet in alien_bullets:
        bullet.draw()

# game over message
def display_game_over():
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(text, (250, 250))

# Game loop
running = True
spacebar_pressed = False  # Spacebar is pressed
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Ends loop if game over
    if lives <= 0:
        display_game_over()
        pygame.display.update()
        pygame.time.wait(2000)  # Wait for 2 seconds before closing
        running = False
        break

    # Move spaceship
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and spaceX > 0:
        spaceX -= space_speed
    if keys[pygame.K_d] and spaceX < 750:
        spaceX += space_speed

    # Shoot if spacebar is pressed
    if keys[pygame.K_SPACE]:
        if not spacebar_pressed:  # Only shoot if spacebar was not previously pressed
            shoot_bullet()
            spacebar_pressed = True  # Set to True so it doesn't keep shooting
    else:
        spacebar_pressed = False  # Reset when spacebar is released

    # Move and draw bullets
    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()
        if bullet.y < 0:
            bullets.remove(bullet)

        # Check for collision with each alien
        for alien in aliens[:]:
            if bullet.collides_with(alien):
                aliens.remove(alien)
                bullets.remove(bullet)
                spawn_aliens(random.randint(0, 2))  # Spawn new aliens
                break  # Exit loop once collision is detected

    # Move aliens downward and spawn new ones when they move off the screen
    for alien in aliens[:]:
        alien[1] += alien[2]  # Move each alien down based on its speed

        # Alien shooting logic
        alien[3] -= 1  # Decrease the shoot timer
        if alien[3] <= 0:  # Time to shoot
            alien_bullets.append(AlienBullet(alien[0] + 22, alien[1] + 50))
            alien[3] = random.randint(60, 180)  # Reset shoot timer (1-3 seconds)

        # If alien moves off screen, remove it and spawn new ones
        if alien[1] > 600:
            aliens.remove(alien)
            spawn_aliens(random.randint(0, 2))
            alien_hit_count += 1
            if alien_hit_count >= 5:
                lives -= 1
                alien_hit_count = 0

    # If there are no aliens, spawn a new group
    if len(aliens) == 0:
        spawn_aliens(random.randint(0, 2))

    # Update and draw alien bullets
    update_alien_bullets()
    draw_alien_bullets()

    # Draw everything
    draw_aliens()
    for bullet in bullets:
        bullet.draw()
    screen.blit(spaceIng, (spaceX, spaceY))  # Draw spaceship

    # Display lives
    font = pygame.font.Font(None, 36)
    text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.update()
