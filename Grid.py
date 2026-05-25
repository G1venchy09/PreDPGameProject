import pygame as py
from random import randint
from Player import Player, Obstacle, Enemy, Friend, Sprite

py.mixer.init()
py.init()

cell_w, cell_h = 60, 60
row, col = 9, 9
screen_w, screen_h = col * cell_w, row * cell_h
panel_w = 3 * cell_w

screen = py.display.set_mode((screen_w + panel_w, screen_h))
py.display.set_caption("Generating random grid")

# ── Enemy position ────────────────────────────────────────────────────
ENEMY_ROW, ENEMY_COL = 0, col - 1

# ── Grid ─────────────────────────────────────────────────────────────
grid = [[randint(0, 4) for _ in range(col)] for _ in range(row)]

# Clear border corridors so there is always a path around the map
for c in range(col):
    grid[0][c] = 1
for r in range(row):
    grid[r][0] = 1
for c in range(col):
    grid[row - 1][c] = 1
for r in range(row):
    grid[r][col - 1] = 1

# Place enemy
grid[ENEMY_ROW][ENEMY_COL] = 5

# Guarantee all important tiles have at least one open neighbour
important_tiles = [
    (0, 0),                        # hero spawn
    (ENEMY_ROW, ENEMY_COL - 1),    # enemy trap tile left
    (ENEMY_ROW + 1, ENEMY_COL),    # enemy trap tile below
    (row - 1, col - 1),            # portal
]

if False:
    important_tiles += [
        (row - 1, 0),              # friend
        (row - 1, 1),              # right of friend
        (row - 2, 0),              # above friend
    ]

for (tr, tc) in important_tiles:
    if 0 <= tr < row and 0 <= tc < col:
        grid[tr][tc] = 1
        neighbours = []
        if tr - 1 >= 0:  neighbours.append((tr-1, tc))
        if tr + 1 < row: neighbours.append((tr+1, tc))
        if tc - 1 >= 0:  neighbours.append((tr, tc-1))
        if tc + 1 < col: neighbours.append((tr, tc+1))
        has_open = any(grid[nr][nc] not in (0, 5) for nr, nc in neighbours)
        if not has_open:
            nr, nc = neighbours[randint(0, len(neighbours) - 1)]
            grid[nr][nc] = 1

# Place coins only on open floor tiles
for r in range(row):
    for c in range(col):
        if grid[r][c] == 1 and randint(1, 5) == 1:
            grid[r][c] = 3

# Guarantee every coin has at least one open neighbour
for r in range(row):
    for c in range(col):
        if grid[r][c] == 3:
            neighbours = []
            if r - 1 >= 0:  neighbours.append((r-1, c))
            if r + 1 < row: neighbours.append((r+1, c))
            if c - 1 >= 0:  neighbours.append((r, c-1))
            if c + 1 < col: neighbours.append((r, c+1))
            has_open = any(grid[nr][nc] not in (0, 5) for nr, nc in neighbours)
            if not has_open:
                nr, nc = neighbours[randint(0, len(neighbours) - 1)]
                grid[nr][nc] = 1

for r in grid:
    print(r)

# ── Assets ───────────────────────────────────────────────────────────
char       = py.transform.scale(py.image.load("mainChar.png"),      (50, 50))
obstacle   = py.transform.scale(py.image.load("wall.jpg"),          (60, 60))
background = py.transform.scale(py.image.load("background1.jpeg"),  (screen_w, screen_h))
background2 = py.transform.scale(py.image.load("background2.webp"), (screen_w, screen_h))
background3 = py.transform.scale(py.image.load("background3.jpg"), (screen_w, screen_h))

backgrounds = [background, background2, background3]
friendImg  = py.transform.scale(py.image.load("friend.png"), (50, 50))
coin_sound = py.mixer.Sound("chieuk-coin-257878.mp3")
coinImg    = py.transform.scale(py.image.load("coin(1).png"),       (50, 50))
enemyImg   = py.transform.scale(py.image.load("enemy.png"),         (50, 50))
keyImg     = py.transform.scale(py.image.load("key.png"),           (40, 40))
portalImg  = py.transform.scale(py.image.load("portal.png"),        (60, 60))
spriteImg  = py.transform.scale(py.image.load("sprite.png"), (50, 50))

# ── Objects ──────────────────────────────────────────────────────────
p1 = Player(0, 0, 60, 60, char)

