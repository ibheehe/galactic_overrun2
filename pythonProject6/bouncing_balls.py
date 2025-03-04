import pygame

pygame.init()

screen = pygame.display.set_mode((800,600))

pygame.display.set_caption("Galactic Overrun")

spaceIng = pygame.image.load("Spaceship.png")
spaceX = 300
spaceY = 450

def space():
    screen.blit(spaceIng,(spaceX,spaceY))

playerIng = pygame.image.load("Alien.png")
playerX = 250
playerY = 50

def player():
    screen.blit(playerIng,(playerX,playerY))

running = True
while running:

    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    player()
    space()
    pygame.display.update()