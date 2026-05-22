import pygame as py
from random import randint
from Player import Player, Obstacle, Enemy

py.mixer.init()
py.init()

cell_w, cell_h = 60, 60
row, col = 9, 9
screen_w, screen_h = col * cell_w, row * cell_h
panel_w = 3 * cell_w

screen = py.display.set_mode((screen_w + panel_w, screen_h))
py.display.set_caption("Generating random grid")


grid = [[randint(0, 2) for _ in range(col)] for _ in range(row)]

# 0 stays as wall, 1 and 2 become floor or rare coin
for r in range(row):
    for c in range(col):
        if grid[r][c] != 0:
            grid[r][c] = 1 if randint(1, 5) != 1 else 3   # 1 in 5 chance of coin, rest plain floor

# Grid value legend
# 0  = wall/obstacle
# 1  = open floor
# 2  = chest / special tile
# 3  = coin (uncollected)
# 4  = random floor filler (treated as open)
# 5  = enemy body tile  (blocked – player can't walk here)
# 6  = collected coin image
# 7  = key on floor  (player steps + SPACE to collect)
# 8  = portal        (player steps on it → next room)

for r in grid:
    print(r)


char       = py.transform.scale(py.image.load("mainChar.png"),       (50, 50))
obstacle   = py.transform.scale(py.image.load("wall.jpg"),           (60, 60))
background = py.transform.scale(py.image.load("background1.jpeg"),   (screen_w, screen_h))
coin_sound = py.mixer.Sound("chieuk-coin-257878.mp3")
coinImg    = py.transform.scale(py.image.load("coin(1).png"),        (50, 50))
enemyImg   = py.transform.scale(py.image.load("enemy.png"),          (50, 50))
keyImg     = py.transform.scale(py.image.load("key.png"),            (40, 40))
portalImg  = py.transform.scale(py.image.load("portal.png"),         (60, 60))


p1 = Player(0, 0, 60, 60, char)
ENEMY_ROW, ENEMY_COL = 0, col - 1

obstacleList = []
for r in range(row):
    for c in range(col):
        if grid[r][c] == 0:
            obstacleList.append(Obstacle(c * cell_w, r * cell_h, obstacle))
# Hero spawn
grid[0][0] = 1
grid[0][1] = 1
grid[1][0] = 1
grid[1][1] = 1

# Enemy area — top-right
grid[0][col - 1] = 1
grid[0][col - 2] = 1
grid[1][col - 1] = 1

# Portal area — bottom-right
grid[row - 1][col - 1] = 1
grid[row - 1][col - 2] = 1
grid[row - 2][col - 1] = 1

# Place enemy
grid[ENEMY_ROW][ENEMY_COL] = 5          # mark as blocked so player can't walk onto enemy
enemy = Enemy(ENEMY_ROW, ENEMY_COL, enemyImg)

coin               = 0
hp                 = 100
has_key            = False
portal_open        = False
fight_prompt_active = False
game_over= False

clock = py.time.Clock()


def drawGrid(grid):
    index = 0
    for r in range(row):
        for c in range(col):
            val = grid[r][c]
            if val == 0:
                obstacleList[index].draw(screen)
                index += 1
            elif val == 3:                                   
                screen.blit(coinImg,   (c * 60 + 5, r * 60 + 5))
            elif val == 7:
                screen.blit(keyImg,    (c * 60 + 10, r * 60 + 10))
            elif val == 8:
                screen.blit(portalImg, (c * 60, r * 60))

def draw_panel(coin, hp, has_key):
    font = py.font.SysFont(None, 30)
    py.draw.rect(screen, "#8BD0CA", (screen_w, 0, panel_w, screen_h))
    screen.blit(font.render(f"Coins : {coin}", True, "#ffffff"), (screen_w + 20,  40))
    screen.blit(font.render(f"HP    : {hp}",   True, "#ff4444"), (screen_w + 20,  80))
    if has_key:
        screen.blit(font.render("KEY !", True, "#ffe066"), (screen_w + 20, 120))


def draw_fight_prompt():
    font_big   = py.font.SysFont(None, 40)
    font_small = py.font.SysFont(None, 30)

    box_w, box_h = 320, 140
    box_x = (screen_w - box_w) // 2
    box_y = (screen_h - box_h) // 2

    py.draw.rect(screen, "#1a1a2e", (box_x, box_y, box_w, box_h), border_radius=10)
    py.draw.rect(screen, "#e2b96f", (box_x, box_y, box_w, box_h), width=2, border_radius=10)

    screen.blit(font_big.render("An enemy blocks your path!", True, "#e2b96f"), (box_x + 20, box_y + 18))
    screen.blit(font_small.render("Do you want to fight?",    True, "#ffffff"), (box_x + 65, box_y + 58))

    py.draw.rect(screen, "#2d6a4f", (box_x + 40,  box_y + 95, 90, 32), border_radius=6)
    screen.blit(font_small.render("YES  [Y]", True, "#ffffff"), (box_x + 50,  box_y + 102))

    py.draw.rect(screen, "#7a1e1e", (box_x + 190, box_y + 95, 90, 32), border_radius=6)
    screen.blit(font_small.render("NO  [N]",  True, "#ffffff"), (box_x + 202, box_y + 102))



