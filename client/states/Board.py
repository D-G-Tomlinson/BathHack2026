import pygame as pg
from string import ascii_uppercase

from backend_handler import get_game, make_move

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HOVER = (200, 200, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

NUMBER_FONT = pg.font.SysFont("monospace", 12)

FONT = pg.font.SysFont("centurygothic", 48)
BUTTON_FONT = pg.font.SysFont("centurygothic", 28)
INPUT_FONT  = pg.font.SysFont("centurygothic", 32)
TITLE_FONT = pg.font.SysFont("centurygothic",72)
TIMER_FONT = pg.font.SysFont("centurygothic", 24)

info = pg.display.Info()
(width, height) = info.current_w, info.current_h

drag = None

loading = pg.transform.scale(pg.image.load("Images/Cat_loading_screen.png"),(2.2*300, 300))

server_state = None # {'board': [[None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None]], 'cancelled': 0, 'pieces': {'bag': ['a', 'l', 'q', 'p', 'a', 'e', 'g', 'a', 'n', 'o', 'f', 'h', 'b', 'e', 'n', 't', 'e', 'k', 's', 'b', 'l', 'o', 'l', 'a', 'g', 'm', 'b', 'l', 'n', 'm', 'l', 'k', 'v', 'a', 'b', 'u', 'i', 'o', 'a', 'i', 'i', 'i', 'r', 'e', 'l', 'r', 'i', 's', 'e', 'e', 'u', 'o', 'y', 'c', 't', 'n', 'l', 'n', 'a', 'd', 's', 't', 't', 'd', 'k', 't', 's', 'l', 'd', 'l', 'i', 'c', 'z', 'e', 'r', 'e', 'p', 'e', 'f', 'j', 'o', 'o', 'h', 'i', 'd', 'n', 'n', 'y', 'a', 'v', 'e', 'e', 'r', 'i', 'r', 'u', 'o', 'e', 'w'], 'p1': ['r', 'a', 'u', 'l', 'x', 'g', 'o'], 'p2': ['t', 'i', 'a', 'w', 'n', 'a', 'l']}, 'player1Name': 'david', 'player1Next': True, 'player2Name': 'gabriel', 'scores': [0, 0]}
last_time = pg.time.get_ticks()
start_waiting = None

points = {'a':1 , 'b':3, 'c':3, 'd':2, 'e':1, 'f':4, 'g':2, 'h':4, 'i':1, 'j':8, 'k':5, 'l':1, 'm':3, 'n':1, 'o':1, 'p':3, 'q':10, 'r':1, 's':1, 't':1, 'u':1, 'v':8, 'w':4, 'x':8, 'y':4, 'z':10}

input_box_width = 280
input_box_x = (width + 10 ) - (input_box_width)
input_box = pg.Rect(input_box_width, height//2, input_box_width, 40)




BOARD_MULT = 3

board_width = width//BOARD_MULT
piece_width = board_width//10

board_width = 10 * (piece_width)

#board_rect = pg.Rect((width - board_width)//2,(width - board_width)//2, board_width, board_width)
#board_rect = pg.Rect(50,50, board_width, board_width)
board_rect = pg.Rect(50,40, board_width, board_width)

rack_rect = pg.Rect(board_rect.left,board_rect.bottom+2*piece_width, 7*piece_width, piece_width)

test_rack = ['a','b','c','blank']

letters = list(ascii_uppercase.lower())
letters.append("blank")

imgs={}

input_guess = ""

for c in letters:
    imgs[c] = pg.transform.scale(pg.image.load("Images/Alphabet/"+str(c).upper()+"_letter_tile.png"),(piece_width, piece_width))

def try_entry(start,guess,direction):
    print("make guess")
    raise NotImplementedError

def update(game, events):
    # for dev

    global server_state
    global last_time
    global start_waiting
    global input_guess
    global drag
    now = pg.time.get_ticks()
    if now - last_time >= 1000 or server_state is None:
        last_time = now
        server_state = get_game(game.code)
        if server_state["cancelled"] != 0:
            game.end_state = server_state
            return "end"
        if game.isPlayer1 != server_state["player1Next"]:
            if start_waiting is None:
                start_waiting = pg.time.get_ticks()
            return
    # input
    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN and board_rect.collidepoint(event.pos):
            (x,y) = event.pos
            x = (x-board_rect.left)//piece_width
            y = (y-board_rect.top)//piece_width
            drag = (x,y)
        elif event.type == pg.MOUSEBUTTONUP and board_rect.collidepoint(event.pos):
            (x,y) = event.pos
            x = (x-board_rect.left)//piece_width
            y = (y-board_rect.top)//piece_width
            dx,dy = drag
            drag = None
            if x == dx and dy < y:
                try_entry(start=(x,y),guess=input_guess,direction="down")
            elif y == dy and dx < x:
                try_entry(start=(x,y),guess=input_guess,direction="right")
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                input_guess = input_guess[:-1]
            elif event.unicode and event.unicode.isprintable():
                input_guess += event.unicode


def draw_lines(screen):
    for x in range(board_rect.left,board_rect.right,board_rect.width//10):
        pg.draw.line(screen, BLACK, (x,board_rect.top), (x,board_rect.bottom))
    for y in range(board_rect.top,board_rect.bottom,board_rect.height//10):
        pg.draw.line(screen, BLACK,(board_rect.left,y),(board_rect.right,y))
    pg.draw.line(screen,BLACK, (rack_rect.left,rack_rect.top), (rack_rect.right,rack_rect.top))
    pg.draw.line(screen,BLACK, (rack_rect.left,rack_rect.bottom), (rack_rect.right,rack_rect.bottom))
    for x in range(rack_rect.left,rack_rect.right,piece_width):
        pg.draw.line(screen, BLACK, (x,rack_rect.top), (x,rack_rect.bottom))

def draw_rack(screen,game):
    y = rack_rect.top
    x = rack_rect.left
    if game.isPlayer1:
        rack = server_state["pieces"]["p1"]
    else:
        rack = server_state["pieces"]["p2"]
    for (count, img) in enumerate(rack):
        draw_piece(screen,(x+count*piece_width,y),img)

def draw_loading(screen, start):
    info = pg.display.Info()
    (width, height) = info.current_w, info.current_h

    all = pg.Surface((width, height))
    all.set_alpha(100)
    all.fill(WHITE)
    screen.blit(all, (0, 0))

    loading.get_rect().center = (width//2,height//2)
    diff = (pg.time.get_ticks() - start)/150
    new_image = pg.transform.rotate(loading.copy(), diff)
    new_image.get_rect().center = (width//2,height//2)
    screen.blit(new_image,(new_image.get_rect().left,new_image.get_rect().top))
    text = TITLE_FONT.render("Waiting for other player ...", True, BLACK)
    screen.blit(text,(0,0))

def draw(game, screen):
    pg.draw.rect(screen, (174, 207, 223), board_rect)
    pg.draw.rect(screen, (174, 207, 223), rack_rect)
    draw_lines(screen)
    draw_rack(screen,game)
    draw_board(screen)
    draw_scores(screen,game.isPlayer1)
    draw_input(screen)
    global start_waiting
    if start_waiting is not None:
        draw_loading(screen, start_waiting)

def draw_input(screen):
    global input_guess
    pg.draw.rect(screen, WHITE, input_box, 0)

    guess_surface = INPUT_FONT.render(input_guess, True, BLACK)
    screen.blit(guess_surface,
                (input_box.x + 5, input_box.y + (input_box.height - guess_surface.get_height()) // 2))

    #

def draw_scores(screen, isP1):
    n1 = ("You" if isP1 else server_state["player1Name"])+": "
    n2 = ("You: " if not isP1 else server_state["player2Name"])+": "
    text = FONT.render(n1 + str(server_state["scores"][0])+", "+n2 + str(server_state["scores"][1]), True, WHITE)
    screen.blit(text,(0,0))

def draw_board(screen):
    # do special pieces

    x,y = board_rect.topleft
    for row in server_state["board"]:
        x = board_rect.left
        for piece in row:
            if piece is not None:
                draw_piece(screen,(x,y),piece)
            x += piece_width
        y += piece_width

def draw_piece(screen, pos,letter):
    (x, y) = pos
    piece_rect = pg.Rect(x, y, piece_width, piece_width)
    pg.draw.rect(screen, "#b5e789", piece_rect)
    pg.draw.rect(screen, BLACK, piece_rect,width=1)
    if letter == "blank":
        return
    letter_text = BUTTON_FONT.render(letter.upper(), True, BLACK)
    point_text = NUMBER_FONT.render(str(points[letter]), True, BLACK)
    screen.blit(letter_text, (x+5, y))
    screen.blit(point_text, (x+piece_width//2, y+piece_width//2))

def init(game):
    global start_waiting
    start_waiting = None

functions = (update,draw,init)
