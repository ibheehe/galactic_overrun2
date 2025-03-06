import pygame
import random

pygame.init()

# Initialize the mixer for sound
pygame.mixer.init()

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

def spawn_aliens(num_aliens):
    current_aliens = len(aliens)
    available_space = max_aliens - current_aliens
    num_aliens_to_spawn = min(num_aliens, available_space)  # Ensure we don't exceed the cap

    for _ in range(num_aliens_to_spawn):
        alienX = random.randint(50, 750)  # Random X position
        alienY = random.randint(20, 100)  # Random Y start position
        alien_speed = random.uniform(0.1, 0.3)  # Random speed for variation
        aliens.append([alienX, alienY, alien_speed])  # Add new alien to the list

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
        # Check for collision with alien
        alien_rect = pygame.Rect(alien[0], alien[1], 50, 50)  # Alien rectangle
        bullet_rect = pygame.Rect(self.x, self.y, self.width, self.height)  # Bullet rectangle
        return bullet_rect.colliderect(alien_rect)  # Check if they collide

def shoot_bullet():
    laser_sound.play()  # laser sfx play
    bullet = Bullet(spaceX + 22, spaceY)  # Spawn bullet from spaceship
    bullets.append(bullet)

# game over message
def display_game_over():
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(text, (250, 250))

# Game loop
running = True
spacebar_pressed = False  # spacebar is pressed
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ends loop if game over
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

    # shoot of spacebar is pressed to prevent a beam and not bullets
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

        # Remove bullet if it moves off-screen
        if bullet.y < 0:
            bullets.remove(bullet)

        # Check for collision with each alien
        for alien in aliens[:]:
            if bullet.collides_with(alien):
                # Remove the alien and the bullet on collision
                aliens.remove(alien)
                bullets.remove(bullet)

                # Spawn a random number of new aliens

                num_new_aliens = random.randint(0, 2)  # Spawn aliens after they die
                spawn_aliens(num_new_aliens)
                break  # Exit loop once collision is detected

    # Move aliens downward and spawn new ones when they move off the screen
    for alien in aliens[:]:
        alien[1] += alien[2]  # Move each alien down based on its speed

        # If alien moves off screen, remove it and spawn new aliens
        if alien[1] > 600:  # Alien goes off the screen at the bottom
            aliens.remove(alien)
            num_new_aliens = random.randint(0, 2)  # Spawn between 0 and 3 new aliens
            spawn_aliens(num_new_aliens)

            # Increase the alien hit count and check if game over
            alien_hit_count += 1
            if alien_hit_count >= 5:  # If 5 aliens hit the bottom, decrease a life
                lives -= 1  # Decrease lives instead of setting to 0
                alien_hit_count = 0  # Reset the alien hit count after losing a life

    # If there are no aliens, spawn a new group, ensuring the cap is not exceeded
    if len(aliens) == 0:
        num_new_aliens = random.randint(0, 2)  # Spawn between 0 and 3 new aliens
        spawn_aliens(num_new_aliens)

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
