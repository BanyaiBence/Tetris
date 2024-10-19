import pygame as pg
from random import choice
from colors import Colors, Color
import json
import os

type Matrix[T] = list[list[T]]
type Font = pg.font.Font
type Clock = pg.time.Clock

type MaybeMatrix[T] = Matrix[T] | None

pg.init()
pg.font.init()

class Game:
    
    SHAPES: Matrix[int] = [[[1, 1, 1, 1]],
              [[1, 1], [1, 1]],
              [[1, 1, 0], [0, 1, 1]],
              [[0, 1, 1], [1, 1, 0]],
              [[1, 1, 1], [0, 1, 0]],
              [[1, 1, 1], [1, 0, 0]],
              [[1, 1, 1], [0, 0, 1]]
              ]
    FALL_EVENT: int = pg.USEREVENT
    LEFT_EVENT: int = pg.USEREVENT + 1
    RIGHT_EVENT: int = pg.USEREVENT + 2
    DOWN_EVENT: int = pg.USEREVENT + 3
    FONT: Font = pg.font.SysFont("Arial", 16)
    SCORE_FONT: Font = pg.font.SysFont("Arial", 32)
    DEBUG: bool = False
    DIMENSIONS: list[int] = [12, 24]
    SQUARE_SIZE: int = 40
    WIDTH: int = SQUARE_SIZE*DIMENSIONS[0]
    HEIGHT: int = SQUARE_SIZE*DIMENSIONS[1]
    SAVE_FILE: str = "save.json"

    def __init__(self):
        pg.init()
        self.window: pg.Surface = pg.display.set_mode((Game.WIDTH, Game.HEIGHT))
        pg.display.set_caption('Tetris')
        self.clock: Clock = pg.time.Clock()

        self.matrix: Matrix[int] = [[0 for i in range(Game.DIMENSIONS[0])] for j in range(Game.DIMENSIONS[1])]
        self.score: int = 0
        
        self.reset_shape()
        self.load()

    def load(self) -> bool:
        try:
            with open(Game.SAVE_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return False
        
        for key, value in data.items():
            setattr(self, key, value)


    def new_shape(self) -> list[int]:
        shape = choice(self.SHAPES)
        return shape
    
    
    def draw_shape(self) -> None:
        S: int = Game.SQUARE_SIZE
        P: list[int] = self.shape_pos
        for i, row in enumerate(self.shape):
            for j, col in enumerate(row):
                if col == 0:
                    continue
                pg.draw.rect(self.window, self.shape_color,
                    ((P[1]+j)*S, (P[0]+i)*S, S, S))   

    def draw(self) -> None:
        self.window.fill(Colors.BLACK)
        S: int = Game.SQUARE_SIZE
        self.draw_ghost()
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if Game.DEBUG:
                    text: pg.Surface = Game.FONT.render(f"({i},{j})", False, Colors.WHITE)
                    self.window.blit(text, (j*S, i*S))
                if col == 0:
                    continue
                pg.draw.rect(self.window, col,
                    (j*S, i*S, S, S))
                

        self.draw_shape()
        for i in range(len(self.matrix)):
            pg.draw.line(self.window, Colors.WHITE, (0, i*S), (Game.WIDTH, i*S))

        for j in range(len(self.matrix[0])):
            pg.draw.line(self.window, Colors.WHITE, (j*S, 0), (j*S, Game.HEIGHT))
        text: pg.Surface = Game.SCORE_FONT.render(str(self.score), False, Colors.RED)
        self.window.blit(text, (Game.WIDTH-45, 30))
        
        pg.display.flip()

    def schedule_move(self, direction) -> None:
        P: list[int] = self.shape_pos
        D: list[int] = direction
        self.next_pos: list[int] = [P[0] + D[0], P[1] + D[1]]

    def move(self) -> None:
        self.shape_pos: list[int] = self.next_pos

    def save(self) -> None:
        with open(Game.SAVE_FILE, "w") as f:
            dict_to_save: dict = {}
            for key, value in self.__dict__.items():
                if is_jsonable(value):
                    dict_to_save[key] = value
            json.dump(dict_to_save, f)

    def events(self) -> None:
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

    def run(self) -> None :
        if not self.DEBUG:
            pg.time.set_timer(Game.FALL_EVENT, 500)
        while True:
            self.clock.tick(60)
            self.events()
            if not self.collision(self.shape, self.shape_pos, self.next_pos):
                self.move()
            
            self.try_save(self.shape, self.shape_pos, self.next_pos)

            self.clear_rows()
            self.draw()
            

    def in_bounds(self, pos: list[int]) -> bool:
        x: int = pos[1]
        y: int = pos[0]
        if x < 0 or x >= Game.DIMENSIONS[0]:
            return False
        if y < 0 or y >= Game.DIMENSIONS[1]:
            return False
        return True


    def collision(self, shape: MaybeMatrix[int] =None, shape_pos: list[int] =[0, 0], next_pos: list[int] =[0, 0]) -> bool:
        x: int = shape_pos[1]
        y: int = shape_pos[0]
        nx: int = next_pos[1]
        ny: int = next_pos[0]
        d: tuple = (ny - y, nx - x)

        if d[0]:
            if y + len(shape) >= Game.DIMENSIONS[1]:
                return True

            for i, row in enumerate(shape):
                for j, col in enumerate(row):
                    if col and self.in_bounds((ny+i, x+j)) and self.matrix[ny+i][x+j]:
                        return True

        if d[1]:
            if nx < 0 or nx + len(shape[0]) > Game.DIMENSIONS[0]:
                return True

            for i, row in enumerate(shape):
                for j, col in enumerate(row):
                    if col and self.in_bounds((y+i, nx+j)) and self.matrix[y+i][nx+j]:
                        return True
                    
    def try_save(self, shape: MaybeMatrix[int], shape_pos: list[int]=[0, 0], next_pos: list[int]=[0, 0]) -> bool:
        x: int = shape_pos[1]
        y: int = shape_pos[0]
        ny: int = next_pos[0]
        if y + len(shape) >= Game.DIMENSIONS[1]:
                self.save_shape()
                return True

        for i, row in enumerate(shape):
            for j, col in enumerate(row):
                if col and self.in_bounds((ny+i, x+j)) and self.matrix[ny+i][x+j]:
                    self.save_shape()
                    return True
        return False
                    
    def test_collision(self, shape: Matrix[int] =None, shape_pos: list[int]=[0, 0]) -> bool:
        x: int = shape_pos[1]
        y: int = shape_pos[0]
        if y + len(shape) >= Game.DIMENSIONS[1]:
            return True
        if x < 0 or x + len(shape[0]) > Game.DIMENSIONS[0]:
            return True
        for i, row in enumerate(shape):
            for j, col in enumerate(row):
                if col and self.in_bounds((y+i, x+j)) and self.matrix[y+i][x+j]:
                    return True


        
    def save_shape(self) -> None:
        x: int = self.shape_pos[1]
        y: int = self.shape_pos[0]
        if y == 0:
            os.remove(Game.SAVE_FILE)
            quit()
        for i, row in enumerate(self.shape):
            for j, col in enumerate(row):
                if col:
                    self.matrix[y+i][x+j] = self.shape_color
        self.reset_shape()

    def reset_shape(self) -> None:
        self.shape: Matrix[int] = self.new_shape()
        self.shape_color: Color = Colors.random_color()
        self.shape_pos: list[int] = [0, 5]
        self.next_pos: list[int] = [1, 5]


    def rotate_shape(self) -> None:
        new_shape: Matrix[int] = list(zip(*self.shape[::-1]))
        succ: bool = False
        if not self.test_collision(new_shape, self.shape_pos):
            succ: bool = True
            self.shape: Matrix[int] = new_shape 
        if self.DEBUG:
            print(f"Rotate: {self.shape} -> {new_shape}: {'SUCCESS' if succ else 'FAILURE'}")
    
    def clear_rows(self) -> None:
        for i, row in enumerate(self.matrix):
            if all(row):
                self.matrix.pop(i)
                self.matrix.insert(0, [0 for i in range(Game.DIMENSIONS[0])])
                self.score += 1

    def calc_ghost(self) -> list[int]:
        x: int = self.shape_pos[1]
        y: int = self.shape_pos[0]

        while not self.collision(self.shape, [y, x], [y+1, x]):
            y += 1
        return [y, x]
        

    def draw_ghost(self) -> None:
        S: int = Game.SQUARE_SIZE
        P: list[int] = self.calc_ghost()
        for i, row in enumerate(self.shape):
            for j, col in enumerate(row):
                if col == 0:
                    continue
                pg.draw.rect(self.window, Colors.WHITE,
                    ((P[1]+j)*S, (P[0]+i)*S, S, S))

def is_jsonable(obj: any) -> bool:
    try:
        json.dumps(obj)
        return True
    except:
        return False

if __name__ == '__main__':
    game: Game = Game()
    game.run()