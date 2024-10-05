import pygame as pg
from random import choice, randint

pg.init()

class Game:
    SHAPES = [
        [[1, 1, 1, 1]],
        [[1, 1], [1, 1]],
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1, 1], [1, 1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1, 1], [0, 0, 1]]
    ]
    WIDTH = 20
    HEIGHT = 25
    COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    CELL_SIZE = 30
    DOWN_EVENT = pg.USEREVENT
    LEFT_EVENT = pg.USEREVENT + 1
    RIGHT_EVENT = pg.USEREVENT + 2
    LEFT_KEYS = [pg.K_LEFT, pg.K_a]
    RIGHT_KEYS = [pg.K_RIGHT, pg.K_d]
    DOWN_KEYS = [pg.K_DOWN, pg.K_s]
    UP_KEYS = [pg.K_UP, pg.K_w]
    

    def __init__(self):
        self.screen = pg.display.set_mode((self.WIDTH * 30, self.HEIGHT * 30))
        pg.display.set_caption('Tetris')
        self.clock = pg.time.Clock()
        self.grid = [[0 for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.shape = self.new_shape()
        self.pos = [0, 0]
        self.n_pos = [0, 0]
        self.dir = [0, 0]
        self.score = 0
        self.game_over = False
        self.current_color = choice(self.COLORS)
        self.current_color = (255 ,255, 255)
        self.fall_speed = 500

    
    def new_shape(self):
        shape = choice(self.SHAPES)
        self.current_color = choice(self.COLORS)
        self.current_color = (255 ,255, 255)
        self.pos = [0, randint(0, self.WIDTH - len(shape[0]))]
        self.n_pos = [0, 0]
        self.dir = [0, 0]
        return shape
    
    def schedule_move(self, direction):
        self.n_pos = [self.pos[0] + direction[0], self.pos[1] + direction[1]]
        self.dir = direction

    
    def run(self):
        pg.time.set_timer(self.DOWN_EVENT, self.fall_speed)
        while not self.game_over:
            self.clock.tick(120)
            self.events()
            self.update()
            self.draw()
        print(f'Game over! Score: {self.score}')

    def check_game_over(self):
        for i, cell in enumerate(self.grid[0]):
            if cell:
                self.game_over = True
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game_over = True
            if event.type == pg.KEYDOWN:
                if event.key in self.LEFT_KEYS:
                    pg.time.set_timer(self.LEFT_EVENT, 50)
                if event.key in self.RIGHT_KEYS:
                    pg.time.set_timer(self.RIGHT_EVENT, 50)
                if event.key in self.DOWN_KEYS:
                    pg.time.set_timer(self.DOWN_EVENT, 50)
                if event.key in self.UP_KEYS:
                    self.shape = self.rotate(self.shape)

            if event.type == pg.KEYUP:
                if event.key in self.DOWN_KEYS:
                    pg.time.set_timer(self.DOWN_EVENT, self.fall_speed)
                if event.key in self.RIGHT_KEYS or event.key in self.LEFT_KEYS:
                    pg.time.set_timer(self.LEFT_EVENT, 50000)
                    pg.time.set_timer(self.RIGHT_EVENT, 50000)

            if event.type == self.DOWN_EVENT:
                self.schedule_move([1, 0])
            if event.type == self.LEFT_EVENT:
                self.schedule_move([0, -1])
            if event.type == self.RIGHT_EVENT:
                self.schedule_move([0, 1])

    def update(self):
        if not self.resolve_collisions():
            self.move()
            self.check_game_over()
            self.clear_rows()

    def move(self):
        self.pos = self.n_pos

    def draw(self):
        self.screen.fill((0, 0, 0))

        #self.draw_grid_lines()
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell:
                    pg.draw.rect(self.screen, cell, (j * self.CELL_SIZE, i * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE))
        self.draw_current_shape()
        self.draw_ghost()
        pg.display.flip()

    def draw_current_shape(self):
        self.draw_shape(self.shape, self.pos[1]*self.CELL_SIZE, self.pos[0]*self.CELL_SIZE, self.current_color)

    def draw_shape(self, shape, x, y, color):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    pg.draw.rect(self.screen, color, (x + j * self.CELL_SIZE, y + i * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE))

    def draw_grid_lines(self):
        for i in range(0, self.WIDTH * self.CELL_SIZE, self.CELL_SIZE):
            pg.draw.line(self.screen, (255, 255, 255), (i, 0), (i, self.HEIGHT * self.CELL_SIZE))
        for i in range(0, self.HEIGHT * self.CELL_SIZE, self.CELL_SIZE):
            pg.draw.line(self.screen, (255, 255, 255), (0, i), (self.WIDTH * self.CELL_SIZE, i))

    def draw_ghost(self):
        x, y = self.get_ghost()
        self.draw_shape(self.shape, x*self.CELL_SIZE, y*self.CELL_SIZE, (100, 100, 100))

    def rotate(self, shape):
        return list(zip(*shape[::-1]))
    
    def ghost_collisions(self, y):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell and self._in_bounds(self.pos[1] + j, y + i) and self.grid[y + i][self.pos[1] + j]:
                    return True
        return y + len(self.shape) > self.HEIGHT
    
    def resolve_collisions(self):
        x = self.n_pos[1]
        y = self.n_pos[0]
        if self.dir[1]:
            side_length = len(self.shape[0])
            for row in self.shape:
                if len(row) > side_length:
                    side_length = len(row)
            if x < 0 or x + side_length > self.WIDTH:
                return True
            
            for i, row in enumerate(self.shape):
                for j, cell in enumerate(row):
                    if cell and self._in_bounds(x + j, y + i) and self.grid[y + i][x + j]:
                        return True

        if self.dir[0]:
            if y + len(self.shape) > self.HEIGHT:
                self.next_shape()
                return True
            
            for i, row in enumerate(self.shape):
                for j, cell in enumerate(row):
                    if cell and self._in_bounds(x + j, y + i) and self.grid[y + i][x + j]:
                        self.next_shape()
                        return True
        return False
            
    def next_shape(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                new_x = self.pos[1] + j
                new_y = self.pos[0] + i
                if cell and self._in_bounds(new_x, new_y):
                    self.grid[new_y][new_x] = self.current_color
        self.shape = self.new_shape()
        
    
    def _in_bounds(self, x, y):
        return not (x < 0 or x >= self.WIDTH or y < 0 or y >= self.HEIGHT)

    def clear_rows(self):
        for i, row in enumerate(self.grid):
            if all(row):
                self.score += 1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(self.WIDTH)])
                self.fall_speed = max(100, self.fall_speed - 25)
                pg.time.set_timer(self.DOWN_EVENT, self.fall_speed)

    def get_ghost(self):
        y = self.pos[0]
        while not self.ghost_collisions(y):
            y += 1
        return (self.pos[1], y - 1)

if __name__ == '__main__':
    Game().run()