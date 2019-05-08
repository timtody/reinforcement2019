import pygame
import os
import numpy as np
from pygame.locals import *
from globals import GLOBALS


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
    def __init__(self, color, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((GLOBALS.TILE_SIZE, GLOBALS.TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)


class Wall(Entity):
    def __init__(self, pos, *groups):
        super().__init__(Color("#DDDDDD"), pos, *groups)


class PacMan(Entity):
    def __init__(self, platforms, pos, *groups):
        super().__init__(Color("#0000FF"), pos)
        self.image, self.rect = load_image('pacman.png')
        self.movespeed = 5
        self.hsp = 0
        self.vsp = 0
        self.platforms = platforms

    def update(self):
        # get keyboard inputs
        # subject to change with simulated env
        pressed = pygame.key.get_pressed()
        key_left = pressed[pygame.K_a]
        key_right = pressed[pygame.K_d]
        key_up = pressed[pygame.K_w]
        key_down = pressed[pygame.K_s]

        move_h = key_right - key_left
        move_v = key_down - key_up
        self.hsp = move_h*self.movespeed
        self.vsp = move_v*self.movespeed

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

    def collide(self):
        for p in self.platforms:
            if pygame.sprite.collide_rect(self.rect.move([self.hsp, self.vsp]), p):
                while not pygame.sprite.collide_rect(self.rect.move([np.sign(self.hsp), np.sign(self.vsp)]), p):
                    self.rect = self.rect.move([np.sign(self.hsp), np.sign(self.vsp)])
                if pygame.sprite.collide_rect(self.rect.move([np.sign(self.hsp), 0]), p):
                    self.hsp = 0
                if pygame.sprite.collide_rect(self.rect.move([0, np.sign(self.vsp)]), p):
                    self.vsp = 0

    def meeting_platform(self, rect):
        for p in self.platforms:
            if pygame.sprite.collide_rect(rect, p):
                return True



class Ghost(Entity):
    # todo: implement
    pass
