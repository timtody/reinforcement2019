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


class CameraAwareLayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self, target, world_size):
        super().__init__()
        self.target = target
        self.cam = pygame.Vector2(0, 0)
        self.world_size = world_size
        if self.target:
            self.add(target)

    def draw(self, surface):
        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]
            newrect = surface_blit(spr.image, spr.rect.move(self.cam))
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty


class Entity(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        
    
    def meeting_platform(self, rect):
        for p in self.platforms:
            if pygame.sprite.collide_rect(rect, p):
                return True
    
    def move(self):
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
    def __init__(self, group, platforms, coins, ghosts, pos):
        super().__init__(group)
        self.lives = 3
        self.points = 0
        self.image, self.rect = load_image('pacman.png')
        self.start = pos
        self.rect.topleft = pos
        self.movespeed = 3
        self.hsp = 0
        self.vsp = 0
        self.platforms = platforms
        self.coins = coins
        self.ghosts = ghosts
        self.lost = False
        self.reward = 0
        self.ActionSpace = ActionSpace
        self.action = ActionSpace.IDLE
        
    def update(self):
        self.reward = 0
        # get keyboard inputs
        # subject to change with simulated env
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
        
        # check for coins
        for c in self.coins:
            if pygame.sprite.collide_rect(self, c):
                c.kill()
                print("GOT REWARD YUHJUU")
                self.points += 1
                self.reward = 10
        
        # check for collision with ghosts
        for g in self.ghosts:
            if pygame.sprite.collide_rect(self, g):
                self.lives -= 1
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
    def __init__(self, group, platforms, pos):
        super().__init__(group)
        self.image, self.rect = load_image('ghost.png')
        self.start = pos
        self.rect.topleft = pos
        self.movespeed = 2
        self.hsp = 0
        self.vsp = 0
        self.platforms = platforms
        self.ActionSpace = ActionSpace
        self.action = ActionSpace.IDLE

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

        