from random import randint as r

type Color = tuple[int]
class Colors:
    RED: Color = (255, 0, 0)
    GREEN: Color = (0, 255, 0)
    BLUE: Color = (0, 0, 255)
    YELLOW: Color = (255, 255, 0)
    PURPLE: Color = (255, 0, 255)
    ORANGE: Color = (255, 140, 0)
    WHITE: Color = (255, 255, 255)
    BLACK: Color = (0, 0, 0)
    GRAY: Color = (150, 150, 150)


    @staticmethod
    def random_color() -> Color:
        return (r(150, 255), r(150, 255), r(150, 255))