def draw_game_over():
    font_big    = py.font.SysFont(None, 80)
    font_medium = py.font.SysFont(None, 40)
    font_small  = py.font.SysFont(None, 30)

    # Dark overlay over the whole screen
    overlay = py.Surface((screen_w + panel_w, screen_h))
    overlay.set_alpha(180)
    overlay.fill("#000000")
    screen.blit(overlay, (0, 0))

    # YOU DIED text
    died_text = font_big.render("YOU DIED", True, "#cc0000")
    screen.blit(died_text, (died_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 - 80)).topleft))

    # Game over subtext
    over_text = font_medium.render("GAME OVER", True, "#ffffff")
    screen.blit(over_text, (over_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2)).topleft))

    # Restart prompt
    restart_text = font_small.render("Press  R  to restart", True, "#aaaaaa")
    screen.blit(restart_text, (restart_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 + 70)).topleft))


def find(coin):
    r = p1.y // 60
    c = p1.x // 60
    if event.type == py.KEYDOWN:
        if event.key == py.K_SPACE and grid[r][c] == 3:
            coin += 1
            grid[r][c] = 6
            coin_sound.play()
    return coin






def check_enemy_trap(hp, has_key, portal_open):
    global fight_prompt_active

    r = p1.y // 60
    c = p1.x // 60

    # player steps on trap tile → show prompt
    if enemy.alive and r == enemy.trap_row and c == enemy.trap_col:
        if not fight_prompt_active:
            fight_prompt_active = True

    #  YES / NO while prompt is open
    if fight_prompt_active and enemy.alive:
        if event.type == py.KEYDOWN:
            if event.key == py.K_y:
                fight_prompt_active = False
                damage = randint(1, 100)
                hp = max(0, hp - damage)
                print(f"You fought! -{damage} HP  (HP remaining: {hp})")
                if hp <= 0:
                    global game_over
                    game_over = True
                    hp = 0
                    print("You died!")
                else:
                    grid[enemy.grid_row][enemy.grid_col] = 1
                    grid[enemy.trap_row][enemy.trap_col]  = 7
                    enemy.alive = False
                            
                    grid[enemy.grid_row][enemy.grid_col] = 1     # enemy tile → open floor
                    grid[enemy.trap_row][enemy.trap_col]  = 7    # spawn key on trap tile
                    enemy.alive = False

            elif event.key == py.K_n:                        # FLEE
                fight_prompt_active = False
                print("You backed away...")
                p1.x = max(0, (enemy.trap_col - 1) * 60)    # push player one cell left

    # player on key tile + SPACE → collect key, spawn portal
    if event.type == py.KEYDOWN:
        if event.key == py.K_SPACE and grid[r][c] == 7:
            grid[r][c] = 1
            has_key = True
            print("Key collected!")
            grid[row - 1][col - 1] = 8
            portal_open = True
            print("A portal appeared at the bottom-right corner!")

    # Step 4: player steps on portal → next room
    if portal_open and grid[r][c] == 8:
        print("Entering portal… loading next room!")
        load_next_room()

    return hp, has_key, portal_open


def load_next_room():
    global grid, obstacleList, enemy, portal_open, has_key, fight_prompt_active,ENEMY_ROW, ENEMY_COL

    print("=== LOADING NEXT ROOM ===")

    # Reset all flags
    portal_open         = False
    has_key             = False
    fight_prompt_active = False

    # Fresh random grid
    grid = [[randint(0, 4) for _ in range(col)] for _ in range(row)]

    # Open tiles around player spawn
    grid[0][0], grid[0][1], grid[1][0] = 1, 1, 1

    # Top-right: enemy (no portal yet — must be re-earned)
    grid[ENEMY_ROW][ENEMY_COL] = 5

    # Bottom-right: open floor, NOT a portal yet
    grid[row - 1][col - 1] = 1

    # New enemy object
    enemy = Enemy(ENEMY_ROW, ENEMY_COL, enemyImg)

    # Rebuild obstacles
    obstacleList.clear()
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 0:
                obstacleList.append(Obstacle(c * cell_w, r * cell_h, obstacle))

    # Respawn player at top-left
    p1.x, p1.y = 0, 0

def restart_game():
    global grid, obstacleList, enemy, portal_open, has_key
    global fight_prompt_active, coin, hp, game_over, ENEMY_ROW, ENEMY_COL

    hp                  = 100
    coin                = 0
    portal_open         = False
    has_key             = False
    fight_prompt_active = False
    game_over           = False

    grid = [[randint(0, 4) for _ in range(col)] for _ in range(row)]
    grid[0][0], grid[0][1], grid[1][0] = 1, 1, 1
    grid[row - 1][col - 1] = 1
    grid[row - 2][col - 1] = 1
    grid[row - 1][col - 2] = 1
    grid[ENEMY_ROW][ENEMY_COL] = 5

    obstacleList.clear()
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 0:
                obstacleList.append(Obstacle(c * cell_w, r * cell_h, obstacle))

    enemy  = Enemy(ENEMY_ROW, ENEMY_COL, enemyImg)
    p1.x, p1.y = 0, 0
    print("=== GAME RESTARTED ===")


run = True
while run:
    for event in py.event.get():
        if event.type == py.QUIT:
            run = False

        if event.type == py.KEYDOWN:
            if event.key == py.K_r and game_over:
                restart_game()
                continue                      # skip all other processing this frame

        if not game_over:
            if not fight_prompt_active:
                p1.move(screen, grid, event)
                coin = find(coin)
            hp, has_key, portal_open = check_enemy_trap(hp, has_key, portal_open)

    clock.tick(15)

    screen.blit(background, (0, 0))
    drawGrid(grid)

    if enemy.alive:
        enemy.draw(screen)

    draw_panel(coin, hp, has_key)
    p1.draw(screen)

    if fight_prompt_active and not game_over:
        draw_fight_prompt()

    if game_over:
        draw_game_over()

    py.display.flip()

py.quit()