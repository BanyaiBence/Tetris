import pygame as pg
from random import choice
from colors import Colors
import itertools

class Game:
    WIDTH = 600
    HEIGHT = 960
    SQUARE_SIZE = 40
    SHAPES = [[[1, 1, 1, 1]],
              [[1, 1], [1, 1]],
              [[1, 1, 0], [0, 1, 1]],
              [[0, 1, 1], [1, 1, 0]],
              [[1, 1, 1], [0, 1, 0]],
              [[1, 1, 1], [1, 0, 0]],
              [[1, 1, 1], [0, 0, 1]]
              ]
    FALL_EVENT = pg.USEREVENT
    LEFT_EVENT = pg.USEREVENT + 1
    RIGHT_EVENT = pg.USEREVENT + 2
    DOWN_EVENT = pg.USEREVENT + 3
    def __init__(self):
        pg.init()
        self.window = pg.display.set_mode((Game.WIDTH, Game.HEIGHT))
        pg.display.set_caption('Tetris')
        self.clock = pg.time.Clock()

        self.matrix = [[0 for i in range(15)] for j in range(24)]
        self.reset_shape()

    def new_shape(self):
        shape = choice(self.SHAPES)
        return shape
    
    
    def draw_shape(self):
        S = Game.SQUARE_SIZE
        P = self.shape_pos
        for i, row in enumerate(self.shape):
            for j, col in enumerate(row):
                if col == 0:
                    continue
                pg.draw.rect(self.window, self.shape_color,
                    ((P[1]+j)*S, (P[0]+i)*S, S, S))   

    def draw(self):
        self.window.fill(Colors.BLACK)
        S = Game.SQUARE_SIZE
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if col == 0:
                    continue
                pg.draw.rect(self.window, col,
                    (j*S, i*S, S, S))

        self.draw_shape()
        pg.display.flip()

    def schedule_move(self, direction):
        P = self.shape_pos
        D = direction
        self.next_pos = [P[0] + D[0], P[1] + D[1]]

    def move(self):
        self.shape_pos = self.next_pos


    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type in [Game.FALL_EVENT, Game.DOWN_EVENT]:
                self.schedule_move([1, 0])
            if event.type == Game.LEFT_EVENT:
                self.schedule_move([0, -1])
            if event.type == Game.RIGHT_EVENT:
                self.schedule_move([0, 1])

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_a:
                    pg.time.set_timer(Game.LEFT_EVENT, 100)
                if event.key == pg.K_d:
                    pg.time.set_timer(Game.RIGHT_EVENT, 100)
                if event.key == pg.K_s:
                    pg.time.set_timer(Game.DOWN_EVENT, 100)
                if event.key == pg.K_w:
                    self.rotate_shape()

            if event.type == pg.KEYUP:
                if event.key == pg.K_a:
                    pg.time.set_timer(Game.LEFT_EVENT, 100000)
                if event.key == pg.K_d:
                    pg.time.set_timer(Game.RIGHT_EVENT, 100000)
                if event.key == pg.K_s:
                    pg.time.set_timer(Game.DOWN_EVENT, 100000)

    def run(self):
        pg.time.set_timer(Game.FALL_EVENT, 500)
        while True:
            self.clock.tick(60)
            self.events()
            if not self.collision(self.shape):
                self.move()
            self.clear_rows()
            self.draw()

    def in_bounds(self, pos):
        x = pos[1]
        y = pos[0]
        if x < 0 or x >= 15:
            return False
        if y < 0 or y >= 24:
            return False
        return True


    def collision(self, shape=None):
        x = self.shape_pos[1]
        y = self.shape_pos[0]
        nx = self.next_pos[1]
        ny = self.next_pos[0]
        d = (ny - y, nx - x)

        if d[0]:
            if y + len(shape) >= 24:
                self.save_shape()
                return True

            for i, row in enumerate(shape):
                for j, col in enumerate(row):
                    if col and self.in_bounds((ny+i, x+j)) and self.matrix[ny+i][x+j]:
                        self.save_shape()
                        return True

        if d[1]:
            if nx < 0 or nx + len(shape[0]) >= 16:
                return True

            for i, row in enumerate(shape):
                for j, col in enumerate(row):
                    if col and self.in_bounds((y+i, nx+j)) and self.matrix[y+i][nx+j]:
                        return True

        
    def save_shape(self):
        x = self.shape_pos[1]
        y = self.shape_pos[0]
        for i, row in enumerate(self.shape):
            for j, col in enumerate(row):
                if col:
                    self.matrix[y+i][x+j] = self.shape_color
        self.reset_shape()

    def reset_shape(self):
        self.shape = self.new_shape()
        self.shape_color = Colors.random_color()
        self.shape_pos = [0, 5]
        self.next_pos = [0, 5]

    def move_shape(self, dir):
        new_pos = [self.shape_pos[0] + dir[0], self.shape_pos[1] + dir[1]]
        if new_pos[1] < 0:
            return
        right = self.shape.right
        if new_pos[1] + right > 15:
            return
        

        if self.check_collision(new_pos):
            return

        self.shape_pos[0] += dir[0]
        self.shape_pos[1] += dir[1]

    def rotate_shape(self):
        new_shape = list(zip(*self.shape[::-1]))
        if not self.collision(new_shape):
            self.shape = new_shape 
    
    def clear_rows(self):
        for i, row in enumerate(self.matrix):
            if all(row):
                self.matrix.pop(i)
                self.matrix.insert(0, [0 for i in range(15)])


if __name__ == '__main__':
    game = Game()
    game.run()