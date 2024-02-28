from random import choice
import hashlib
from PIL import Image, ImageDraw


colors = [
    (255, 45, 85), (244, 164, 96), (255, 231, 87), (141, 211, 199),
    (189, 195, 199), (204, 230, 235), (155, 187, 85), (252, 203, 110),
    (230, 145, 56), (238, 102, 102), (163, 189, 44), (247, 163, 103),
    (147, 166, 169), (54, 168, 219), (95, 138, 206), (140, 101, 171),
    (221, 75, 57), (127, 146, 168), (155, 89, 182), (52, 152, 219)
]


def generate_avatar(login: str):
    hash_object = hashlib.sha256(login.encode('utf-8')).digest()

    hash_int = bin(int.from_bytes(hash_object, byteorder='big'))[2:51]

    matrix = []
    for i in range(7):
        row = []
        for j in range(4):
            value = hash_int[i * 7 + j]
            row.append(value)
        row += [0, 0, 0]
        matrix.append(row)
    
    for row in matrix:
        print(row)
        for j in range(4, 7):
            row[j] = row[7 - j - 1]
        print(row)


    color = {
        '0': (255, 255, 255),
        '1': choice(colors)
    }

    image = Image.new('RGB', (7, 7))
    pixels = image.load()
    for i in range(7):
        for j in range(7):
            pixels[j, i] = color[matrix[i][j]]

    image = image.resize((150, 150), Image.NEAREST)

    return image
