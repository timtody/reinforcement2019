import sys
from level import level
from objects import *
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(GLOBALS.SCREEN_SIZE.size)
    timer = pygame.time.Clock()
    platforms = pygame.sprite.Group()
    player = PacMan(platforms, (GLOBALS.TILE_SIZE*3, GLOBALS.TILE_SIZE*3))
    level_width = len(level[0])*GLOBALS.TILE_SIZE
    level_height = len(level)*GLOBALS.TILE_SIZE
    entities = CameraAwareLayeredUpdates(player, pygame.Rect(0, 0, level_width, level_height))

    # build the level
    x = y = 0
    for row in level:
        for col in row:
            if col == "P":
                Wall((x, y), platforms, entities)
            if col == "E":
                Wall((x, y), platforms, entities)
            x += GLOBALS.TILE_SIZE
        y += GLOBALS.TILE_SIZE
        x = 0

    while 1:
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                pass

        entities.update()

        screen.fill((0, 0, 0))
        entities.draw(screen)
        screen.blit(player.image, player.rect)
        pygame.display.update()
        timer.tick(60)