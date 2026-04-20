"""
here we will work with images in pygame
the way images work - they are drawn on a surface
Create a rectangle of a given size and then we will simply draw the image
at the coordinates of the rectangle
All the images which are used in a project must be located within the same folder as the 
python script
You must never load an image insude the loop. You can draw insude the loop
Char image ref:https://vectorportal.com/no/vector/fotballspiller-cristiano-ronaldo.ai/30147
"""

import pygame as py
py.init()
w,h=600,600

screen=py.display.set_mode((w,h))
py.display.set_caption("Working with images in pygame")
img=py.image.load("char.jpg")
img=py.transform.scale(img,(400,400))
x,y=0,0
clock=py.time.Clock()

run=True 
while run:
    clock.tick(25)
    for event in py.event.get():
        if event.type == py.QUIT:
            run = False
    screen.fill("#ffffff")
    screen.blit(img,(x,y))
    x,y=x+1,y+1
    


    py.display.flip()
py.quit()



