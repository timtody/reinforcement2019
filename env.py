import pygame, sys
from pygame.locals import QUIT, KEYDOWN



def get_movesets(movespeed: int):
    keys = pygame.key.get_pressed()
    key_left = keys[pygame.K_a]        
    key_right = keys[pygame.K_d]
    key_up = keys[pygame.K_w]        
    key_down = keys[pygame.K_s]

    move_h = movespeed*(key_right - key_left)
    move_v = movespeed*(key_down - key_up)
    
    return move_h, move_v


width = 1280
height = 720
size = width, height
speed = [1, 2]
black = 0, 0, 0
x = y = 0
movesp = 1

screen = pygame.display.set_mode(size)
ball = pygame.image.load("img/pacman.png")
wall = pygame.image.load("img/wall.png")
ballrect = ball.get_rect()
wallrect = wall.get_rect()

while 1:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()

    move_h, move_v = get_movesets(movesp)

    ballrect = ballrect.move([move_h, move_v])

    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()