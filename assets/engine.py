import pygame
import math
import os
import ast

global e_colorkey, typekey, stack_key
e_colorkey = (255, 255, 255)
typekey = { # Category, size, cost, score, satisfaction, earnings
    "pipeline": ['a', (1, 1), 100, 5, 1, 0],
    "reservoir": ['a', (2, 1), 200, 10, 2, 0],
    "newater": ['a', (1, 1), 500, 30, 3, 0],
    "power": ['a', (2, 1), 100, 5, 1, 0],
    "solar": ['a', (2, 1), 200, 10, 2, 0],
    "nuclear": ['a', (2, 1), 1000, 50, 0, 0],
    "landed": ['h', (1, 1), 500, 3, 7, 0],
    "condo1": ['h', (2, 2), 200, 5, 6, 0],
    "condo2": ['h', (1, 4), 200, 5, 6, 0],
    "hdb1": ['h', (2, 2), 200, 5, 4, 0],
    "hdb2": ['h', (1, 4), 200, 5, 4, 0],
    "hdb2-1": ['h', (4,1), 200, 5, 4, 0],
    "hdb_stacked1": ['h', (2, 2), 200, 5, 4, 0],
    "hdb_stacked2": ['h', (1, 4), 200, 5, 4, 0],
    "hdb_stacked2-1": ['h', (1, 4), 200, 5, 4, 0],
    "squatter": ['h', (2, 1), 0, 10, -5, 0],
    "primary": ['e', (2, 1), 300, 20, 1, 30],
    "secondary1": ['e', (2, 2), 1000, 15, 2, 50],
    "secondary2": ['e', (1, 4), 1000, 15, 2, 50],
    "tertiary1": ['e', (2, 1), 2000, 10, 5, 100],
}
stack_key = {
    "hdb1": 11,
    "hdb_stacked1": 11,
    "hdb2": 11,
    "hdb_stacked2": 11,
    "hdb_stacked2-1": 11,
    "hdb2-1": 13,
    "condo1": 14,
    "condo2": 15,
    "condo2-2": 16,
    "tertiary1": 31,
    "tertiary1-1": 32,
}
TILE_SIZE = 32


def set_global_colorkey(colorkey):
    global e_colorkey
    e_colorkey = colorkey


def load_txt(path):
    with open(path, 'r') as fp:
        return fp.read().splitlines()


