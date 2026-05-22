import pygame as py
from random import randint
py.mixer.init()
BLOCKED = {0, 5}
class Player:
    """
    Player is a rectangle object of pygame
    So it must take x,y, width and height
    """
    speedX,speedY=randint(3,6),randint(1,4)
    def __init__(self,x:int,y:int,w:int,h:int,img):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.rect=(self.x,self.y,self.w,self.h)
        self.collide=False
        self.img=img
        

    def draw(self,screen):
        
        # return py.draw.rect(screen,"#ffffff",self.rect)
        screen.blit(self.img,(self.x,self.y))
    
    def move(self, screen, grid, event):
        r = self.y // 60
        c = self.x // 60
        if event.type == py.KEYDOWN:
            if event.key == py.K_a and c-1 >= 0 and grid[r][c-1] not in BLOCKED:
                self.x -= 60
            if event.key == py.K_d and c+1 < len(grid[0]) and grid[r][c+1] not in BLOCKED:
                self.x += 60
            if event.key == py.K_w and r-1 >= 0 and grid[r-1][c] not in BLOCKED:
                self.y -= 60
            if event.key == py.K_s and r+1 < len(grid) and grid[r+1][c] not in BLOCKED:
                self.y += 60

        

    def collision(self,enemy):
        if abs(self.x-enemy.x)<=self.w and abs(self.y-enemy.y)<=self.h:
            if self.collide==False:
                print("send to gulag")
                self.collide=True
        elif self.collide==True:
            self.collide=False




class Obstacle:
    def __init__(self,x:int,y:int,img):
        self.x=x
        self.y=y
        self.img=img

    def draw(self,screen):
        screen.blit(self.img,(self.x,self.y))
        # return py.draw.rect(screen,"#000000",(self.x,self.y,60,60))

class Enemy:
    """
    Placed on the grid at (grid_row, grid_col).
    The tile directly IN FRONT of the enemy (one cell to the left by default)
    is the 'trap tile'.  When the player steps on it they take random HP damage,
    the enemy vanishes and is replaced by a key on the same trap tile.
    """
    def __init__(self, grid_row: int, grid_col: int, img):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.img = img
        self.alive = True                       # False once the player triggers the trap

    # pixel position of the enemy sprite
    @property
    def px(self): return self.grid_col * 60
    @property
    def py_pos(self): return self.grid_row * 60

    # the trap tile is one cell to the LEFT of the enemy
    @property
    def trap_row(self): return self.grid_row
    @property
    def trap_col(self): return self.grid_col - 1

    def draw(self, screen):
        if self.alive:
            screen.blit(self.img, (self.px, self.py_pos))