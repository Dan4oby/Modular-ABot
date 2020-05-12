# файл, предназначенный для работы модуля Image
from PIL import Image, ImageFilter, ImageDraw
import random


def rand(int1, int2, k: int):
    rand_num = random.randint(0, 100)
    if rand_num > k:
        return random.randint(int1, int2)
    else:
        return (int1 + int2) / 2


class Picture:
    def __init__(self, image):
        self.image = image
        self.width = self.image.size[0]
        self.height = self.image.size[1]

    def blacknwhite(self):
        return self.image.convert('L')

    def negative(self):
        draw = ImageDraw.Draw(self.image)
        pix = self.image.load()
        for x in range(self.width):
            for y in range(self.height):
                dx = x
                dy = y
                r = pix[x, y][0]
                g = pix[x, y][1]
                b = pix[x, y][2]
                draw.point((x, y), (255 - r, 255 - g, 255 - b))

        return self.image

    def mirror(self):
        draw = ImageDraw.Draw(self.image)
        pix = self.image.load()
        for x in range(self.width):
            for y in range(self.height):
                dx = abs(self.width - x) - 1
                dy = y
                r = pix[dx, dy][0]
                g = pix[dx, dy][1]
                b = pix[dx, dy][2]
                draw.point((x, y), (r, g, b))

        return self.image

    def horror(self):
        draw = ImageDraw.Draw(self.image)
        pix = self.image.load()
        for x in range(self.width):
            for y in range(self.height):
                dx = x
                dy = y
                r = pix[dx, dy][0]
                g = pix[dx, dy][1]
                b = pix[dx, dy][2]
                if (r + g + b) > 100:
                    sr = (r + g + b) // 3
                    draw.point((x, y), (255 - sr, 255 - sr, 255 - sr))
                else:
                    sr = (r + g + b) // 3
                    draw.point((x, y), (sr, sr, sr))

        return self.image

    def aggressive(self):
        draw = ImageDraw.Draw(self.image)
        pix = self.image.load()
        dist = 3
        for x in range(dist, self.width - dist):
            for y in range(dist, self.height - dist):
                dx = rand(x - dist, x + dist, 75)
                dy = rand(y - dist, y + dist, 75)
                r = pix[dx, dy][0]
                g = pix[dx, dy][1]
                b = pix[dx, dy][2]

                draw.point((x, y), (255, 200 - g, 200 - b))

        return self.image


    def pixel(self):
        draw = ImageDraw.Draw(self.image)
        pix = self.image.load()
        for x in range(4, self.width):
            for y in range(4, self.height):
                if x % 4 <= 1:
                    dx = x
                else:
                    dx = x - 10
                if y % 4 <= 1:
                    dy = y
                else:
                    dy = y - 10
                r = pix[dx, dy][0]
                g = pix[dx, dy][1]
                b = pix[dx, dy][2]
                draw.point((x, y), (r, g, b))

        return self.image
