import sys
import pygame
from enum import Enum, auto
from level import level
from collections import defaultdict
from objects import *
from pygame.locals import QUIT, KEYDOWN
from matplotlib import pyplot as plt

class ActionSpace(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    IDLE = auto()

class Env:
    tile_size = 64
    game_speed = 60
    width = 1280
    height = 720
    size = width, height
    SCREEN_SIZE = pygame.Rect((0, 0, 20*32, 18*32))
    TILE_SIZE = 32

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.action_space = ActionSpace
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.screen = pygame.display.set_mode(GLOBALS.SCREEN_SIZE.size)
        self.timer = pygame.time.Clock()

        self.playables = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()

        self.ghost = Ghost([self.ghosts, self.entities], self.platforms, (GLOBALS.TILE_SIZE*10, GLOBALS.TILE_SIZE*10))
        self.ghost2 = Ghost([self.ghosts, self.entities], self.platforms, (GLOBALS.TILE_SIZE*12, GLOBALS.TILE_SIZE*12))
        self.ghost3 = Ghost([self.ghosts, self.entities], self.platforms, (GLOBALS.TILE_SIZE*14, GLOBALS.TILE_SIZE*14))

        self.player = PacMan([self.playables, self.entities], self.platforms, self.coins, self.ghosts, (GLOBALS.TILE_SIZE*3, GLOBALS.TILE_SIZE*3))


        level_width = len(level[0])*GLOBALS.TILE_SIZE
        level_height = len(level)*GLOBALS.TILE_SIZE
        # build the level
        x = y = 0
        for row in level:
            for col in row:
                if col == "P":
                    Wall((x, y), self.platforms)
                if col == " " and not (x, y) == self.player.rect.topleft:
                    Coin((x, y), self.coins)
                x += GLOBALS.TILE_SIZE
            y += GLOBALS.TILE_SIZE
            x = 0

    def render(self):
        observation = defaultdict(dict)
        reward = defaultdict(dict)
        done = defaultdict(dict)
        info = defaultdict(dict)

        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()

        # calculate pacmans points and lives
        surface_points = self.myfont.render(f'points: {self.player.points}', 
        False, (0, 0, 0))

        surface_lives = self.myfont.render(f'lives: {self.player.lives}', 
        False, (0, 0, 0))


        # entities.update()
        self.entities.update()
       
        #platforms.update()
        self.screen.fill((0, 0, 0))
        self.entities.draw(self.screen)
        self.coins.draw(self.screen)
        self.entities.draw(self.screen)
        self.platforms.draw(self.screen)

        # show points and lives
        self.screen.blit(surface_points,(0,17*32-10))
        self.screen.blit(surface_lives,(256,17*32-10))

        pygame.display.update()

        # setup return values for render
        observation["pacman"] = pygame.surfarray.array2d(self.screen).T
        observation["ghosts"][0] = pygame.surfarray.array2d(self.screen).T
        observation["ghosts"][1] = pygame.surfarray.array2d(self.screen).T
        observation["ghosts"][2] = pygame.surfarray.array2d(self.screen).T

        reward["pacman"] = self.player.reward
        reward["ghosts"][0] = self.ghost.reward
        reward["ghosts"][1] = self.ghost2.reward
        reward["ghosts"][2] = self.ghost3.reward

        # todo: implement done=True for the case that the player has collected all coin
        done = self.player.lost

        # add all information here which cannot be retrieved easily via the visual channel
        info["player"]["lives"] = self.player.lives

        return observation, reward, done, info


if __name__ == "__main__":
    env = Env()
    while 1:

        obs, reward, done, info = env.render()
        env.timer.tick(60)
        plt.imshow(obs["pacman"])
        plt.show()

        # pacman und ghosts have  ActionSpace = IDLE, UP, DOWN, LEFT, RIGHT
        env.player.action = env.player.ActionSpace.DOWN
        env.ghost.action = env.ghost.ActionSpace.DOWN
        env.ghost2.action = env.ghost2.ActionSpace.UP
        env.ghost3.action = env.ghost3.ActionSpace.IDLE