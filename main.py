import pygame
import sys
import random
from assets.engine import *

pygame.init()

global SCREENSIZE, TILE_SIZE, WIDTH, HEIGHT, font, mainClock, PATH
SCREENSIZE = (1200, 900)
TILE_SIZE = 32
WIDTH, HEIGHT = 400, 300
font = pygame.font.SysFont("gabriola", 30)
mainClock = pygame.time.Clock()
grid_width = 5
PATH = "assets"
starting_money = 1000

global typekey
typekey = {  # Category, cost, score, satisfaction, earnings
    "pipeline": ['a', (1, 1), 100, 5, 1, 0],
    "reservoir": ['a', (2, 1), 200, 10, 2, 0],
    "newater": ['a', (1, 1), 500, 30, 3, 0],
    "reservoir-1": ['a', (1, 2), 200, 10, 2, 0],
    "power": ['a', (2, 1), 100, 5, 1, 0],
    "power-1": ['a', (2, 1), 100, 5, 1, 0],
    "solar": ['a', (2, 1), 200, 10, 2, 0],
    "solar-1": ['a', (1, 2), 200, 10, 2, 0],
    "nuclear": ['a', (2, 1), 1000, 50, 0, 0],
    "nuclear-1": ['a', (2, 1), 1000, 50, 0, 0],
    "landed": ['h', (1, 1), 500, 3, 7, 0],
    "condo1": ['h', (2, 2), 200, 5, 6, 0],
    "condo2": ['h', (1, 4), 200, 5, 6, 0],
    "condo2-1": ['h', (4, 1), 200, 5, 6, 0],
    "condo_stacked1": ['h', (2, 2), 300, 5, 6, 0],
    "condo_stacked2": ['h', (1, 4), 300, 5, 6, 0],
    "condo_stacked2-1": ['h', (4, 1), 300, 5, 6, 0],
    "hdb1": ['h', (2, 2), 200, 5, 4, 0],
    "hdb2": ['h', (1, 4), 200, 5, 4, 0],
    "hdb2-1": ['h', (4, 1), 200, 5, 4, 0],
    "hdb_stacked1": ['h', (2, 2), 300, 5, 4, 0],
    "hdb_stacked2": ['h', (1, 4), 300, 5, 4, 0],
    "hdb_stacked2-1": ['h', (1, 4), 300, 5, 4, 0],
    "squatter": ['h', (2, 1), 0, 10, -5, 0],
    "squatter-1": ['h', (1, 2), 0, 10, -5, 0],
    "primary": ['e', (2, 1), 300, 20, 1, 30],
    "primary-1": ['e', (1, 2), 300, 20, 1, 30],
    "secondary1": ['e', (2, 2), 1000, 15, 2, 50],
    "secondary2": ['e', (1, 4), 1000, 15, 2, 50],
    "secondary2-1": ['e', (4, 1), 1000, 15, 2, 50],
    "tertiary1": ['e', (2, 1), 2000, 10, 5, 100],
    "tertiary_stacked1": ['e', (2, 1), 2100, 10, 5, 100]
}

display = pygame.display.set_mode(SCREENSIZE)
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("yes")
pygame.display.init()

mouse_indicator = pygame.Rect(0, 0, 2, 2)

