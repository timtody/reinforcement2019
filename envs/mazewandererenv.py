import sys
import pygame
from collections import defaultdict
from pygame.locals import QUIT, KEYDOWN
from .game_objects import *
from .actionspace import ActionSpace
from .configs import BaseConfig
from .level import Level
from PIL import Image

class Env:
    def __init__(self, config=BaseConfig, levelName='Full'):
        pygame.init()
        pygame.font.init()
        # config
        self.TILE_SIZE = config.TILE_SIZE
        self.SCREEN_SIZE = pygame.Rect(config.SCREEN_SIZE)
        self.action_space = ActionSpace
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE.size)
        self.timer = pygame.time.Clock()
        self.level = Level(levelName)
        
        # sprite groups
        self.playables = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()

        # observations
        self.observation = defaultdict(dict)
        self.reward = defaultdict(dict)
        self.done = defaultdict(dict)
        self.info = defaultdict(dict)

        # setup the scene
        self.init_playables()
        self.setup_level()

    def setup_level(self, walls=True):
        level_width = len(self.level.string_representation[0])*self.TILE_SIZE
        level_height = len(self.level.string_representation)*self.TILE_SIZE
        # build the level
        x = y = 0
        for row in self.level.string_representation:
            for col in row:
                if col == "P" and not (x, y) == self.player.rect.topleft and walls:
                    Wall((x, y), self.platforms)
                if col == " " and not (x, y) == self.player.rect.topleft:
                    Coin((x, y), self.coins)
                x += self.TILE_SIZE
            y += self.TILE_SIZE
            x = 0

    def init_playables(self):
        # playables
        self.ghost = Ghost(
            [self.ghosts, self.entities], self.platforms, 
            (self.TILE_SIZE*9, self.TILE_SIZE*9))
        self.ghost2 = Ghost(
            [self.ghosts, self.entities], self.platforms, 
            (self.TILE_SIZE*9, self.TILE_SIZE*9))
        self.ghost3 = Ghost(
            [self.ghosts, self.entities], self.platforms, 
            (self.TILE_SIZE*0, self.TILE_SIZE*9))
        self.player = PacMan(
            [self.playables, self.entities], self.platforms, self.coins, self.ghosts, 
            (self.TILE_SIZE*3, self.TILE_SIZE*2))
    
    def reset(self):
        # delete all current coins and players
        for sprite in self.entities.sprites():
            sprite.kill()
        for coin in self.coins.sprites():
            coin.kill()

        self.init_playables()
        self.setup_level(walls=False)

    def render(self, update_display=False):
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
        # calculate pacmans points and lives
        surface_points = self.myfont.render(f'points: {self.player.points}', 
        False, (0, 0, 0))
        surface_lives = self.myfont.render(f'lives: {self.player.lives}', 
        False, (0, 0, 0))

        self.entities.update()
        self.screen.fill((0, 0, 0))
        self.entities.draw(self.screen)
        self.coins.draw(self.screen)
        self.entities.draw(self.screen)
        self.platforms.draw(self.screen)

        # show points and lives
        self.screen.blit(surface_points,(0,17*32-10))
        self.screen.blit(surface_lives,(256,17*32-10))
        
        if update_display: pygame.display.update()

        # setup return values for render
        screenRaw = pygame.surfarray.array2d(self.screen).T
        screen = np.array(Image.fromarray(screenRaw).resize((80,72),Image.NEAREST))
        screen = screen/np.max(screen)
        self.observation["pacman"] = screen
        self.observation["ghosts"][0] = screen
        self.observation["ghosts"][1] = screen
        self.observation["ghosts"][2] = screen
        # compute the distance to pacman per ghost
        self.info["ghosts"][0] = np.sqrt(np.square(self.ghost.rect.topleft[0]-self.player.rect.topleft[0]) +
                                        np.square(self.ghost.rect.topleft[1]-self.player.rect.topleft[1]))
        self.info["ghosts"][1] = np.sqrt(np.square(self.ghost2.rect.topleft[0]-self.player.rect.topleft[0]) +
                                        np.square(self.ghost2.rect.topleft[1]-self.player.rect.topleft[1]))
        self.info["ghosts"][2] = np.sqrt(np.square(self.ghost3.rect.topleft[0]-self.player.rect.topleft[0]) +
                                        np.square(self.ghost3.rect.topleft[1]-self.player.rect.topleft[1]))
        # get the rewards per entity
        self.reward["pacman"] = self.player.reward
        self.reward["ghosts"][0] = self.ghost.reward
        self.reward["ghosts"][1] = self.ghost2.reward
        self.reward["ghosts"][2] = self.ghost3.reward
        # todo: implement done=True for the case that the player has collected all coin
        self.done = self.player.lost or len(self.coins) == 0
        # add all information here which cannot be retrieved easily via the visual channel
        self.info["player"]["lives"] = self.player.lives

        # implement replay buffer
        # batch_size x screen_h x screen_w

        return self.observation, self.reward, self.done, self.info, screenRaw
