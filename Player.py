import pygame as py
from random import randint
from collections import deque
py.mixer.init()

BLOCKED = {0, 5}

moveSound=py.mixer.Sound("moveSound.mp3")
moveSound.set_volume(0.1)

class Player:
    

    def __init__(self, x:int, y:int, w:int, h:int, img):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = (self.x, self.y, self.w, self.h)
        self.collide = False
        self.img = img

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def move(self, screen, grid, event):
        r = self.y // 60
        c = self.x // 60
        if event.type == py.KEYDOWN:
            moveSound.play()
            if event.key == py.K_a and c-1 >= 0 and grid[r][c-1] not in BLOCKED:
                self.x -= 60
            if event.key == py.K_d and c+1 < len(grid[0]) and grid[r][c+1] not in BLOCKED:
                self.x += 60
            if event.key == py.K_w and r-1 >= 0 and grid[r-1][c] not in BLOCKED:
                self.y -= 60
            if event.key == py.K_s and r+1 < len(grid) and grid[r+1][c] not in BLOCKED:
                self.y += 60

    


class Obstacle:
    def __init__(self, x:int, y:int, img):
        self.x = x
        self.y = y
        self.img = img

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))


class Enemy:
    def __init__(self, grid_row: int, grid_col: int, img):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.img = img
        self.alive = True

    @property
    def px(self): return self.grid_col * 60
    @property
    def py_pos(self): return self.grid_row * 60

    @property
    def trap_row(self): return self.grid_row
    @property
    def trap_col(self): return self.grid_col - 1

    @property
    def trap_row_below(self): return self.grid_row + 1      
    @property
    def trap_col_below(self): return self.grid_col          

    def draw(self, screen):
        if self.alive:
            screen.blit(self.img, (self.px, self.py_pos))


class Friend:
    def __init__(self, grid_row: int, grid_col: int, img):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.img = img
        self.alive = True

    @property
    def px(self): return self.grid_col * 60
    @property
    def py_pos(self): return self.grid_row * 60

    # trap tile to the RIGHT of friend
    @property
    def trap_row_right(self): return self.grid_row
    @property
    def trap_col_right(self): return self.grid_col + 1

    # trap tile ABOVE friend
    @property
    def trap_row_above(self): return self.grid_row - 1
    @property
    def trap_col_above(self): return self.grid_col

    def draw(self, screen):
        if self.alive:
            screen.blit(self.img, (self.px, self.py_pos))


class Sprite:
    def __init__(self, grid_row: int, grid_col: int, img):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.img = img
        self.active = False          # starts inactive until player moves 2 tiles away

    @property
    def px(self): return self.grid_col * 60
    @property
    def py_pos(self): return self.grid_row * 60

    def draw(self, screen):
        if self.active:
            screen.blit(self.img, (self.px, self.py_pos))

    def bfs(self, grid, target_row, target_col):
        """Find next step toward target using BFS shortest path."""
        start = (self.grid_row, self.grid_col)
        goal  = (target_row, target_col)
        if start == goal:
            return start

        rows = len(grid)
        cols = len(grid[0])
        visited = {start}
        queue = deque([(start, [])])

        while queue:
            (r, c), path = queue.popleft()
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    if grid[nr][nc] not in (0, 5) or (nr, nc) == goal:
                        visited.add((nr, nc))
                        new_path = path + [(nr, nc)]
                        if (nr, nc) == goal:
                            return new_path[0] if new_path else start
                        queue.append(((nr, nc), new_path))
        return start   # no path found, stay still

    def move_toward(self, grid, target_row, target_col):
        if not self.active:
            return
        next_step = self.bfs(grid, target_row, target_col)
        self.grid_row, self.grid_col = next_step
