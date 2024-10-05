from random import randint as r
class Colors:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    ORANGE = (255, 140, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def random_color():
        return (r(0, 255), r(0, 255), r(0, 255))