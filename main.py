import pygame as pg
from random import choice
import colors
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
    def __init__(self):
        pg.init()
        self.window = pg.display.set_mode((Game.WIDTH, Game.HEIGHT))
        pg.display.set_caption('Tetris')
        self.clock = pg.time.Clock()

        self.matrix = [[0 for i in range(15)] for j in range(24)]
        self.shape = self.new_shape()

    def new_shape(self):
        shape = choice(self.SHAPES)
        return shape
    
    
    def draw(self):
        self.window.fill(colors.BLACK)

        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if col == 0:
                    continue
                pg.draw.rect(self.window, col,
                    (
                    j*Game.SQUARE_SIZE,
                    i*Game.SQUARE_SIZE,
                    Game.SQUARE_SIZE, 
                    Game.SQUARE_SIZE
                    ))

        for i , row in enumerate(self.shape.matrix):
            for j, col in enumerate(row):
                if col == 0:
                    continue
                pg.draw.rect(self.window, self.shape.color,
                    (
                    (self.shape_pos[1]+j)*Game.SQUARE_SIZE,
                    (self.shape_pos[0]+i)*Game.SQUARE_SIZE,
                    Game.SQUARE_SIZE, 
                    Game.SQUARE_SIZE
                    )
                    )
        pg.display.flip()

    def run(self):
        pg.time.set_timer(pg.USEREVENT, 800)
        pg.time.set_timer(pg.USEREVENT+1, 80)
        while True:
            self.clock.tick(120)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.shape_dir = [0, -1]
                    if event.key == pg.K_RIGHT:
                        self.shape_dir = [0, 1]
                    if event.key == pg.K_DOWN:
                        pg.time.set_timer(pg.USEREVENT, 50)
                
                if event.type == pg.KEYUP:
                    if event.key == pg.K_DOWN:
                        pg.time.set_timer(pg.USEREVENT, 800)
                    if event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
                        self.shape_dir = [0, 0]


                if event.type == pg.USEREVENT:
                    self.fall_shape()
                if event.type == pg.USEREVENT+1:
                    if self.shape_dir[0] == 1:
                        self.fall_shape()
                    side_dir = [0, self.shape_dir[1]]
                    self.move_shape(side_dir)
            self.draw()

    def set_shape(self):
        self.shape_dir = [0, 0]
        for ii in range(4):
            for jj in range(4):
                if self.shape.matrix[ii][jj] == 0:
                    continue
                self.matrix[self.shape_pos[0]+ii][self.shape_pos[1]+jj] = self.shape.color

    def fall_shape(self):
        dir = [1, 0]
        new_pos = [self.shape_pos[0] + dir[0], self.shape_pos[1] + dir[1]]
        if new_pos[1] < 0:
            return
        right = self.shape.right
        if new_pos[1] + right > 15:
            return
        
        if new_pos[0] + 4 > 24:
            self.set_shape()
            self.choose_shape()
            return

        if self.check_collision(new_pos):
            self.set_shape()
            self.choose_shape()
            return

        self.shape_pos[0] += dir[0]
        self.shape_pos[1] += dir[1]

    def check_collision(self, new_pos):
        right = self.shape.right
        for i in range(4):
            for j in range(4-right):
                if self.shape.matrix[i][j] != 0:  
                    row_idx = new_pos[0] + i
                    col_idx = new_pos[1] + j
                    
                    if self.matrix[row_idx][col_idx] != 0:
                        return True
        return False

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

    def __repr__(self):
        result = ''
        for row in self.matrix:
            row_str = ''
            for col in row:
                if col == 0:
                    row_str += '0 '
                else:
                    row_str += 'X '
            result += row_str + '\n'
        result += '\n'
        return result


if __name__ == '__main__':
    game = Game()
    game.run()