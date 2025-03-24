import pygame
import random
import os

pygame.init()

# Initialising the mixer for sound
pygame.mixer.init()

# Loading laser sfx
laser_sound = pygame.mixer.Sound("laser_shot.mp3") 
laser_sound.set_volume(0.5)

# Loading background sound
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1) # music repeats

# Loading explosion sound
alien_explosion_sound = pygame.mixer.Sound("smash.mp3")
alien_explosion_sound.set_volume(0.5)

# Loading explosion image and resizing it to match the alien size
explosion_img = pygame.image.load("explosion.png")
explosion_img = pygame.transform.scale(explosion_img, (50,50))

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Galactic Overrun")

# Adding a var to store the highest score
high_score = 0

# Loading the score from a txt file (if not found, just start from 0)
try:
    with open("high_score.txt", "r") as file:
        high_score = int(file.read())
except FileNotFoundError:
    high_score = 0

# Loading and scaling spaceship image
spaceIng = pygame.image.load("Spaceship.png")
spaceIng = pygame.transform.scale(spaceIng, (50, 50))
spaceX = 300
spaceY = 450
space_speed = 1  # Movement speed

# Loading alien image
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

# Adding a scoring screen
score = 0
font = pygame.font.Font(None, 36) # Default font, size 36

# Adding Power Ups variables
powerups = []
shield_active = False
shield_end_time = 0

# Loading shield image
shield_img = pygame.image.load("shield.png") if os.path.exists("shield.png") else None
if shield_img:
    shield_img = pygame.transform.scale(shield_img, (30, 30))

# Loading background frames
back_frame_folder = "back_frames"
background_frames = []
for frame_file in sorted(os.listdir(back_frame_folder)):
    if frame_file.endswith(".png"):
        frame_path = os.path.join(back_frame_folder, frame_file)
        frame = pygame.image.load(frame_path)
        frame = pygame.transform.scale(frame, (800, 600))
        background_frames.append(frame)
current_frame_index = 0
frame_delay = 100  # Delay between frames in milliseconds
last_frame_update = pygame.time.get_ticks()

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
explosions = []

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

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.duration = 25
        self.alpha = 255 # fully visible

    def update(self):
        self.frame += 1
        self.alpha = max(0, 255 - (self.frame * 10)) # gradually fade out

    def draw(self):
        if self.frame < self.duration: # checking if explosion is still
            explosion_img.set_alpha(self.alpha)
            screen.blit(explosion_img, (self.x, self.y))
            return True # explosion active
        else:
            return False # explosion done
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

# Powerups class
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1.4
        self.rect = pygame.Rect(x, y, 30, 30) 
        
    def update(self):
        self.y += self.speed
        self.rect.y = self.y 
        
    def draw(self): 
        screen.blit(shield_img, (self.x, self.y))

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

# Game over message
def display_game_over():
    font_large = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 36)
    #gameover text
    text = font_large.render("GAME OVER", True, (255,0,0))
    screen.blit(text, (255,200))
    #final score
    score_text = font_small.render(f"Final Score: {score}", True, (255,255,255))
    screen.blit(score_text, (300,300))
    #high score
    high_score_text = font_small.render(f"High Score: {high_score}", True, (255,255,255))
    screen.blit(high_score_text, (300,360))
    #Instruction
    restart_text = font_small.render("Press R to Restart or Q to Quit", True, (255,255,255))
    screen.blit(restart_text, (250, 400))

# Game loop
running = True
spacebar_pressed = False  # Spacebar is pressed
while running:
    # Animated background: Load frames from 'back_frames' folder, cycle through them every 'frame_delay' ms, and draw the current frame as the background.
    # Updateing background animation
    now = pygame.time.get_ticks()
    if now - last_frame_update > frame_delay:
        current_frame_index = (current_frame_index + 1) % len(background_frames)
        last_frame_update = now

    # Draw the current background frame
    screen.blit(background_frames[current_frame_index], (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Drawing the explosions
    for explosion in explosions[:]:
        if not explosion.draw():
            explosions.remove(explosion)
        else:
            explosion.update()
    
    # Ends loop if game over
    if lives <= 0:
        with open("high_score.txt", "w") as file:
            file.write(str(high_score))
        display_game_over()
        pygame.display.update()
        waiting = True # waiting for player input
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # Restarting the game
                        lives = 5
                        score = 0
                        aliens.clear()
                        bullets.clear()
                        alien_bullets.clear()
                        waiting = False
                    if event.key == pygame.K_q: # Quiting the game
                        running = False
                        waiting = False
        continue

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
                score += 10 # Score augments
                alien_explosion_sound.play()
                if score > high_score: # Updating the value of the highest score
                    high_score = score
                spawn_aliens(random.randint(0, 2))  # Spawn new aliens
                # spawning an explosion at the alien's position
                explosions.append(Explosion(alien[0], alien[1]))
                if random.random() < 0.4: # 40% chance to drop powerup
                    powerups.append(PowerUp(alien[0], alien[1])) # spawning when alien dies
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

    # Updating and draw alien bullets
    update_alien_bullets()
    draw_alien_bullets()

    # Drawing everything
    draw_aliens()
    for bullet in bullets:
        bullet.draw()
    screen.blit(spaceIng, (spaceX, spaceY))  # Draw spaceship

    # powerup code
    for powerup in powerups[:]:
        powerup.update()
        powerup.draw()

        # Remove if off-screen
        if powerup.y > 600:
            powerups.remove(powerup)
            continue
        # collision check
        spaceship_rect = pygame.Rect(spaceX, spaceY, 50, 50)
        if powerup.rect.colliderect(spaceship_rect):
            powerups.remove(powerup)
            lives += 1  # Grant extra life
            continue

        
    # Display lives
    font = pygame.font.Font(None, 36)
    text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Displaying the score screen
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (10, 50))

    # Displaying high score
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (10, 90))

    pygame.display.update()
