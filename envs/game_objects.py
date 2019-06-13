import pygame
import os
import numpy as np
from pygame.locals import *
from .actionspace import ActionSpace


def load_image(name, colorkey=None):
    fullname = os.path.join('img', name)
    try:
        image = pygame.image.load(fullname)
    except Exception as e:
        raise e
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_images_directional(name):
    """loads images with named directional suffixes
    
    Arguments:
        name {string} -- name
    
    Returns:
        [list] -- [images in order of right, down, left, up]
        [pygame.rect] -- [the corresponding rectangle for position and movement]
    """
    name = name.split(".")[0]
    directions = [name+"_right.png", name+"_down.png", name+"_left.png", name+"_up.png"]
    join = lambda x: os.path.join("img", x)
    fullnames = map(join, directions)
    images = []
    for name in fullnames:
        im = pygame.image.load(name)
        images.append(im)
    rect = images[0].get_rect()

    return images, rect
    

class Entity(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.lastValidMove = [0,0]
        
    
    def meeting_platform(self, rect):
        for p in self.platforms:
            if pygame.sprite.collide_rect(rect, p):
                return True
    
    def move(self,secondTry=False):
        # horizontal collision and movement
        if self.meeting_platform(self.rect.move([self.hsp, 0])):
            while not self.meeting_platform(self.rect.move([np.sign(self.hsp), 0])):
                self.rect = self.rect.move([np.sign(self.hsp), 0])
            self.hsp = 0
        self.rect = self.rect.move([self.hsp, 0])

        # vertical collision and movement
        if self.meeting_platform(self.rect.move([0, self.vsp])):
            while not self.meeting_platform(self.rect.move([0, np.sign(self.vsp)])):
                self.rect = self.rect.move([0, np.sign(self.vsp)])
            self.vsp = 0
        self.rect = self.rect.move([0, self.vsp])
    
    def move_with_validity_check(self,secondTry=False):
        hspValid = False
        vspValid = False
        # horizontal collision and movement
        if self.meeting_platform(self.rect.move([self.hsp, 0])):
            while not self.meeting_platform(self.rect.move([np.sign(self.hsp), 0])):
                self.rect = self.rect.move([np.sign(self.hsp), 0])
            self.hsp = 0
        else:
            hspValid = True

        #self.rect = self.rect.move([self.hsp, 0])

        # vertical collision and movement
        if self.meeting_platform(self.rect.move([0, self.vsp])):
            while not self.meeting_platform(self.rect.move([0, np.sign(self.vsp)])):
                self.rect = self.rect.move([0, np.sign(self.vsp)])
            self.vsp = 0
        else:
            vspValid = True
        
        if hspValid and vspValid:
            if self.vsp and self.hsp:
                print('Sanity Check failed')
                exit(0)
            
            self.rect = self.rect.move([self.hsp, self.vsp])
            self.lastValidMove = [self.hsp, self.vsp]
            return

        elif not secondTry:
            self.hsp, self.vsp = self.lastValidMove
            self.move(secondTry=True)
        
        #self.rect = self.rect.move([0, self.vsp])


class Wall(Entity):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image, self.rect = load_image('wall.png')
        self.rect.topleft = pos


class Coin(Entity):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image, self.rect = load_image('coin.png')
        self.rect.topleft = pos


class PacMan(Entity):
    def __init__(self, group, platforms, coins, ghosts, pos, lives, coinReward, noCoinReward, ghostColReward):
        super().__init__(group)
        self.lives = lives
        self.points = 0
        self.images, self.rect = load_images_directional('pacman.png')
        self.image = self.images[0]
        self.start = pos
        self.rect.topleft = pos
        self.movespeed = 32
        self.hsp = 0
        self.vsp = 0
        self.rotation_angle = 0
        self.platforms = platforms
        self.coins = coins
        self.ghosts = ghosts
        self.lost = False
        self.reward = 0
        self.ActionSpace = ActionSpace
        self.action = ActionSpace.IDLE
        self.coinReward = coinReward
        self.noCoinReward = noCoinReward
        self.ghostColReward = ghostColReward
    
    def rotate(self):
        if self.action == ActionSpace.RIGHT:
            self.image = self.images[0]
        if self.action == ActionSpace.LEFT:
            self.image = self.images[2]
        if self.action == ActionSpace.UP:
            self.image = self.images[1]
        if self.action == ActionSpace.DOWN:
            self.image = self.images[3]
        
    def update(self):
        self.reward = self.noCoinReward
        # undo rotation from previous game step
        #self.rotate(-self.rotation_angle)
        
        # set the movement parameters of the agent
        if self.action == self.ActionSpace.IDLE:
            move_h = 0
            move_v = 0
        if self.action == self.ActionSpace.UP:
            move_h = 0
            move_v = -1
            #self.rotate(90)
        if self.action == self.ActionSpace.DOWN:
            move_h = 0
            move_v = 1
            #self.rotate(270)
        if self.action == self.ActionSpace.LEFT:
            move_h = -1
            move_v = 0
            #self.rotate(180)
        if self.action == self.ActionSpace.RIGHT:
            move_h = 1
            move_v = 0
            #self.rotate(0)

        self.hsp = move_h*self.movespeed
        self.vsp = move_v*self.movespeed
        # horizontal collision and movement 
        self.move()
        self.rotate()
        
        
        # check for coins
        for c in self.coins:
            if pygame.sprite.collide_rect(self, c):
                c.kill()
                self.points += 1
                self.reward = self.coinReward
        
        # check for collision with ghosts
        for g in self.ghosts:
            if pygame.sprite.collide_rect(self, g):
                self.lives -= 1
                self.reward = self.ghostColReward
                g.reward = 10
                self.rect.topleft = self.start
                for g in self.ghosts:
                    g.rect.topleft = g.start
                break
            else:
                g.reward = 0
                # todo: reset ghosts and player positions
        
        # check for lives
        if self.lives == 0:
            self.lost = True


class Ghost(Entity):
    def __init__(self, group, platforms, playables, pos, movespeed):
        super().__init__(group)
        self.image, self.rect = load_image('ghost.png')
        self.start = pos
        self.rect.topleft = pos
        self.movespeed = movespeed
        self.hsp = 0
        self.vsp = 0
        self.platforms = platforms
        self.ActionSpace = ActionSpace
        self.action = ActionSpace.IDLE
        # first index of sprite group is pacman
        self.pacman = playables
        self.reward = 0
    
    def distance_to_pacman(self):
        pacman = self.pacman.sprites()[0]
        ghost_pos = np.array(self.rect.topleft)
        pacman_pos = np.array(pacman.rect.topleft)
        dist = np.linalg.norm(ghost_pos - pacman_pos)
        
        return dist

    def update(self):
        if self.action == self.ActionSpace.IDLE:
            move_h = 0
            move_v = 0
        if self.action == self.ActionSpace.UP:
            move_h = 0
            move_v = -1
        if self.action == self.ActionSpace.DOWN:
            move_h = 0
            move_v = 1
        if self.action == self.ActionSpace.LEFT:
            move_h = -1
            move_v = 0
        if self.action == self.ActionSpace.RIGHT:
            move_h = 1
            move_v = 0

        self.hsp = move_h*self.movespeed
        self.vsp = move_v*self.movespeed

        # horizontal collision and movement
        self.move()
        # uncomment if need be
        #self.distance_to_pacman = self.distance_to_pacman()