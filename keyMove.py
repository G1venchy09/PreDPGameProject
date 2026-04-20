import pygame as py
py.init()
sWidth, sHeight=600,600
screen=py.display.set_mode((sWidth,sHeight))
py.display.set_caption("Keyboard movement")



x,y,r=sWidth/2,sHeight/2,20
speedX,speedY=5,5

def collision(x,y,r):
    if y+r>=200 and y+r<=300:
        if x+r>=400 and x-r<=405:
            print("Collision")
            return True
    return False    
running=True
"""
create an objects of clock
This is an extremely efficient way of coding game as this will not use
cpu/processing or battery a lot. It will halt the processing for this programm
depending on the clock spped
"""
clock=py.time.Clock()

while running:
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
    clock.tick(60)#this will set max framerate to 60

    screen.fill("#ffffff")   #this will delete the previous screen 
    py.draw.circle(screen,"#ff0000",(x,y),r)
    py.draw.line(screen,"#4bd4e6df",(400,200),(400,300,),5)
    keys=py.key.get_pressed()
    if keys[py.K_a]and x >r and not collision(x,y,r):
        x-=speedX
    if keys[py.K_d]and x<600-r and not collision(x,y,r):
        x+=speedX
    if keys[py.K_w]and y>r:
        y-=speedY
    if keys[py.K_s]and y<600-r:
        y+=speedY
    
    py.display.flip()
    py.time.delay(100)

py.quit()
 