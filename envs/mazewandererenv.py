import sys
import pygame
from collections import defaultdict
from pygame.locals import QUIT, KEYDOWN
from .game_objects import *
from .actionspace import ActionSpace
from .configs import BaseConfig
from .level import Level
from PIL import Image
from random import randint

class Env:
    def __init__(self, expConfig, 
                 config=BaseConfig, 
                 levelName='Full', 
                 manual_test=False):
        
        flags = DOUBLEBUF
        pygame.init()
        pygame.font.init()
        pygame.event.set_allowed([QUIT])
        # config
        self.expConfig = expConfig
        self.TILE_SIZE = config.TILE_SIZE
        
        self.action_space = ActionSpace
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.timer = pygame.time.Clock()

        # list of active entities
        self.ghost_list = []

        # setup level and screen size
        self.level = Level(levelName)
        self.screen_y = len(self.level.string_representation)*self.TILE_SIZE
        self.screen_x = len(self.level.string_representation[0])*self.TILE_SIZE
        self.screen_y_comp = self.screen_y // 8
        self.screen_x_comp = self.screen_x // 8
        self.expConfig.screen_x = self.screen_x
        self.expConfig.screen_y = self.screen_y
        self.expConfig.screen_x_comp = self.screen_x_comp
        self.expConfig.screen_y_comp = self.screen_y_comp
        print(f"screen dimensions: {self.screen_x}, {self.screen_y}\n")

        self.SCREEN_SIZE = pygame.Rect(0, 0, self.screen_x, self.screen_y)
        self.screen = pygame.display.set_mode(
            (self.SCREEN_SIZE.size), 
            flags)
        
        level = self.level.string_representation
        self.grid_level = np.empty((len(level), len(level[0])), dtype=np.int)

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

        # starting positions for entities
        self.start_positions = dict()

        # setup the scene
        self.setup_level()
        self.init_playables()

        # set renderin parameters
        self.screen.set_alpha(None)

        # max achievable score
        self.total_coins = len(self.coins)
        
        # manual testing
        self.manual = manual_test
        self.clock = pygame.time.Clock()





    def setup_level(self, walls=True):
        level_width = len(
            self.level.string_representation[0])*self.TILE_SIZE
        level_height = len(
            self.level.string_representation)*self.TILE_SIZE
        # build the level
        self.numCoins = 0
        x = y = 0
        for i, row in enumerate(self.level.string_representation):
            for j, col in enumerate(row):
                # 0 means no wall tile is present
                self.grid_level[i, j] = 1 if col == "P" else 0
                if col == "P" and walls:
                    # 1 for wall tile
                    Wall((x, y), self.platforms)
                if col == " ":
                    Coin((x, y), self.coins)
                    self.numCoins += 1
                if col == "T":
                    Coin((x, y), self.coins)
                    self.numCoins += 1
                    self.expConfig.pacman_start_poses.append((j, i))
                    self.start_positions["player"] = [j, i]
                if col in ["A", "B", "C"]:
                    self.start_positions[col] = [j, i]
                x += self.TILE_SIZE
            y += self.TILE_SIZE
            x = 0

    def init_playables(self):
        # playables
        if "A" in self.start_positions:
            self.ghost = Ghost(
                [self.ghosts, self.entities], self.platforms, self.playables,
                (self.TILE_SIZE*self.start_positions["A"][0], self.TILE_SIZE*self.start_positions["A"][1]),
                self.expConfig.ghost_speed,
                self.grid_level)
            self.ghost_list.append("ghost")
        else:
            self.ghost = Ghost(
                [self.ghosts, self.entities], self.platforms, self.playables,
                (0, 0),
                self.expConfig.ghost_speed,
                self.grid_level)
            self.ghost_list.append("ghost")
        if "B" in self.start_positions:
            self.ghost2 = Ghost(
                [self.ghosts, self.entities], self.platforms, self.playables,
                (self.TILE_SIZE*1, self.TILE_SIZE*1),
                self.expConfig.ghost_speed,
                self.grid_level)

            self.ghost_list.append("ghost2")

        if "C" in self.start_positions:
            self.ghost3 = Ghost(
                [self.ghosts, self.entities], self.platforms, self.playables,
                (self.TILE_SIZE*1, self.TILE_SIZE*1),
                self.expConfig.ghost_speed,
                self.grid_level)
            self.ghost_list.append("ghost3")
        # Random Start Position
        numPoses = len(self.expConfig.pacman_start_poses)
        pacmanPos = self.expConfig.pacman_start_poses[randint(0,numPoses-1)]
        self.player = PacMan(
            [self.playables, self.entities], self.platforms, self.coins, self.ghosts,
            (self.TILE_SIZE*pacmanPos[0], self.TILE_SIZE*pacmanPos[1]),
            self.expConfig.pacman_lives,
            self.expConfig.pacman_reward_coin,
            self.expConfig.pacman_reward_no_coin,
            self.expConfig.pacman_reward_ghost,
            self.grid_level
        )
        self.player.movespeed = self.expConfig.pacman_movespeed

    def reset(self):
        # delete all current coins and players
        for sprite in self.entities.sprites():
            sprite.kill()
        for coin in self.coins.sprites():
            coin.kill()

        self.init_playables()
        self.setup_level(walls=False)

    def set_rewards(self):
        # compute the distance to pacman per ghost
        # todo: implement abstract reward calculation for all entities
        self.player.calculate_reward()
        self.ghost.calculate_reward()
        self.ghost2.calculate_reward()
        self.ghost3.calculate_reward()

    def get_screen(self, recording):
        # setup return values for render
        screenRaw = pygame.surfarray.array2d(self.screen).T
        if recording:
            pixels = pygame.surfarray.array3d((self.screen)).transpose((1,0,2))
        else:
            pixels = None
        screen = np.array(Image.fromarray(screenRaw).resize(
            (self.screen_x//8,self.screen_y//8), Image.NEAREST))
        screen = screen/16449355#np.max(screen)
        return screen, pixels

    def render_text(self):
        # calculate pacmans points and lives
        surface_points = self.myfont.render(f'points: {self.player.points}',
        False, (0, 0, 0))
        surface_lives = self.myfont.render(f'lives: {self.player.lives}',
        False, (0, 0, 0))
        # show points and lives
        self.screen.blit(surface_points,(0,17*self.TILE_SIZE-10))
        self.screen.blit(surface_lives,(256,17*self.TILE_SIZE-10))

    def draw_entities(self):
        self.entities.update()
        self.screen.fill((0, 0, 0))
        self.coins.draw(self.screen)
        self.entities.draw(self.screen)
        self.platforms.draw(self.screen)

    def configure_outputs(self, screen):
        # here the output dict is filled with relevant values
        if len(self.coins) == 0:
            self.player.collected_all_coins = True
            
        self.observation["pacman"] = screen
        self.observation["ghosts"][0] = screen
        self.observation["ghosts"][1] = screen
        self.observation["ghosts"][2] = screen
        self.info["ghost"][0] = self.ghost.reward if "ghost" in self.ghost_list else None
        self.info["ghost"][1] = self.ghost.reward if "ghost2" in self.ghost_list else None
        self.info["ghost"][2] = self.ghost.reward if "ghost3" in self.ghost_list else None
        self.reward["pacman"] = self.player.reward
        self.reward["ghosts"][0] = self.ghost.reward if "ghost" in self.ghost_list else None
        self.reward["ghosts"][1] = self.ghost2.reward if "ghost2" in self.ghost_list else None
        self.reward["ghosts"][2] = self.ghost3.reward if "ghost3" in self.ghost_list else None
        self.done = self.player.lost or len(self.coins) == 0
        # add all information here which cannot be retrieved easily via the visual channel
        self.info["player"]["lives"] = self.player.lives
        # calculate score
        score = self.total_coins - len(self.coins)
        self.info["player"]["score"] = score
    
    def manual_control(self):
        pressed = pygame.key.get_pressed()
        self.ghost.action = self.key_to_actionspace(pressed)
    
    def key_to_actionspace(self, pressed):
        if pressed[pygame.K_w]:
            return self.player.ActionSpace(0)
        elif pressed[pygame.K_s]:
            return self.player.ActionSpace(1)
        elif pressed[pygame.K_a]:
            return self.player.ActionSpace(2)
        elif pressed[pygame.K_d]:
            return self.player.ActionSpace(3)
        else:
            return self.player.ActionSpace(4)

    def render(self, update_display=False, render_text=False, recording=False):
        if self.manual:
            self.manual_control()
            self.clock.tick(12)
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
        if render_text: self.render_text()
        if update_display: pygame.display.update()
        #self.set_rewards()
        screen, pixels = self.get_screen(recording)
        self.configure_outputs(screen)
        self.draw_entities()

        return self.observation, self.reward, self.done, self.info, pixels

    def writeScreen(self, filePath):
        pygame.image.save(self.screen, filePath)
