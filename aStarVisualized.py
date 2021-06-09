import pygame
import math
from queue import PriorityQueue


WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A star path finding algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Cell:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    # verify what kind of cell it is
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

    def is_path(self):
        return self.color == PURPLE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, window):
        pygame.draw.rect(window, self.color,
                         (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # row+1 means going down one row row-1 going up one row
        # col+1 means going right one col col-1 going left one col
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():
            # making the cell below a neighbor
            self.neighbors.append(grid[self.row+1][self.col])
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():
            # making the cell above a neighbor
            self.neighbors.append(grid[self.row-1][self.col])
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():
            # making the cell to the right a neighbor
            self.neighbors.append(grid[self.row][self.col+1])
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():
            # making the cell to the left a neighbor
            self.neighbors.append(grid[self.row][self.col-1])

    def __lt__(self, other):
        return False

    def reset(self):
        self.color = WHITE


def h(p1, p2):  # for h part of A* get distances between start and end for approximation
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)


def make_grid(rows, width):  # creates actual logic grid
    grid = []
    gap = width//rows  # distance between cells with integer division

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            cell = Cell(i, j, gap, rows)
            grid[i].append(cell)

    return grid


def draw_grid(window, rows, width):  # draws the gridlines
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i*gap), (width, i*gap))
        pygame.draw.line(window, GREY, (i*gap, 0), (i*gap, width))


def draw(window, grid, rows, width):  # draws our cells and gridlines
    window.fill(WHITE)

    for row in grid:
        for cell in row:
            cell.draw(window)

    draw_grid(window, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width//rows
    y, x = pos
    row = y//gap
    col = x//gap

    return row, col


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    # start is actual cell, 0 is the F score and count will be a tie breaker in case of 2 exact F scores
    open_set.put((0, count, start))
    came_from = {}  # keeps track which node this node came from

    # this dictionary holds all g scores and initializes them as maximum in the beginning using list comprehension
    # g score the shortest distance from start to current cell
    g_score = {cell: float("inf") for row in grid for cell in row}
    g_score[start] = 0
    f_score = {cell: float("inf") for row in grid for cell in row}
    # start will get the approximate h value from the start to the end
    f_score[start] = h(start.get_pos(), end.get_pos())

    # hash to check what items are actuall in the queue
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # 2 refers to the third variable which is our actual cell
        current_cell = open_set.get()[2]
        open_set_hash.remove(current_cell)

        if current_cell == end:  # reconstruct path from end to beginning
            reconstruct_path(came_from,end,draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current_cell.neighbors:
            # each neighbor is distance 1 apart from another
            temp_g_score = g_score[current_cell]+1

            # if we found a better way to reach a neighbor than before update the path
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current_cell
                g_score[neighbor] = temp_g_score
                # h here is the difference in distance remaining from the neighbor to the end cell
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()  # referring to the lambda function
        if current_cell != start:
            current_cell.make_closed()
    return False

def reconstruct_path(came_from,current_cell,draw):
    while(current_cell in came_from):
        current_cell=came_from[current_cell]
        current_cell.make_path()
        draw()
    

def main(window, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    # variables to check if algorithm started
    start = None
    end = None

    run = True
    algStarted = False
    while(run):
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if algStarted:
                continue
            if pygame.mouse.get_pressed()[0]:  # mouseclick 1 pressed
                posXY = pygame.mouse.get_pos()
                row, col = get_clicked_pos(posXY, ROWS, width)
                cell = grid[row][col]
                if not start:
                    start = cell
                    start.make_start()
                elif not end and cell != start:
                    end = cell
                    end.make_end()
                elif cell != start and cell != end:
                    cell.make_barrier()
            elif pygame.mouse.get_pressed()[2]:  # mouseclick 2 pressed
                posXY = pygame.mouse.get_pos()
                row, col = get_clicked_pos(posXY, ROWS, width)
                cell = grid[row][col]
                cell.reset()
                if cell == start:
                    start = None
                if cell == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not algStarted and start and end:
                    for row in grid:
                        for cell in row:
                            cell.update_neighbors(grid)
                    algorithm(lambda: draw(WINDOW, grid,
                              ROWS, width), grid, start, end)

                    # equivalent of x=lambda: print Hello
                    # x= def func():
                    #     print Hello
                    # x()
                
                if event.key==pygame.K_c: #clear screen
                    start=None
                    end=None
                    grid=make_grid(ROWS,width)
                    

    pygame.quit()


main(WINDOW, WIDTH)
