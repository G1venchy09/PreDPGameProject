import pygame as py
from random import randint
from Player import Player
from Player import Obstacle
py.mixer.init()
'''
obstacle image ref = https://freesvg.org/fire-icon
background image ref = https://www.deviantart.com/melcenage/art/1-The-Fallen-Cathedral-DnD-Background-1314006525
char image ref = https://www.deviantart.com/tag/hollowknightfandom
dig file ref = https://minecraft.fandom.com/wiki/Category:Sound_effects
'''
#in this cript we will generate n x n grid o the screen
#our player can only move within these cells in the grid
cell_w, cell_h = 60,60
row, col = 9, 9
screen_w, screen_h = col * cell_w, row*cell_h
panel_w = 3*cell_w
#generating random value of 0 and 1 in the grid list
# which decides where we draw obstacles
screen = py.display.set_mode((screen_w + panel_w, screen_h))
py.display.set_caption("Generating random grid")
screen.fill("#ffffff")
global grid
py.init()
 
grid =[[randint(0,4) for i in range(col)] for j in range(row)]
grid[0][0], grid[0][1], grid[1][0] = 1, 1, 1
for r in grid:
    print(r)
 
char = py.image.load("char.jpg")
char = py.transform.scale(char, (50, 50))
obstacle = py.image.load("wall.jpg")
obstacle = py.transform.scale(obstacle, (60, 60))
background = py.image.load("background.jpg")
background = py.transform.scale(background,(screen_w,screen_h))
dig = py.mixer.Sound("Sheep3.oga")
coin_sound = py.mixer.Sound("chieuk-coin-257878.mp3")
coinImg=py.image.load("coin(1).png")
coinImg=py.transform.scale(coinImg,(50,50))
 
p1 = Player(0, 0, 60, 60, char)
obstacleList = []
for r in range(row):
    for c in range(col):
        if grid[r][c]== 0:
                obstacleList.append(Obstacle(c*cell_w, r*cell_h, obstacle)) #we append the obstacles based on the grid (we append/we create them)
 
#set the speedX and speedY to thecell width and cell height
# so the player moves exactly as the amount of a cell
# Player.speedX = cell_w
# Player.speedY = cell_h
clock = py.time.Clock()
 
def drawGrid(grid:list[list]):
    index = 0
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 0:
                # py.draw.rect(screen, "#000000", (cell_w*c, cell_h*r, cell_w,cell_h))
                obstacleList[index].draw(screen)
                index+=1
            elif grid[r][c]==6:
                screen.blit(coinImg,(c*60,r*60))

 
 
coin = 0
def draw_panel(coin):
    font = py.font.SysFont(None, 30)
    py.draw.rect(screen, "#8BD0CA", (screen_w, 0, panel_w, screen_h))
    textSurface = font.render(f"Coins:{coin}", True, "#ffffff" )
    screen.blit(textSurface, (screen_w+20, 40))
    
 
def find(coin): #this will take an action based on the value in the grid when a key is pressed
    r = p1.y // 60
    c = p1.x // 60
    if event.type == py.KEYDOWN:
        if event.key == py.K_SPACE and grid[r][c] == 3:
            coin += 1
            grid[r][c] = 6
            coin_sound.play()
    return coin
run = True
while run:
    for event in py.event.get():
        if event.type == py.QUIT:
            run = False
        p1.move(screen, grid, event)
        coin = find(coin)
       
    clock.tick(15)
    #erase the previous creen
    # screen.fill("#ffffff")
    screen.blit(background, (0,0))
    # draw the grid
    drawGrid(grid)
    draw_panel(coin)
    #then draw the player
    p1.draw(screen)
 
    #then move the player
    # p1.move(screen)
    #then move the player
    # for enemy in obstacleList:
    #     p1.collision(enemy)
 
    py.display.flip()
py.quit()