def draw_txt(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def blit_center(surf, surf2, pos):  # surf is the surface blitted on
    x = int(surf2.get_width() / 2)
    y = int(surf2.get_height() / 2)
    surf.blit(surf2, (pos[0] - x, pos[1] - y))


class Animation:
    def __init__(self):
        self.anims = {}
        self.states = []
        self.anim_frames = []

    def update(self, display, SIZE, index):
        pygame.transform.scale(self.anim_frames[index], SIZE, display)

    def positional(self, display, index, positions):
        for position in positions:
            display.blit(self.anim_frames[index], position)

    def load_frames(self, path, name, frame_amt, frame_times):
        frame_list = []
        for i in range(frame_amt):
            image = pygame.image.load(f"{path}/sprites/{name}_{i}.png").convert()
            image.set_colorkey((255, 255, 255))
            frame_list.append(image)
        self.anims[name] = [frame_list, frame_times]
        self.states.append(0)

    def play_anims(self, frame):
        i = 0
        for key in self.anims:
            if frame % int(self.anims[key][1][self.states[i]]) == 0:
                self.states[i] += 1
                if self.states[i] >= len(self.anims[key][0]):
                    self.states[i] = 0
            self.anim_frames.append(self.anims[key][0][self.states[i]])
            i += 1


class Building:
    def __init__(self, x, y, size, type=None, cost=None):
        self.x = x
        self.y = y
        self.size = size
        self.type = type
        self.cost = cost
        self.image = None
        self.ghost = None
        self.surface = None
        self.color = None
        self.rect = pygame.Rect(self.x, self.y, self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE)
        self.placed = False
        self.hold = None
        self.fill_val = 0

    def update(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE)

    def load_image(self):
        self.image = pygame.image.load(f"assets/sprites/{self.type}.png").convert()
        self.image.set_colorkey(e_colorkey)
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        self.ghost = self.image.copy()
        self.ghost.set_alpha(128)

    def update_size(self, size):
        self.size = size
        self.rect = pygame.Rect(self.x, self.y, self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE)

    def set_surface(self, image=None, color=None):
        if color is not None:
            self.surface = pygame.Surface((self.size[0] * TILE_SIZE, self.size[1] * TILE_SIZE))
            self.surface.fill(color)
        if image is not None:
            self.surface = pygame.Surface((5 * TILE_SIZE, 5 * TILE_SIZE))
            self.surface = pygame.transform.scale(image, (5 * TILE_SIZE, 5 * TILE_SIZE), self.surface)

    def rotate(self):
        if self.type[-2:] == "-1":
            try:
                self.type = self.type[0:-2]
                self.load_image()
                self.update_size((self.size[1], self.size[0]))
            except FileNotFoundError:
                self.type = self.type + "-1"
        else:
            try:
                self.type = self.type + "-1"
                self.load_image()
                self.update_size((self.size[1], self.size[0]))
            except FileNotFoundError:
                self.type = self.type[0:-2]

    def hover(self, grid, mouse_pos):
        relative_x = ((mouse_pos[0] / 3 - grid.x) // TILE_SIZE) * TILE_SIZE
        relative_y = ((mouse_pos[1] / 3 - grid.y) // TILE_SIZE) * TILE_SIZE
        if relative_x > grid.size[0] * TILE_SIZE - self.size[0] * TILE_SIZE:
            relative_x = grid.size[0] * TILE_SIZE - self.size[0] * TILE_SIZE
        if relative_x < 0:
            relative_x = 0
        if relative_y < 0:
            relative_y = 0
        if relative_y > grid.size[1] * TILE_SIZE - self.size[1] * TILE_SIZE:
            relative_y = grid.size[1] * TILE_SIZE - self.size[1] * TILE_SIZE
        grid.surface.blit(self.ghost, (relative_x, relative_y))
        self.hold = (relative_x, relative_y)
        self.update(mouse_pos[0], mouse_pos[1])


class Grid(Building):
    def __init__(self, x, y, size, type=None, cost=None):
        super().__init__(x, y, size, type, cost)
        self.grid_array = [[None for x in range(self.size[0])] for i in range(self.size[1])]

    def check_grid(self, position, object):
        hold = None
        triggered = False
        size = (int(object.size[0]), int(object.size[1]))
        position = (int(position[0] // TILE_SIZE), int(position[1] // TILE_SIZE))
        for y in range(position[1], position[1] + size[1]):
            for x in range(position[0], position[0] + size[0]):
                if not triggered:
                    hold = self.grid_array[y][x]
                    triggered = not triggered
                if self.grid_array[y][x] != hold:
                    return [False, False]
        return [True, hold is not None]

    # expanding grid
    def update_grid(self, num):
        stock = [None for _ in range(len(self.grid_array[0]) + num)]
        for row in self.grid_array:
            for _ in range(num):
                row.append(None)
        for _ in range(num):
            self.grid_array.append(stock)

    def place(self, object, position):
        self.fill_val += 1
        result = self.check_grid(position, object)
        if not result[0]:
            return False
        else:
            if result[1] and object.type not in stack_key:
                return False
            size = object.size
            relative_x = int(position[0] // TILE_SIZE)
            relative_y = int(position[1] // TILE_SIZE)
            for y in range(relative_y, relative_y + size[1]):
                for x in range(relative_x, relative_x + size[0]):
                    self.grid_array[y][x] = self.fill_val

            if result[1]:
                if object.type[-2:] == "-1":
                    object.type = f"{object.type[0:-3]}_stacked{object.type[-3]}-1"
                else:
                    object.type = f"{object.type[0:-1]}_stacked{object.type[-1]}"
                object.load_image()
            return True

    def remove(self, object, position):
        size = (int(object.size[0]), int(object.size[1]))
        hold = None
        triggered = False
        position = (int(position[0] // TILE_SIZE), int(position[1] // TILE_SIZE))
        copy = self.grid_array.copy()
        for y in range(position[1], position[1] + size[1]):
            for x in range(position[0], position[0] + size[0]):
                if not triggered:
                    hold = copy[y][x]
                    triggered = not triggered
                if copy[y][x] != hold:
                    return False
        if hold is not None:
            for y in range(position[1], position[1] + size[1]):
                for x in range(position[0], position[0] + size[0]):
                    self.grid_array[y][x] = None