sprite              = Sprite(0, 0, spriteImg)    # starts at hero spawn
sprite_just_hit     = False                      # true right after collision
sprite_move_timer   = 0                          # controls sprite movement speed
SPRITE_MOVE_DELAY   = 7                         # frames between each sprite step


obstacleList = []
for r in range(row):
    for c in range(col):
        if grid[r][c] == 0:
            obstacleList.append(Obstacle(c * cell_w, r * cell_h, obstacle))

enemy = Enemy(ENEMY_ROW, ENEMY_COL, enemyImg)

# ── State ─────────────────────────────────────────────────────────────
coin                = 0
hp                  = 100
has_key             = False
portal_open         = False
fight_prompt_active = False
game_over           = False
current_room=0
friend              = None       # only exists in room 2
talk_prompt_active  = False
game_over           = False
victory             = False

clock = py.time.Clock()

# ── Draw helpers ──────────────────────────────────────────────────────
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

    box_w, box_h = 400, 140
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

    overlay = py.Surface((screen_w + panel_w, screen_h))
    overlay.set_alpha(180)
    overlay.fill("#000000")
    screen.blit(overlay, (0, 0))

    died_text = font_big.render("YOU DIED", True, "#cc0000")
    screen.blit(died_text, died_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 - 80)).topleft)

    over_text = font_medium.render("GAME OVER", True, "#ffffff")
    screen.blit(over_text, over_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2)).topleft)

    restart_text = font_small.render("Press  R  to restart", True, "#aaaaaa")
    screen.blit(restart_text, restart_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 + 70)).topleft)


def draw_talk_prompt():
    font_big   = py.font.SysFont(None, 40)
    font_small = py.font.SysFont(None, 30)

    box_w, box_h = 340, 140
    box_x = (screen_w - box_w) // 2
    box_y = (screen_h - box_h) // 2

    py.draw.rect(screen, "#1a1a2e", (box_x, box_y, box_w, box_h), border_radius=10)
    py.draw.rect(screen, "#66bb6a", (box_x, box_y, box_w, box_h), width=2, border_radius=10)

    screen.blit(font_big.render("You've met your friend!", True, "#66bb6a"), (box_x + 20, box_y + 18))
    screen.blit(font_small.render("Talk?",                 True, "#ffffff"), (box_x + 130, box_y + 58))

    py.draw.rect(screen, "#2d6a4f", (box_x + 40,  box_y + 95, 90, 32), border_radius=6)
    screen.blit(font_small.render("YES  [Y]", True, "#ffffff"), (box_x + 50,  box_y + 102))

    py.draw.rect(screen, "#7a1e1e", (box_x + 210, box_y + 95, 90, 32), border_radius=6)
    screen.blit(font_small.render("NO  [N]",  True, "#ffffff"), (box_x + 222, box_y + 102))


