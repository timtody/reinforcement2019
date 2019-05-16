import sys
import pygame
from collections import defaultdict
from pygame.locals import QUIT, KEYDOWN
from .game_objects import *
from .actionspace import ActionSpace
from .configs import BaseConfig
from .level import Level

class Env:
    def __init__(self, config=BaseConfig, level=Level):
        pygame.init()
        pygame.font.init()
        # config
        self.TILE_SIZE = config.TILE_SIZE
        self.SCREEN_SIZE = pygame.Rect(config.SCREEN_SIZE)
        self.action_space = ActionSpace
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE.size)
        self.timer = pygame.time.Clock()
        self.level = level
        
        # sprite groups
        self.playables = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()

        # playables
        self.ghost = Ghost([self.ghosts, self.entities], self.platforms, (self.TILE_SIZE*10, self.TILE_SIZE*10))
        self.ghost2 = Ghost([self.ghosts, self.entities], self.platforms, (self.TILE_SIZE*12, self.TILE_SIZE*12))
        self.ghost3 = Ghost([self.ghosts, self.entities], self.platforms, (self.TILE_SIZE*14, self.TILE_SIZE*14))
        self.player = PacMan([self.playables, self.entities], self.platforms, self.coins, self.ghosts, (self.TILE_SIZE*3, self.TILE_SIZE*3))

        # observations
        self.observation = defaultdict(dict)
        self.reward = defaultdict(dict)
        self.done = defaultdict(dict)
        self.info = defaultdict(dict)

        level_width = len(level.string_representation[0])*self.TILE_SIZE
        level_height = len(level.string_representation)*self.TILE_SIZE
        # build the level
        x = y = 0
        for row in self.level.string_representation:
            for col in row:
                if col == "P":
                    Wall((x, y), self.platforms)
                if col == " " and not (x, y) == self.player.rect.topleft:
                    Coin((x, y), self.coins)
                x += self.TILE_SIZE
            y += self.TILE_SIZE
            x = 0

    def render(self):
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
        self.observation["pacman"] = pygame.surfarray.array2d(self.screen).T
        self.observation["ghosts"][0] = pygame.surfarray.array2d(self.screen).T
        self.observation["ghosts"][1] = pygame.surfarray.array2d(self.screen).T
        self.observation["ghosts"][2] = pygame.surfarray.array2d(self.screen).T

        self.reward["pacman"] = self.player.reward
        self.reward["ghosts"][0] = self.ghost.reward
        self.reward["ghosts"][1] = self.ghost2.reward
        self.reward["ghosts"][2] = self.ghost3.reward

        # todo: implement done=True for the case that the player has collected all coin
        self.done = self.player.lost

        # add all information here which cannot be retrieved easily via the visual channel
        self.info["player"]["lives"] = self.player.lives

        return self.observation, self.reward, self.done, self.info
