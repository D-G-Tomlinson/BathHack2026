import pygame as pg
from string import ascii_uppercase
import math
import os
import json
import random

from backend_handler import get_game, make_move

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HOVER = (200, 200, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Palette
GOLD  = (229, 178,  93)
BROWN = (184, 125,  75)
SKY   = (174, 207, 223)
MAUVE = (176, 123, 172)

NUMBER_FONT = pg.font.SysFont("comicsansms", 12)

NUMBER_FONT2= pg.font.SysFont("comicsansms", 11)
FONT        = pg.font.SysFont("comicsansms", 44)
BUTTON_FONT = pg.font.SysFont("comicsansms", 26)
INPUT_FONT  = pg.font.SysFont("comicsansms", 30)
TITLE_FONT  = pg.font.SysFont("comicsansms", 64)
SCORE_FONT  = pg.font.SysFont("comicsansms", 36)
LABEL_FONT  = pg.font.SysFont("comicsansms", 26)
WAIT_FONT   = pg.font.SysFont("comicsansms", 52)
WAIT_SUB    = pg.font.SysFont("comicsansms", 30)

info = pg.display.Info()
(width, height) = info.current_w, info.current_h

drag = None
selected_cell   = None   # (col, row) clicked on board
place_direction = "H"    # "H" or "V"
play_error      = ""
play_error_time = 0

# button rects set each frame by draw_sidebar so update() can hit-test them
_btn_h_rect    = None
_btn_v_rect    = None
_btn_play_rect = None

# ── circular-cropped waiting cat ──────────────────────────────────────
_IMG_DIR   = os.path.join(os.path.dirname(__file__), "..", "Images", "Colours")
_WAIT_R    = int(height * 0.14)
_WAIT_D    = _WAIT_R * 2
_WAIT_SPIN = _WAIT_R + int(height * 0.05)
_WAIT_NDOT = 10
_WAIT_DMAX = int(height * 0.013)

def _make_circle_cat(path, d):
    raw  = pg.image.load(path).convert_alpha()
    cat  = pg.transform.smoothscale(raw, (d, d))
    mask = pg.Surface((d, d), pg.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pg.draw.circle(mask, (255, 255, 255, 255), (d // 2, d // 2), d // 2)
    cat.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return cat

_wait_cat = _make_circle_cat(os.path.join(_IMG_DIR, "Grey_cat.png"), _WAIT_D)

# small sidebar cat
_side_cat_size = int(height * 0.18)
def _load_cat(name, size):
    img = pg.image.load(os.path.join(_IMG_DIR, name)).convert_alpha()
    w, h = img.get_size()
    scale = size / max(w, h)
    return pg.transform.smoothscale(img, (int(w * scale), int(h * scale)))
_side_cat = _load_cat("Tabby_cat.png", _side_cat_size)

def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def _draw_card(screen, rect, fill=WHITE, border=GOLD, radius=14, border_w=4):
    pg.draw.rect(screen, fill,   rect, border_radius=radius)
    pg.draw.rect(screen, border, rect, border_w, border_radius=radius)

cat_squares: frozenset = frozenset()   # (row, col) pairs; set in init() from game.code seed
_board_screen = None                   # captured each frame in draw() for minigame use

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

# small cat icon drawn on empty cat squares on the board (piece_width now defined)
_cat_cell_img = pg.transform.smoothscale(
    pg.image.load(os.path.join(_IMG_DIR, "Grey_cat.png")).convert_alpha(),
    (piece_width, piece_width)
)

# orange cat for the center 4 starting squares
_center_cat_img = pg.transform.smoothscale(
    pg.image.load(os.path.join(_IMG_DIR, "Orange_cat.png")).convert_alpha(),
    (piece_width, piece_width)
)
CENTER_SQUARES = frozenset([(4, 4), (4, 5), (5, 4), (5, 5)])

# (module_name, multiplier) — order determines random selection
MINIGAME_LIST = [
    ("KaraokeMiniGame",    2),
    ("WordleMiniGame",     3),
    ("SpellingMiniGame",   4),
    ("MathsMiniGame",      5),
    ("ConnectionsMiniGame",6),
]


def _pick_minigame():
    """Return a random (module_name, multiplier) pair."""
    return random.choice(MINIGAME_LIST)


def _run_specific_minigame(screen, module_name):
    """Run the named minigame module via its run_gen generator until it exits."""
    import sys, importlib
    _client_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _client_dir not in sys.path:
        sys.path.insert(0, _client_dir)
    mod = importlib.import_module(module_name)
    clock = pg.time.Clock()
    gen = mod.run_gen(screen, clock)
    try:
        next(gen)
    except StopIteration:
        return
    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                return
        try:
            gen.send(events)
        except StopIteration:
            break
        clock.tick(60)
        pg.display.flip()


def _place_word(word, col, row, direction, is_p1):
    """Validate and apply a word placement. Returns (new_board, new_rack, new_bag, new_score) or raises ValueError."""
    board = [list(r) for r in server_state["board"]]
    rack  = list(server_state["pieces"]["p1" if is_p1 else "p2"])
    bag   = list(server_state["pieces"]["bag"])
    score = server_state["scores"][0 if is_p1 else 1]
    word  = word.lower().strip()

    if not word:
        raise ValueError("No word typed!")

    dc, dr = (1, 0) if direction == "H" else (0, 1)
    c, r   = col, row

    for letter in word:
        if not (0 <= c < 10 and 0 <= r < 10):
            raise ValueError("Word goes off the board!")
        existing = board[r][c]
        if existing is None:
            if letter not in rack:
                raise ValueError(f"You don't have the tile '{letter.upper()}'!")
            rack.remove(letter)
            board[r][c] = letter
            score += points.get(letter, 0)
        elif existing != letter:
            raise ValueError(f"Conflicts with existing tile '{existing.upper()}' at ({c},{r})!")
        c += dc
        r += dr

    # draw new tiles from bag
    needed = 7 - len(rack)
    rack  += bag[:needed]
    bag    = bag[needed:]
    return board, rack, bag, score


def _do_play(game):
    global input_guess, selected_cell, play_error, play_error_time
    if not selected_cell:
        play_error = "Click a start cell first!"
        play_error_time = pg.time.get_ticks()
        return
    if not input_guess.strip():
        play_error = "Type a word first!"
        play_error_time = pg.time.get_ticks()
        return
    try:
        col, row = selected_cell
        # Check which new tiles would land on a cat square before placing
        word = input_guess.lower().strip()
        dc, dr = (1, 0) if place_direction == "H" else (0, 1)
        c, r = col, row
        hit_cat = False
        for _ in word:
            if 0 <= c < 10 and 0 <= r < 10:
                if server_state["board"][r][c] is None and (r, c) in cat_squares:
                    hit_cat = True
            c += dc
            r += dr

        # Pre-select minigame so multiplier can be applied before pushing score
        if hit_cat:
            minigame_name, multiplier = _pick_minigame()
        else:
            multiplier = 1

        old_score = server_state["scores"][0 if game.isPlayer1 else 1]
        new_board, new_rack, new_bag, new_score = _place_word(
            input_guess, col, row, place_direction, game.isPlayer1)
        word_points = new_score - old_score
        final_score = old_score + word_points * multiplier

        make_move(game.code, game.userid,
                  json.dumps(new_board), json.dumps(new_rack), json.dumps(new_bag), final_score)
        # Update local state immediately so the rack redraws without waiting for the next poll
        rack_key = "p1" if game.isPlayer1 else "p2"
        score_idx = 0 if game.isPlayer1 else 1
        server_state["board"] = new_board
        server_state["pieces"][rack_key] = new_rack
        server_state["pieces"]["bag"]    = new_bag
        server_state["scores"][score_idx] = final_score
        input_guess   = ""
        selected_cell = None
        play_error    = ""

        if hit_cat and _board_screen is not None:
            _run_specific_minigame(_board_screen, minigame_name)
    except ValueError as e:
        play_error      = str(e)
        play_error_time = pg.time.get_ticks()
    except Exception as e:
        play_error      = f"Error: {e}"
        play_error_time = pg.time.get_ticks()


def update(game, events):
    global server_state, last_time, start_waiting
    global input_guess, drag, selected_cell, place_direction
    global play_error, play_error_time
    global _btn_h_rect, _btn_v_rect, _btn_play_rect

    now = pg.time.get_ticks()
    if now - last_time >= 1000 or server_state is None:
        last_time = now
        try:
            server_state = get_game(game.code)
            # Server may store board/rack/bag as JSON strings — normalise to lists
            if isinstance(server_state.get("board"), str):
                server_state["board"] = json.loads(server_state["board"])
            pieces = server_state.get("pieces", {})
            for key in ("p1", "p2", "bag"):
                if isinstance(pieces.get(key), str):
                    pieces[key] = json.loads(pieces[key])
        except Exception:
            return   # keep showing last known state if network blips
        if server_state["cancelled"] != 0:
            game.end_state = server_state
            return "end"
        if game.isPlayer1 != server_state["player1Next"]:
            if start_waiting is None:
                start_waiting = pg.time.get_ticks()
            return
        else:
            start_waiting = None   # it's our turn again — hide overlay

    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN:
            pos = event.pos
            # board cell click → select start
            if board_rect.collidepoint(pos):
                x = (pos[0] - board_rect.left) // piece_width
                y = (pos[1] - board_rect.top)  // piece_width
                selected_cell = (x, y)
            # direction buttons
            elif _btn_h_rect and _btn_h_rect.collidepoint(pos):
                place_direction = "H"
            elif _btn_v_rect and _btn_v_rect.collidepoint(pos):
                place_direction = "V"
            # play button
            elif _btn_play_rect and _btn_play_rect.collidepoint(pos):
                _do_play(game)

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                input_guess = input_guess[:-1]
            elif event.key == pg.K_RETURN:
                _do_play(game)
            elif event.unicode and event.unicode.isalpha():
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

def draw_rack(screen, game):
    y = rack_rect.top
    x = rack_rect.left
    rack = server_state["pieces"]["p1"] if game.isPlayer1 else server_state["pieces"]["p2"]
    for count, img in enumerate(rack):
        draw_piece(screen, (x + count * piece_width, y), img)

def draw_loading(screen, start):
    t   = pg.time.get_ticks()
    cx  = width  // 2
    cy  = height // 2

    # semi-transparent SKY overlay
    overlay = pg.Surface((width, height), pg.SRCALPHA)
    overlay.fill((*SKY, 210))
    screen.blit(overlay, (0, 0))

    # card behind everything
    card_w, card_h = int(width * 0.44), int(height * 0.58)
    card = pg.Rect(0, 0, card_w, card_h)
    card.center = (cx, cy)
    pg.draw.rect(screen, WHITE, card, border_radius=24)
    pg.draw.rect(screen, GOLD,  card, 5, border_radius=24)

    # spinner ring
    angle_off = (t / 900.0) * math.tau
    for i in range(_WAIT_NDOT):
        frac   = (i + 1) / _WAIT_NDOT
        fade   = frac ** 1.6
        angle  = angle_off + math.tau * i / _WAIT_NDOT
        dx     = math.cos(angle) * _WAIT_SPIN
        dy     = math.sin(angle) * _WAIT_SPIN
        colour = _lerp_color(WHITE, MAUVE, fade)
        r      = max(3, int(_WAIT_DMAX * (0.35 + 0.65 * fade)))
        pg.draw.circle(screen, colour, (int(cx + dx), int(cy + int(height*0.04) + dy)), r)

    # cat circle border
    cat_cy = cy + int(height * 0.04)
    pg.draw.circle(screen, GOLD,  (cx, cat_cy), _WAIT_R + 5)
    pg.draw.circle(screen, BROWN, (cx, cat_cy), _WAIT_R + 5, 3)

    # bouncing cat
    bob = math.sin(t / 500.0) * int(height * 0.010)
    rect = _wait_cat.get_rect(center=(cx, int(cat_cy + bob)))
    screen.blit(_wait_cat, rect)

    # title
    title = WAIT_FONT.render("Opponent's turn!", True, MAUVE)
    screen.blit(title, title.get_rect(midtop=(cx, card.top + 22)))

    # animated dots
    dot_count = int((t / 500) % 4)
    dots = WAIT_SUB.render("Waiting" + "." * dot_count + " " * (3 - dot_count), True, BROWN)
    screen.blit(dots, dots.get_rect(midbottom=(cx, card.bottom - 22)))

def draw(game, screen):
    global _board_screen
    _board_screen = screen
    if server_state is None:
        screen.fill(SKY)
        return

    # sky background
    screen.fill(SKY)

    # board background card
    board_card = board_rect.inflate(16, 16)
    _draw_card(screen, board_card, fill=GOLD, border=BROWN, radius=10)

    pg.draw.rect(screen, SKY, board_rect)
    draw_lines(screen)
    draw_board(screen)

    # rack card
    rack_card = rack_rect.inflate(16, 14)
    _draw_card(screen, rack_card, fill=GOLD, border=BROWN, radius=10)
    draw_rack(screen, game)

    draw_sidebar(screen, game)

    global start_waiting
    if start_waiting is not None:
        draw_loading(screen, start_waiting)


def draw_sidebar(screen, game):
    global _btn_h_rect, _btn_v_rect, _btn_play_rect

    panel_x  = board_rect.right + 40
    panel_w  = width - panel_x - 30
    panel_cx = panel_x + panel_w // 2
    y        = 40

    # ── score cards ───────────────────────────────────────────────────
    p1_name    = "You" if game.isPlayer1 else (server_state["player1Name"] or "Player 1")
    p2_name    = "You" if not game.isPlayer1 else (server_state["player2Name"] or "Player 2")
    scores     = server_state["scores"]
    is_p1_turn = server_state["player1Next"]
    my_turn    = (game.isPlayer1 == is_p1_turn)

    card_h = int(height * 0.12)
    for i, (name, score) in enumerate([(p1_name, scores[0]), (p2_name, scores[1])]):
        card = pg.Rect(panel_x, y, panel_w, card_h)
        active  = (i == 0 and is_p1_turn) or (i == 1 and not is_p1_turn)
        fill    = MAUVE if active else WHITE
        border  = BROWN if active else GOLD
        tc      = WHITE if active else BLACK
        _draw_card(screen, card, fill=fill, border=border)
        screen.blit(SCORE_FONT.render(name, True, tc),
                    SCORE_FONT.render(name, True, tc).get_rect(topleft=(card.x+14, card.y+8)))
        sc = TITLE_FONT.render(str(score), True, tc)
        screen.blit(sc, sc.get_rect(bottomright=(card.right-14, card.bottom-6)))
        y += card_h + 14

    # ── turn label ────────────────────────────────────────────────────
    y += 6
    turn_surf = SCORE_FONT.render("Your turn!" if my_turn else "Opponent's turn...",
                                  True, BROWN if my_turn else MAUVE)
    screen.blit(turn_surf, turn_surf.get_rect(midtop=(panel_cx, y)))
    y += turn_surf.get_height() + 28

    if not my_turn:
        # nothing interactive to show
        screen.blit(_side_cat, _side_cat.get_rect(midbottom=(panel_cx, height - int(height*0.05))))
        return

    # ── word input ────────────────────────────────────────────────────
    screen.blit(LABEL_FONT.render("Your word:", True, BROWN),
                LABEL_FONT.render("Your word:", True, BROWN).get_rect(midtop=(panel_cx, y)))
    y += LABEL_FONT.size("A")[1] + 6
    inp_rect = pg.Rect(panel_x, y, panel_w, int(height * 0.062))
    _error_active = bool(play_error and pg.time.get_ticks() - play_error_time < 1500)
    _draw_card(screen, inp_rect, fill=(255, 235, 235) if _error_active else WHITE,
               border=(220, 60, 60) if _error_active else BROWN)
    gs = INPUT_FONT.render(input_guess or "start typing...", True,
                           BLACK if input_guess else (180, 180, 180))
    screen.blit(gs, gs.get_rect(midleft=(inp_rect.x + 12, inp_rect.centery)))
    y += inp_rect.height + 20

    # ── start cell ────────────────────────────────────────────────────
    cell_lbl = f"Start cell: ({selected_cell[0]},{selected_cell[1]})" if selected_cell else "Click board to pick start"
    cell_col = BLACK if selected_cell else (150, 150, 150)
    cs = LABEL_FONT.render(cell_lbl, True, cell_col)
    screen.blit(cs, cs.get_rect(midtop=(panel_cx, y)))
    y += cs.get_height() + 16

    # ── H / V direction buttons ───────────────────────────────────────
    btn_w = int(panel_w * 0.42)
    btn_h = int(height * 0.058)
    _btn_h_rect = pg.Rect(panel_x, y, btn_w, btn_h)
    _btn_v_rect = pg.Rect(panel_x + panel_w - btn_w, y, btn_w, btn_h)
    for rect, label, active in ((_btn_h_rect, "Across", place_direction == "H"),
                                 (_btn_v_rect, "Down",   place_direction == "V")):
        _draw_card(screen, rect,
                   fill=GOLD if active else WHITE,
                   border=BROWN, radius=10)
        ls = LABEL_FONT.render(label, True, BLACK)
        screen.blit(ls, ls.get_rect(center=rect.center))
    y += btn_h + 20

    # ── play button ───────────────────────────────────────────────────
    _btn_play_rect = pg.Rect(panel_x, y, panel_w, int(height * 0.075))
    ready = bool(input_guess.strip() and selected_cell)
    _draw_card(screen, _btn_play_rect,
               fill=MAUVE if ready else (200, 200, 200),
               border=BROWN, radius=12)
    ps = SCORE_FONT.render("Play Word", True, WHITE if ready else (130, 130, 130))
    screen.blit(ps, ps.get_rect(center=_btn_play_rect.center))
    y += _btn_play_rect.height + 14

    # ── hint ──────────────────────────────────────────────────────────
    screen.blit(LABEL_FONT.render("Enter also submits", True, (160, 160, 160)),
                LABEL_FONT.render("Enter also submits", True, (160, 160, 160)).get_rect(midtop=(panel_cx, y)))

    # ── deco cat ──────────────────────────────────────────────────────
    screen.blit(_side_cat, _side_cat.get_rect(midbottom=(panel_cx, height - int(height*0.05))))


def draw_input(screen):
    pass   # handled inside draw_sidebar


def draw_scores(screen, isP1):
    pass   # handled inside draw_sidebar

def draw_board(screen):
    x, y = board_rect.topleft
    for ri, row in enumerate(server_state["board"]):
        x = board_rect.left
        for ci, piece in enumerate(row):
            if piece is not None:
                draw_piece(screen, (x, y), piece)
            elif selected_cell == (ci, ri):
                # highlight selected start cell
                pg.draw.rect(screen, GOLD, pg.Rect(x, y, piece_width, piece_width))
                pg.draw.rect(screen, BROWN, pg.Rect(x, y, piece_width, piece_width), 2)
            elif (ri, ci) in CENTER_SQUARES:
                screen.blit(_center_cat_img, (x, y))
            elif (ri, ci) in cat_squares:
                screen.blit(_cat_cell_img, (x, y))
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
    global start_waiting, selected_cell, input_guess, play_error, server_state, cat_squares
    start_waiting = None
    selected_cell = None
    input_guess   = ""
    play_error    = ""
    server_state  = None   # force a fresh fetch on entry
    # Deterministic permutation from game code: 10 cats, unique row AND col
    rng = random.Random(game.code)
    cols = list(range(10))
    rng.shuffle(cols)
    cat_squares = frozenset((row, cols[row]) for row in range(10))

functions = (update,draw,init)