def draw_victory():
    font_big    = py.font.SysFont(None, 80)
    font_medium = py.font.SysFont(None, 40)
    font_small  = py.font.SysFont(None, 30)

    overlay = py.Surface((screen_w + panel_w, screen_h))
    overlay.set_alpha(200)
    overlay.fill("#000000")
    screen.blit(overlay, (0, 0))

    escaped_text = font_big.render("YOU ESCAPED!", True, "#ffd700")
    screen.blit(escaped_text, escaped_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 - 110)).topleft)

    dungeon_text = font_medium.render("from the dungeon!", True, "#ffffff")
    screen.blit(dungeon_text, dungeon_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 - 40)).topleft)

    victory_text = font_medium.render("VICTORY", True, "#ffd700")
    screen.blit(victory_text, victory_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 + 10)).topleft)

    coins_text = font_small.render(f"Coins collected : {coin}", True, "#f0c040")
    screen.blit(coins_text, coins_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 + 65)).topleft)

    hp_text = font_small.render(f"HP remaining    : {hp}", True, "#ff4444")
    screen.blit(hp_text, hp_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 + 100)).topleft)

    restart_text = font_small.render("Press  R  to play again", True, "#aaaaaa")
    screen.blit(restart_text, restart_text.get_rect(center=((screen_w + panel_w) // 2, screen_h // 2 + 145)).topleft)

# ── Coin pick-up ──────────────────────────────────────────────────────
def find(coin,event):
    r = p1.y // 60
    c = p1.x // 60
    if event.type == py.KEYDOWN:
        if event.key == py.K_SPACE and grid[r][c] == 3:
            coin += 1
            grid[r][c] = 6
            coin_sound.play()
    return coin


def check_sprite(hp):
    global sprite_just_hit, sprite_move_timer

    if not sprite.active:
        # Activate once player is 2 tiles away from spawn (0,0)
        player_row = p1.y // 60
        player_col = p1.x // 60
        distance = abs(player_row - 0) + abs(player_col - 0)
        if distance >= 2:
            sprite.active = True
            print("The sprite awakens!")
        return hp

    player_row = p1.y // 60
    player_col = p1.x // 60

    # Check collision
    if sprite.grid_row == player_row and sprite.grid_col == player_col:
        if not sprite_just_hit:
            hp = max(0, hp - 10)
            sprite_just_hit = True
            print(f"Sprite attacks! -10 HP  (HP remaining: {hp})")
            if hp <= 0:
                global game_over
                game_over = True
                print("You died!")
    else:
        # Player moved away by at least 1 tile — reset hit flag
        if sprite_just_hit:
            dist = abs(sprite.grid_row - player_row) + abs(sprite.grid_col - player_col)
            if dist >= 1:
                sprite_just_hit = False

    # Move sprite toward player on a timer
    sprite_move_timer += 1
    if sprite_move_timer >= SPRITE_MOVE_DELAY:
        sprite_move_timer = 0
        sprite.move_toward(grid, player_row, player_col)

    return hp


# ── Enemy trap + key + portal ─────────────────────────────────────────
def check_enemy_trap(hp, has_key, portal_open,event):
    global fight_prompt_active, game_over

    r = p1.y // 60
    c = p1.x // 60

    # Step 1: player steps on trap tile (left OR below) → show prompt
    on_left_trap  = r == enemy.trap_row       and c == enemy.trap_col
    on_below_trap = r == enemy.trap_row_below and c == enemy.trap_col_below

    if enemy.alive and (on_left_trap or on_below_trap):
        if not fight_prompt_active:
            fight_prompt_active = True

    # Step 2: handle YES / NO
    if fight_prompt_active and enemy.alive:
        if event.type == py.KEYDOWN:
            if event.key == py.K_y:
                fight_prompt_active = False
                damage = randint(1, 100)
                hp = max(0, hp - damage)
                print(f"You fought! -{damage} HP  (HP remaining: {hp})")

                if hp <= 0:
                    game_over = True
                    hp = 0
                    print("You died!")
                else:
                    grid[enemy.grid_row][enemy.grid_col] = 1
                    grid[enemy.trap_row][enemy.trap_col]  = 7
                    enemy.alive = False

            elif event.key == py.K_n:
                fight_prompt_active = False
                print("You backed away...")
                p1.x = max(0, (enemy.trap_col - 1) * 60)

    # Step 3: player on key tile + SPACE
    if event.type == py.KEYDOWN:
        if event.key == py.K_SPACE and grid[r][c] == 7:
            grid[r][c] = 1
            has_key = True
            print("Key collected!")
            grid[row - 1][col - 1] = 8
            portal_open = True
            print("A portal appeared at the bottom-right corner!")

    # Step 4: player steps on portal
    if portal_open and grid[r][c] == 8:
        if current_room >= 2:
            global victory
            victory = True
            print("You escaped the dungeon!")
            return hp, has_key, portal_open    # ← return immediately
        else:
            print("Entering portal… loading next room!")
            load_next_room()

    return hp, has_key, portal_open            

def check_friend(hp, event):
    global talk_prompt_active

    if friend is None or not friend.alive:
        return hp

    r = p1.y // 60
    c = p1.x // 60

    # Step 1: player steps on tile to the right or above friend → show prompt
    on_right_trap = r == friend.trap_row_right and c == friend.trap_col_right
    on_above_trap = r == friend.trap_row_above and c == friend.trap_col_above

    if on_right_trap or on_above_trap:
        if not talk_prompt_active:
            talk_prompt_active = True

    # Step 2: handle YES / NO
    if talk_prompt_active:
        if event.type == py.KEYDOWN:
            if event.key == py.K_y:
                talk_prompt_active = False
                heal = randint(1, 100 - hp)  if hp < 100 else 0
                hp = min(100, hp + heal)
                print(f"Friend healed you for {heal} HP! (HP: {hp})")
                grid[friend.grid_row][friend.grid_col] = 1   # friend disappears
                friend.alive = False

            elif event.key == py.K_n:
                talk_prompt_active = False
                print("You walked away...")
                p1.y = max(0, p1.y - 60)    # always move one tile up
    return hp


# ── Room loading ──────────────────────────────────────────────────────
def load_next_room():
    global grid, obstacleList, enemy, portal_open, has_key
    global fight_prompt_active, current_room, background
    global friend, talk_prompt_active, victory
    global sprite, sprite_just_hit, sprite_move_timer

    portal_open         = False
    has_key             = False
    fight_prompt_active = False
    talk_prompt_active  = False
    current_room        += 1
    background          = backgrounds[current_room % len(backgrounds)]

    grid = [[randint(0, 4) for _ in range(col)] for _ in range(row)]

# Clear border corridors
    for c in range(col):
        grid[0][c] = 1
    for r in range(row):
        grid[r][0] = 1
    for c in range(col):
        grid[row - 1][c] = 1
    for r in range(row):
        grid[r][col - 1] = 1

    # Place enemy
    grid[ENEMY_ROW][ENEMY_COL] = 5

    # Important tiles
    important_tiles = [
        (0, 0),
        (ENEMY_ROW, ENEMY_COL - 1),
        (ENEMY_ROW + 1, ENEMY_COL),
        (row - 1, col - 1),
    ]

    if current_room == 1:
        important_tiles += [
            (row - 1, 0),
            (row - 1, 1),
            (row - 2, 0),
        ]

    for (tr, tc) in important_tiles:
        if 0 <= tr < row and 0 <= tc < col:
            grid[tr][tc] = 1
            neighbours = []
            if tr - 1 >= 0:  neighbours.append((tr-1, tc))
            if tr + 1 < row: neighbours.append((tr+1, tc))
            if tc - 1 >= 0:  neighbours.append((tr, tc-1))
            if tc + 1 < col: neighbours.append((tr, tc+1))
            has_open = any(grid[nr][nc] not in (0, 5) for nr, nc in neighbours)
            if not has_open:
                nr, nc = neighbours[randint(0, len(neighbours) - 1)]
                grid[nr][nc] = 1

    # Coins only on open floor tiles
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 1 and randint(1, 5) == 1:
                grid[r][c] = 3

    # Guarantee every coin has at least one open neighbour
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 3:
                neighbours = []
                if r - 1 >= 0:  neighbours.append((r-1, c))
                if r + 1 < row: neighbours.append((r+1, c))
                if c - 1 >= 0:  neighbours.append((r, c-1))
                if c + 1 < col: neighbours.append((r, c+1))
                has_open = any(grid[nr][nc] not in (0, 5) for nr, nc in neighbours)
                if not has_open:
                    nr, nc = neighbours[randint(0, len(neighbours) - 1)]
                    grid[nr][nc] = 1

    # Place friend AFTER coin pass so coins can't overwrite him
    if current_room == 1:
        FRIEND_ROW, FRIEND_COL = row - 1, 0
        grid[FRIEND_ROW][FRIEND_COL]     = 1    # clear friend tile
        grid[FRIEND_ROW][FRIEND_COL + 1] = 1    # right of friend
        grid[FRIEND_ROW - 1][FRIEND_COL] = 1    # above friend
        friend = Friend(FRIEND_ROW, FRIEND_COL, friendImg)
    else:
        friend = None

    obstacleList.clear()
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 0:
                obstacleList.append(Obstacle(c * cell_w, r * cell_h, obstacle))

    # Reset sprite to hero spawn
    sprite            = Sprite(0, 0, spriteImg)
    sprite_just_hit   = False
    sprite_move_timer = 0

    global enemy
    enemy  = Enemy(ENEMY_ROW, ENEMY_COL, enemyImg)
    p1.x, p1.y = 0, 0
    print(f"=== ROOM {current_room + 1} LOADED ===")


# ── Restart ───────────────────────────────────────────────────────────
def restart_game():
    global grid, obstacleList, enemy, portal_open, has_key
    global fight_prompt_active, coin, hp, game_over
    global current_room, background, friend, talk_prompt_active, victory
    global sprite, sprite_just_hit, sprite_move_timer

    hp                  = 100
    coin                = 0
    portal_open         = False
    has_key             = False
    fight_prompt_active = False
    talk_prompt_active  = False
    current_room        = 0
    background          = backgrounds[0]
    friend              = None
    game_over=False
    victory=False

    grid = [[randint(0, 4) for _ in range(col)] for _ in range(row)]

# Clear border corridors so there is always a path around the map
    for c in range(col):
        grid[0][c] = 1
    for r in range(row):
        grid[r][0] = 1
    for c in range(col):
        grid[row - 1][c] = 1
    for r in range(row):
        grid[r][col - 1] = 1

    # Place enemy
    grid[ENEMY_ROW][ENEMY_COL] = 5

    # Guarantee all important tiles have at least one open neighbour
    important_tiles = [
        (0, 0),                        # hero spawn
        (ENEMY_ROW, ENEMY_COL - 1),    # enemy trap tile left
        (ENEMY_ROW + 1, ENEMY_COL),    # enemy trap tile below
        (row - 1, col - 1),            # portal
    ]

    if current_room == 1:
        important_tiles += [
            (row - 1, 0),              # friend
            (row - 1, 1),              # right of friend
            (row - 2, 0),              # above friend
        ]

    for (tr, tc) in important_tiles:
        if 0 <= tr < row and 0 <= tc < col:
            grid[tr][tc] = 1
            neighbours = []
            if tr - 1 >= 0:  neighbours.append((tr-1, tc))
            if tr + 1 < row: neighbours.append((tr+1, tc))
            if tc - 1 >= 0:  neighbours.append((tr, tc-1))
            if tc + 1 < col: neighbours.append((tr, tc+1))
            has_open = any(grid[nr][nc] not in (0, 5) for nr, nc in neighbours)
            if not has_open:
                nr, nc = neighbours[randint(0, len(neighbours) - 1)]
                grid[nr][nc] = 1

    # Place coins only on open floor tiles
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 1 and randint(1, 5) == 1:
                grid[r][c] = 3

    # Guarantee every coin has at least one open neighbour
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 3:
                neighbours = []
                if r - 1 >= 0:  neighbours.append((r-1, c))
                if r + 1 < row: neighbours.append((r+1, c))
                if c - 1 >= 0:  neighbours.append((r, c-1))
                if c + 1 < col: neighbours.append((r, c+1))
                has_open = any(grid[nr][nc] not in (0, 5) for nr, nc in neighbours)
                if not has_open:
                    nr, nc = neighbours[randint(0, len(neighbours) - 1)]
                    grid[nr][nc] = 1

    sprite            = Sprite(0, 0, spriteImg)
    sprite_just_hit   = False
    sprite_move_timer = 0

    obstacleList.clear()
    for r in range(row):
        for c in range(col):
            if grid[r][c] == 0:
                obstacleList.append(Obstacle(c * cell_w, r * cell_h, obstacle))

    enemy  = Enemy(ENEMY_ROW, ENEMY_COL, enemyImg)
    p1.x, p1.y = 0, 0
    print("=== GAME RESTARTED ===")


# ── Main loop ─────────────────────────────────────────────────────────
run = True
while run:
    for event in py.event.get():
        if event.type == py.QUIT:
            run = False

        if event.type == py.KEYDOWN:
            if event.key == py.K_r and (game_over or victory):
                restart_game()
                continue

        if not game_over and not victory:
            if not fight_prompt_active and not talk_prompt_active:
                p1.move(screen, grid, event)
                coin = find(coin, event)
            hp, has_key, portal_open = check_enemy_trap(hp, has_key, portal_open, event)
            hp = check_friend(hp, event)

    # Outside the event loop — runs every frame regardless of input
    if not game_over and not victory:
        hp = check_sprite(hp)                     # ← moved here                        # ← add this

    clock.tick(15)

    screen.blit(background, (0, 0))
    drawGrid(grid)

    if enemy.alive:
        enemy.draw(screen)

    if friend is not None and friend.alive:
        friend.draw(screen)

    sprite.draw(screen)                                    # ← add this

    draw_panel(coin, hp, has_key)
    p1.draw(screen)

    if fight_prompt_active and not game_over:
        draw_fight_prompt()

    if talk_prompt_active and not game_over:
        draw_talk_prompt()

    if game_over:
        draw_game_over()

    if victory:
        draw_victory()

    py.display.flip()

py.quit()