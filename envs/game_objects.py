import pygame
import os
import numpy as np
from pygame.locals import *
from .actionspace import ActionSpace


def load_image(name, colorkey=None):
    fullname = os.path.join('resources/img', name)
    try:
        image = pygame.image.load(fullname)
    except Exception as e:
        raise e
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image.convert(), image.get_rect()

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
    join = lambda x: os.path.join("resources/img", x)
    fullnames = map(join, directions)
    images = []
    for name in fullnames:
        im = pygame.image.load(name)
        images.append(im.convert())
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
    
    def check_if_current_action_legal(self):
        """ returns true if current action is legal
        i.e. the selected action will not run is into a wall """
        if self.get_grid_entries_for_next_action() == 0:
            return True
        else:
            return False
    
    def get_grid_entries_for_next_action(self):
        """ returns 0 if current action will be valid, 1 else """
        rel_pos = self.get_relative_position()
        new_pos = self.add_tuples(rel_pos, self.action.get_dir())
        # indices have to be swapped here because of ingame x,y representation
        tile = self.grid[new_pos[1], new_pos[0]]
        return tile
    
    def get_relative_position(self):
        """ computes world coordinates to grid coordinates """
        pos = self.rect.topleft
        rel_pos = [pos[0] // 32, pos[1] // 32]
        return rel_pos
    
    def add_tuples(self, tupa, tupb):
        """ simply does a broadcast add numpy style for shitty python tuples """
        return (tupa[0] + tupb[0], tupa[1] + tupb[1])
    
    def get_id_of_next_grid_pos(self):
        """ factors in hsp and vsp to calculate the id
        of the tile which would be visited next step"""
        cur_pos = self.get_relative_position()
        next_pos = self.add_tuples([self.move_h, self.move_v], cur_pos)
        return self.grid[next_pos[1], next_pos[0]]
    
    def filter_legal_actions(self):
        if not self.check_if_current_action_legal():
            self.action = self.ActionSpace.IDLE
            self.taken_illegal_action = True
        else:
            self.taken_illegal_action = False
    
    def grid_move(self):
        collision = False
        # collision and movement
        if self.get_id_of_next_grid_pos() == 1:
            self.move_h = self.move_v = 0
            self.hsp = self.vsp = 0
            collision = True
        self.rect = self.rect.move([self.hsp, self.vsp])
        
        return collision
    
    def move(self):
        """moves and checks for collisions with wall tiles. Does not handle
        any collision with coins or other entities,


        Returns:
            bool -- true if entity is colliding with a wall this frame only
        """
        collision = False
        # horizontal collision and movement
        if self.meeting_platform(self.rect.move([self.hsp, 0])):
            while not self.meeting_platform(self.rect.move([np.sign(self.hsp), 0])):
                self.rect = self.rect.move([np.sign(self.hsp), 0])
            self.hsp = 0
            collision = True
        self.rect = self.rect.move([self.hsp, 0])

        # vertical collision and movement
        if self.meeting_platform(self.rect.move([0, self.vsp])):
            while not self.meeting_platform(self.rect.move([0, np.sign(self.vsp)])):
                self.rect = self.rect.move([0, np.sign(self.vsp)])
            self.vsp = 0
            collision = True
        self.rect = self.rect.move([0, self.vsp])

        return collision
    
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
    def __init__(self, group, platforms,
                 coins, ghosts, pos,
                 lives, coinReward, noCoinReward,
                 ghostColReward, grid):
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
        self.move_h = 0
        self.move_v = 0
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
        self.grid = grid
        self.has_collected_coin = False
        self.has_been_caught = False
        self.taken_illegal_action = False
        self.collected_all_coins = False

    def rotate(self):
        if self.action == ActionSpace.RIGHT:
            self.image = self.images[0]
        if self.action == ActionSpace.LEFT:
            self.image = self.images[2]
        if self.action == ActionSpace.UP:
            self.image = self.images[3]
        if self.action == ActionSpace.DOWN:
            self.image = self.images[1]
    
    def update(self):
        # gets called every frame by the engine
        self.filter_legal_actions()
        
        self.set_movement()
        
        # actually do movement
        self.move()
        self.rotate()

        # check for coins
        self.check_for_coins()
        
        # check for collision with ghosts
        self.check_for_ghosts()
        
        # check if all lives were lost
        self.check_for_lives()
        
        # calculate reward at the end of updateo
        self.calculate_reward()
        
    def calculate_reward(self):
        self.reward = 0
        # pacman recieves a positive reward for collecting coins
        if self.has_collected_coin:
            self.reward += self.coinReward
        else:
            self.reward += self.noCoinReward
        
        # pacman recieves a negative reward for being caught
        if self.has_been_caught:
            self.reward += self.ghostColReward
        
        # pacman gets negative reward for trying to
        # execute illegal actions 
        if self.taken_illegal_action:
            self.reward += -10
            
        if self.lost:
            self.reward -= 1000
        
        if self.collected_all_coins:
            self.reward += 1000
        
        return self.reward
    
    def check_for_coins(self):
        for c in self.coins:
            if pygame.sprite.collide_rect(self, c):
                c.kill()
                self.points += 1
                self.has_collected_coin = 1
                return
        self.has_collected_coin = 0
    
    def check_for_ghosts(self):
        for g in self.ghosts:
            if pygame.sprite.collide_rect(self, g):
                self.lives -= 1
                self.has_been_caught = True
                g.caught_pacman = True
                self.rect.topleft = self.start
                for g in self.ghosts:
                    g.rect.topleft = g.start
                return
            else:
                g.caught_pacman = False
        self.has_been_caught = False
    
    def check_for_lives(self):
        # check for lives
        if self.lives == 0:
            self.lost = True
    
    def set_movement(self):
        # set the movement parameters of the agent
        if self.action == self.ActionSpace.IDLE:
            # placeholder
            pass
        elif self.action == self.ActionSpace.UP:
            self.move_h = 0
            self.move_v = -1
        elif self.action == self.ActionSpace.DOWN:
            self.move_h = 0
            self.move_v = 1
        elif self.action == self.ActionSpace.LEFT:
            self.move_h = -1
            self.move_v = 0
        elif self.action == self.ActionSpace.RIGHT:
            self.move_h = 1
            self.move_v = 0

        self.hsp = self.move_h*self.movespeed
        self.vsp = self.move_v*self.movespeed


class Ghost(Entity):
    def __init__(self, group, 
                 platforms, playables, 
                 pos, movespeed,
                 grid):
        super().__init__(group)
        self.image, self.rect = load_image('ghost.png')
        self.start = pos
        self.rect.topleft = pos
        self.movespeed = movespeed
        self.hsp = 0
        self.vsp = 0
        self.move_h = 0
        self.move_v = 0
        self.platforms = platforms
        self.ActionSpace = ActionSpace
        self.action = ActionSpace.IDLE
        self.pacman = playables
        self.reward = 0
        self.is_collided = False
        self.caught_pacman = False
        self.grid = grid
        self.taken_illegal_action = False
        
    def distance_to_pacman(self):
        pacman = self.pacman.sprites()[0]
        ghost_pos = np.array(self.rect.topleft)
        pacman_pos = np.array(pacman.rect.topleft)
        dist = np.linalg.norm(ghost_pos - pacman_pos)
        
        return dist
    
    def calculate_reward(self):
        normalized_distance = self.distance_to_pacman() / 100
        self.reward = -normalized_distance
        if self.taken_illegal_action: 
            self.reward -= 10
        if self.caught_pacman: 
            self.reward += 100

    def update(self):
        self.filter_legal_actions()
        self.set_movement()
        # horizontal collision and movement
        # check if a collision has happened

        self.grid_move()
        self.calculate_reward()
        #print(f"ghost reward is: {self.reward}")
    
    def set_movement(self):
        if self.action == self.ActionSpace.IDLE:
            self.move_h = self.move_h
            self.move_v = self.move_v
        elif self.action == self.ActionSpace.UP:
            self.move_h = 0
            self.move_v = -1
        elif self.action == self.ActionSpace.DOWN:
            self.move_h = 0
            self.move_v = 1
        elif self.action == self.ActionSpace.LEFT:
            self.move_h = -1
            self.move_v = 0
        elif self.action == self.ActionSpace.RIGHT:
            self.move_h = 1
            self.move_v = 0
        
        self.hsp = self.move_h*self.movespeed
        self.vsp = self.move_v*self.movespeed
