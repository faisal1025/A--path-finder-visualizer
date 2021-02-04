import pygame
from queue import PriorityQueue

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finder Visualizer")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_row):  # width is the each spot width
        self.row = row
        self.col = col
        self.y = row * width   # row at which you are * each width  = gives y position
        self.x = col * width   # col at which you are * each width  = gives x position
        self.color = WHITE
        self.neighbour = []
        self.width = width
        self.total_row = total_row

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_barrier(self):
        self.color = BLACK

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        # x and y is the position width is the length of each spot
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbour(self, grid):
        if self.row < self.total_row - 1 and not grid[self.row+1][self.col].is_barrier():  # down
            self.neighbour.append(grid[self.row+1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # up
            self.neighbour.append(grid[self.row - 1][self.col])

        if self.col < self.total_row - 1 and not grid[self.row][self.col + 1].is_barrier():  # right
            self.neighbour.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # left
            self.neighbour.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    row1, col1 = p1
    row2, col2 = p2
    return abs(row1 - row2) + abs(col1 - col2)


def draw_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        if not current.is_start():
            current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_list = PriorityQueue()
    open_list.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_list_hash = {start}

    while not open_list.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_list.get()[2]
        open_list_hash.remove(current)
        if current == end:
            draw_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbour in current.neighbour:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())

                if neighbour not in open_list_hash:
                    count += 1
                    open_list.put((f_score[neighbour], count, neighbour))
                    open_list_hash.add(neighbour)
                    neighbour.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(total_rows, total_width):
    grid = []
    width = total_width // total_rows
    for i in range(total_rows):
        grid.append([])
        for j in range(total_rows):
            spot = Spot(i, j, width, total_rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, total_rows, total_width):
    width = total_width // total_rows
    for i in range(total_rows):
        pygame.draw.line(win, GREY, (0, i * width), (total_width, i * width))  # horizontal line
        for j in range(total_rows):
            pygame.draw.line(win, GREY, (j * width, 0), (j * width, total_width))  # vertical line


def draw(win, grid, total_rows, total_width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, total_rows, total_width)  # this method draw lines after drawing the grid
    pygame.display.update()


def get_clicked_pos(pos, total_rows, total_width):
    width = total_width // total_rows
    x, y = pos

    row = y // width
    col = x // width

    return row, col


def main(win, total_width):
    total_rows = 50
    grid = make_grid(total_rows, total_width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, total_rows, total_width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, total_rows, total_width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != start and spot != end:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, total_rows, total_width)
                spot = grid[row][col]
                if spot.is_start():
                    start = None
                    spot.reset()
                elif spot.is_end():
                    end = None
                    spot.reset()
                elif spot.is_barrier():
                    spot.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbour(grid)

                    algorithm(lambda: draw(win, grid, total_rows, total_width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(total_rows, total_width)

    pygame.quit()


main(WIN, WIDTH)







