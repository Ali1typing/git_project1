import pygame
import pytmx


WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 672, 608
FPS = 15
MAPS_DIR = "maps"
TILE_SIZE = 32
ENEMY_EVENT_TYPE = 10
TIME_TO_SPAWN = 5000


class Labyrinth:

    def __init__(self, filename, free_tiles, finish_tile):
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def find_path_step(self, start, target):
        INF = 1000
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 < next_y < self.height and \
                        self.is_free((next_x, next_y)) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Enemy:

    def __init__(self, position):
        self.x, self.y = position
        self.delay = 100
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, (255, 0, 0), center, TILE_SIZE // 2)


class Hero:

    def __init__(self, position):
        self.x, self.y = position

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, (255, 255, 255), center, TILE_SIZE // 2)


class Game:

    def __init__(self, labyrinth, hero, enemy):
        self.labyrinth = labyrinth
        self.hero = hero
        self.enemy_1 = enemy
        self.enemy_2 = Enemy((8, 17))
        self.enemy_3 = Enemy((11, 17))

    def render(self, screen):
        self.labyrinth.render(screen)
        self.hero.render(screen)
        self.enemy_1.render(screen)
        self.enemy_2.render(screen)
        self.enemy_3.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.hero.set_position((next_x, next_y))

    def stop_game(self):
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            return True

    def return_game(self):
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            return True

    def move_enemy_1(self):
        next_position = self.labyrinth.find_path_step(self.enemy_1.get_position(), self.hero.get_position())
        self.enemy_1.set_position(next_position)

    def move_enemy_2(self):
        next_position = self.labyrinth.find_path_step(self.enemy_2.get_position(), self.hero.get_position())
        self.enemy_2.set_position(next_position)

    def move_enemy_3(self):
        next_position = self.labyrinth.find_path_step(self.enemy_3.get_position(), self.hero.get_position())
        self.enemy_3.set_position(next_position)


    def check_win(self):
        return self.labyrinth.get_tile_id(self.hero.get_position()) == self.labyrinth.finish_tile

    def check_lose(self):
        if self.hero.get_position() == self.enemy_1.get_position():
            return self.hero.get_position() == self.enemy_1.get_position()
        if self.hero.get_position() == self.enemy_2.get_position():
            return self.hero.get_position() == self.enemy_2.get_position()
        if self.hero.get_position() == self.enemy_3.get_position():
            return self.hero.get_position() == self.enemy_3.get_position()


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, 1, (50, 70, 0))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10,
                                              text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def main():
    pygame.init()
    pygame.display.set_caption('Проект')
    screen = pygame.display.set_mode(WINDOW_SIZE)

    hero = Hero((7, 13))
    labyrinth = Labyrinth("карта1.tmx", [1, 2], 2)
    enemy = Enemy((13, 1))
    game = Game(labyrinth, hero, enemy)

    clock = pygame.time.Clock()
    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == ENEMY_EVENT_TYPE and not game_over:
                game.move_enemy_1()
            if event.type == ENEMY_EVENT_TYPE and not game_over\
                    and TIME_TO_SPAWN < pygame.time.get_ticks():
                game.move_enemy_2()
            if event.type == ENEMY_EVENT_TYPE and not game_over\
                    and TIME_TO_SPAWN * 2 < pygame.time.get_ticks():
                game.move_enemy_3()
        if not game_over:
            game.update_hero()
        screen.fill((0, 0, 0))
        game.render(screen)
        if game.stop_game():
            game_over = True
        if game_over and game.return_game():
            game_over = False
        if game.check_win():
            game_over = True
            show_message(screen, 'You won!')
        if game.check_lose():
            game_over = True
            show_message(screen, 'You lost!')

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()




if __name__ == '__main__':
    main()