# grid initialisation
grass = pygame.image.load("assets/sprites/grass.png").convert()
grid_x, grid_y = (WIDTH / 2 - (32 * grid_width // 2), HEIGHT / 2 - (32 * grid_width // 2))
grid = Grid(grid_x, grid_y, (grid_width, grid_width))


def draw_grid():
    grid.set_surface(image=grass)
    for x in range(0, grid_width * 32 + 32, 32):
        pygame.draw.line(grid.surface, (0, 0, 0), (x, 0), (x, grid_width * 32))
    for y in range(0, grid_width * 32 + 32, 32):
        pygame.draw.line(grid.surface, (0, 0, 0), (0, y), (grid_width * 32, y))


draw_grid()

# background stuff
waves = Animation()
waves.load_frames(PATH, "wave", 5, (12, 12, 12, 12, 12))
waves.load_frames(PATH, "bigwave", 2, (30, 30))


# objects


def init_object(cat):
    mx, my = pygame.mouse.get_pos()
    item = Building(mx, my, typekey[cat][1], cat, typekey[cat][2])
    item.load_image()
    return item


stats = [0, 10, starting_money, 0, 0, 0, 0]


def update_stats(stats, object_list):
    growth = 2
    max_pop = stats[1]
    for object in object_list:
        data = typekey[object[0].type]
        if data[0] == 'e':
            max_pop -= data[3]
            if max_pop > 0:
                stats[2] += data[5] * data[3]
            else:
                stats[2] += data[5] * (data[3] + max_pop)

    if stats[1] > stats[3] or stats[1] > stats[4] or stats[1] > stats[5] or stats[1] > stats[6]:
        lose(stats)
        return
    stats[0] += 1
    if stats[0] == 5:
        growth = 5
    stats[1] += growth


def purchase(stats, object):
    data = typekey[object.type]

    if stats[2] - data[2] >= 0:
        stats[2] -= data[2]
    else:
        return False
    if data[0] == 'a':
        stats[6] += data[3]
        stats[3] += data[4]
    if data[0] == 'h':
        stats[4] += data[3]
        stats[3] += data[4]
    if data[0] == 'e':
        stats[5] += data[3]
    return True


def show_stats(stats):  # expect stats to be in format [day, population, $, satisfaction, houses, jobs, amenities]
    lines = [f"DAY {stats[0]}",
             f"WALLET: ${stats[2]}",
             f"POPULATION: {stats[1]}",
             "Advance to next day",
             "by pressing Q",
             "Delete buildings for the",
             "cost of $100 by pressing Y"]
    lines2 = ["Don't let any drop",
              "below population!",
              f"HAPPINESS: {stats[3]}",
              f"JOBS: {stats[5]}",
              f"HOUSING: {stats[4]}",
              f"AMENITIES: {stats[6]}", ]
    sized = pygame.font.SysFont("gabriola", 15)
    y = 40
    for text in lines:
        draw_txt(text, sized, (0, 0, 0), screen, 0, y)
        y += 25
    y = 40
    for text in lines2:
        draw_txt(text, sized, (0, 0, 0), screen, 300, y)
        y += 25


def lose(stats):
    screen.fill((255, 255, 255))
    pygame.display.set_caption("Game Over!")
    lose = pygame.Surface((1200, 900))
    lose.fill((0, 0, 0))
    lose.set_alpha(100)
    running = True
    while running:
        draw_txt("Your stats were too low to keep up with population growth! You Lose!", font, (255, 20, 20), lose, 0,
                 0)
        draw_txt(f"You survived to day {stats[0]}!", font, (255, 20, 20), lose, 0, 50)
        display.blit(lose, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        mainClock.tick(60)


def mainmenu():
    screen.fill((255, 255, 255))
    main = pygame.image.load("assets/sprites/main.png").convert()
    menu = pygame.Surface((1200, 900))
    pygame.display.set_caption("Main")
    start = pygame.Rect(375, 310, 450, 130)
    help = pygame.Rect(375, 490, 450, 150)
    quit = pygame.Rect(375, 670, 450, 130)
    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if start.collidepoint(mx, my):
                        running = False
                    if help.collidepoint(mx, my):
                        helpmenu()
                    if quit.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()
        pygame.transform.scale(screen, SCREENSIZE, display)
        pygame.draw.rect(menu, (255, 0, 0), start)
        pygame.draw.rect(menu, (0, 255, 0), help)
        pygame.draw.rect(menu, (0, 0, 255), quit)
        display.blit(menu, (0, 0))
        menu.set_alpha(0)
        pygame.transform.scale(main, SCREENSIZE, display)
        pygame.display.update()
        mainClock.tick(60)


def helpmenu():
    current_state = 1
    running = True
    menu = pygame.Surface((WIDTH, HEIGHT))
    pygame.display.set_caption("Help")
    font = pygame.font.SysFont("arial", 15)
    controls = pygame.image.load("assets/sprites/controls.png").convert()
    while running:
        menu.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_state = 1
                if event.key == pygame.K_2:
                    current_state = 2
                if event.key == pygame.K_3:
                    current_state = 3
                if event.key == pygame.K_4:
                    current_state = 4
                if event.key == pygame.K_5:
                    current_state = 5
                if event.key == pygame.K_6:
                    current_state = 6
                if event.key == pygame.K_ESCAPE:
                    running = False
        if current_state == 1:
            menu.fill((255, 100, 100))
            menu.set_alpha(255)
            menu_text = [
                "Press 2 to access controls",
                "Press 3 to access building hotkeys & information",
                "Objective: Survive without letting any component",
                "",
                "",
            ]
            text_y = 0
            for text in menu_text:
                draw_txt(text, font, (0, 0, 0), menu, 0, text_y)
                text_y += 15
        if current_state == 2:
            menu.fill((255, 100, 100))
            menu.set_alpha(255)
            menu_text = [
                "Y : Toggle Deletion Mode",
                "R : Rotate buildings",
                "Q : Activate next day"
                "LMB : Place buildings",
                "RMB : Cancel Choice",
            ]
            text_y = 0
            for text in menu_text:
                draw_txt(text, font, (0, 0, 0), menu, 0, text_y)
                text_y += 20
        if current_state == 3:
            menu.fill((255, 100, 100))
            menu.set_alpha(255)
            pygame.transform.scale(controls, (WIDTH, HEIGHT), menu)
        screen.blit(menu, (0, 0))
        pygame.transform.scale(screen, SCREENSIZE, display)
        pygame.display.update()
        mainClock.tick(60)


objectlist = []
mainmenu()
next = pygame.Rect(WIDTH - 90, 200, 75, 50)
frame = 0
# todo -> fix animations
deletion = False
help_rect = pygame.Rect(0, 0, 50, 30)
help_toggle = False
while True:
    if frame <= 60:
        frame += 1
        if frame % 30:
            ...
    else:
        frame = 0

    pygame.display.set_caption("game")

    screen.fill((0, 0, 255))
    draw_grid()
    waves.play_anims(frame)
    waves.update(screen, (WIDTH, HEIGHT), 1)
    waves.positional(display, 0, ((0, 0), (50, 20), (300, 40), (250, 180)))
    mouse_indicator.x = (pygame.mouse.get_pos()[0] - 2) / (SCREENSIZE[0] / 400)
    mouse_indicator.y = (pygame.mouse.get_pos()[1] - 2) / (SCREENSIZE[0] / 400)

    draw_txt("help", font, (0, 0, 0), screen, 0, 0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if len(objectlist) and not objectlist[-1][1]:
                    if grid.place(objectlist[-1][0], objectlist[-1][0].hold):
                        objectlist[-1][1] = True
                        if not purchase(stats, objectlist[-1][0]):
                            grid.remove(objectlist[-1][0], objectlist[-1][0].hold)
                            objectlist.pop()
                if deletion:
                    if stats[2] - 100 >= 0:
                        for object in objectlist:
                            if object[0].rect.collidepoint(pygame.mouse.get_pos()):
                                objectlist.remove(object)
                                grid.remove(object[0], object[0].hold)
                                stats[2] -= 100
                if help_rect.collidepoint(pygame.mouse.get_pos()[0] // 3, pygame.mouse.get_pos()[1] // 3):
                    helpmenu()

                # elif help_button.collidepoint(mx ,my)...
            if event.button == 3:
                if len(objectlist) > 0:
                    if not objectlist[-1][1]:
                        objectlist.pop()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                update_stats(stats, objectlist)
            if event.key == pygame.K_y:
                deletion = not deletion
            if event.key == pygame.K_r:
                if len(objectlist) != 0 and not objectlist[-1][1]:
                    objectlist[-1][0].rotate()
            if event.key == pygame.K_a:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("pipeline"), False])
            if event.key == pygame.K_s:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("reservoir"), False])
            if event.key == pygame.K_d:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("newater"), False])
            if event.key == pygame.K_f:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("power"), False])
            if event.key == pygame.K_g:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("solar"), False])
            if event.key == pygame.K_h:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("nuclear"), False])
            if event.key == pygame.K_i:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("landed"), False])
            if event.key == pygame.K_j:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object(f"condo{random.randint(1, 2)}"), False])
            if event.key == pygame.K_k:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object(f"hdb{random.randint(1, 2)}"), False])
            if event.key == pygame.K_l:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("squatter"), False])
            if event.key == pygame.K_z:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("primary"), False])
            if event.key == pygame.K_x:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object(f"secondary{random.randint(1, 2)}"), False])
            if event.key == pygame.K_c:
                if len(objectlist) == 0 or objectlist[-1][1]:
                    objectlist.append([init_object("tertiary1"), False])

    for object in objectlist:
        if object[1]:
            grid.surface.blit(object[0].image, object[0].hold)

    if len(objectlist) != 0 and not objectlist[-1][1]:
        objectlist[-1][0].hover(grid, pygame.mouse.get_pos())

    if deletion:
        draw_txt("DELETION MODE ON", font, (255, 0, 0), screen, 180, 30)
    show_stats(stats)
    screen.blit(grid.surface, (grid.x, grid.y))
    pygame.transform.scale(screen, SCREENSIZE, display)

    pygame.display.update()
    mainClock.tick(60)
