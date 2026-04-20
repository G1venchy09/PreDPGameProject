import pygame as py
from random import randint
py.mixer.init()
class Player:
    """
    Player is a rectangle object of pygame
    So it must take x,y, width and height
    """
    dig = py.mixer.Sound("Sheep3.oga")
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
    
    def move(self,screen,grid,event):
        r=self.y//60
        c=self.x//60
        if event .type==py.KEYDOWN:     #makes an event occur only ones even if you hold the key
            if event.key==py.K_a and c-1>=0 and grid[r][c-1]!=0:
                self.x-=60
                Player.dig.play()
            if event.key==py.K_d and c+1<len(grid[0]) and grid[r][c+1]!=0:
                self.x+=60
                Player.dig.play()
            if event.key==py.K_w and r-1>=0 and grid[r-1][c]!=0:
                self.y-=60
                Player.dig.play()
            if event.key==py.K_s and r+1<len(grid) and grid[r+1][c]!=0:
                self.y+=60
                Player.dig.play() 

        # keys=py.key.get_pressed() 
        # if keys[py.K_a]and self.x>0: 
        #     self.x-=Player.speedX
        # if keys[py.K_d]and self.x<600-self.w :
        #     self.x+=Player.speedX
        # if keys[py.K_w]and self.y>0:
        #     self.y-=Player.speedY
        # if keys[py.K_s]and self.y<600-self.h:
        #     self.y+=Player.speedY
        # self.rect=(self.x,self.y,self.w,self.h)


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
    