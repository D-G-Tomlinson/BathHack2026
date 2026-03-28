import pygame
import random
import os

os.environ["SDL_RENDER_SCALE_QUALITY"] = "0"
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("CatWordle - Guess the cat word!")

W, H = screen.get_size()
BASE_W, BASE_H = 520, 870
_s  = min(W / BASE_W, H / BASE_H)
_ox = (W - int(BASE_W * _s)) // 2
_oy = (H - int(BASE_H * _s)) // 2

def sx(v): return int(v * _s)
def px(v): return _ox + int(v * _s)
def py(v): return _oy + int(v * _s)

GRID_COLS = 5
GRID_ROWS = 8

TILE_SIZE = sx(62)
TILE_GAP  = sx(8)
GRID_X    = (W - (GRID_COLS * (TILE_SIZE + TILE_GAP) - TILE_GAP)) // 2
GRID_Y    = py(110)

KEY_ROWS = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
]
KEY_SIZE    = sx(38)
KEY_GAP     = sx(6)
KEY_Y_START = GRID_Y + GRID_ROWS * (TILE_SIZE + TILE_GAP) + sx(20)

WHITE     = (255, 255, 255)
BLACK     = (20, 20, 20)
GREY_BG   = (174, 207, 223)
TILE_EMPTY = (255, 255, 255)
TILE_EDGE  = (184, 125, 75)
GREEN      = (130, 210, 100)
YELLOW     = (229, 178, 93)
DARK_GREY  = (184, 125, 75)
KEY_BG     = (176, 123, 172)
TEXT_DARK  = (30, 30, 30)
TEXT_LIGHT = (255, 255, 255)

CAT_WORDS = [
    "KITTY", "TABBY", "PURRS", "MEOWS", "TIGER",
    "FLUFF", "FURRY", "CLAWS", "PERCH", "PROWL",
    "CHIRP", "SNIFF", "GROOM", "BASKS", "DROOL",
    "HISSY", "TUFTS", "LAZES", "PATCH", "PAWED",
]

dic_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dic.txt")
with open(dic_path) as f:
    VALID_WORDS = {w.strip().upper() for w in f if len(w.strip()) == 5} | set(CAT_WORDS)

font_large = pygame.font.SysFont("Comic Sans MS", sx(32), bold=True)
font_tile  = pygame.font.SysFont("Comic Sans MS", sx(36), bold=True)
font_key   = pygame.font.SysFont("Comic Sans MS", sx(18), bold=True)
font_msg   = pygame.font.SysFont("Comic Sans MS", sx(26), bold=True)
font_title = pygame.font.SysFont("Comic Sans MS", sx(42), bold=True)

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Images")

def _cat(name, h):
    img = pygame.image.load(os.path.join(IMG_DIR, name)).convert_alpha()
    w = int(img.get_width() * h / img.get_height())
    return pygame.transform.smoothscale(img, (w, h))

# centred decoration above the instructions card
cat_deco     = _cat("Orange Cat.png",         sx(90))
cat_sleeping = _cat("Sleeping Tabby Cat.png", sx(85))
# side cats for the game screen margins
cat_grey_sm  = _cat("Grey cat.png",            sx(85))
cat_black_sm = _cat("Black cat.png",           sx(85))
# bottom row (3 cats fits the narrow layout)
cat_row = [
    _cat("Tabby cat.png",  sx(88)),
    _cat("Brown Cat.png",  sx(88)),
    _cat("White cat.png",  sx(88)),
]


def start_screen():
    btn_w, btn_h = sx(200), sx(55)
    btn_x = W // 2 - btn_w // 2
    btn_y = py(450)
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    while True:
        events = yield
        hovered = btn_rect.collidepoint(pygame.mouse.get_pos())

        for event in events:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered:
                    return True

        screen.fill(GREY_BG)

        # centred cat above the card
        screen.blit(cat_deco, (W // 2 - cat_deco.get_width() // 2, py(75)))
        # bottom row of cats
        for img, cx in zip(cat_row, [px(85), px(260), px(435)]):
            screen.blit(img, (cx - img.get_width() // 2, py(605)))

        # Title
        title = font_title.render("CatWordle!", True, BLACK)
        screen.blit(title, (W // 2 - title.get_width() // 2, py(22)))

        # Instructions card
        card_x, card_y, card_w, card_h = px(30), py(182), sx(460), sx(245)
        pygame.draw.rect(screen, TILE_EMPTY, (card_x, card_y, card_w, card_h), border_radius=sx(14))
        pygame.draw.rect(screen, TILE_EDGE,  (card_x, card_y, card_w, card_h), sx(2), border_radius=sx(14))

        lines = [
            "Guess the 5-letter cat word!",
            "You have 8 tries.",
            "Green = right letter, right spot.",
            "Yellow = right letter, wrong spot.",
            "Brown = letter not in the word.",
        ]
        for i, line in enumerate(lines):
            s = font_key.render(line, True, BLACK)
            screen.blit(s, (W // 2 - s.get_width() // 2, card_y + sx(24) + i * sx(40)))

        # Play button
        btn_col = GREEN if hovered else YELLOW
        pygame.draw.rect(screen, btn_col,    btn_rect, border_radius=sx(12))
        pygame.draw.rect(screen, TILE_EDGE,  btn_rect, sx(2), border_radius=sx(12))
        label = font_msg.render("PLAY", True, BLACK)
        screen.blit(label, (W // 2 - label.get_width() // 2, btn_y + btn_h // 2 - label.get_height() // 2))

        pygame.display.flip()


def end_screen(game):
    won = game["state"] == "won"
    cat_img = cat_deco if won else cat_sleeping

    btn_back = pygame.Rect(W // 2 - sx(77), py(480), sx(155), sx(52))

    while True:
        events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(event.pos):
                    return

        screen.fill(GREY_BG)
        if _ox > 40:
            screen.blit(cat_grey_sm,  (_ox // 2 - cat_grey_sm.get_width() // 2,  H // 2 - cat_grey_sm.get_height() // 2))
            screen.blit(cat_black_sm, (W - _ox // 2 - cat_black_sm.get_width() // 2, H // 2 - cat_black_sm.get_height() // 2))
        for img, cx in zip(cat_row, [px(85), px(260), px(435)]):
            screen.blit(img, (cx - img.get_width() // 2, py(620)))

        screen.blit(cat_img, (W // 2 - cat_img.get_width() // 2, py(72)))

        card_x, card_y, card_w, card_h = px(30), py(185), sx(460), sx(265)
        pygame.draw.rect(screen, TILE_EMPTY, (card_x, card_y, card_w, card_h), border_radius=sx(14))
        pygame.draw.rect(screen, TILE_EDGE,  (card_x, card_y, card_w, card_h), sx(2), border_radius=sx(14))

        msg_col = GREEN if won else (180, 60, 60)
        for f in (font_large, font_msg, font_key):
            t = f.render(game["message"], True, msg_col)
            if t.get_width() <= card_w - sx(20):
                break
        screen.blit(t, (W // 2 - t.get_width() // 2, card_y + sx(28)))

        for i, line in enumerate([
            f"Guesses used: {len(game['guesses'])} / {GRID_ROWS}",
            game["hint"],
        ]):
            s = font_key.render(line, True, BLACK)
            screen.blit(s, (W // 2 - s.get_width() // 2, card_y + sx(105) + i * sx(48)))

        bk_col = YELLOW if btn_back.collidepoint(pygame.mouse.get_pos()) else TILE_EMPTY
        pygame.draw.rect(screen, bk_col,    btn_back, border_radius=sx(12))
        pygame.draw.rect(screen, TILE_EDGE, btn_back, sx(2), border_radius=sx(12))
        screen.blit(font_msg.render("Back", True, BLACK), font_msg.render("Back", True, BLACK).get_rect(center=btn_back.center))

        pygame.display.flip()


def new_game():
    word = random.choice(CAT_WORDS)
    return {
        "word": word,
        "guesses": [],
        "current": "",
        "state": "playing",
        "message": "",
        "key_colours": {},
        "hint": f"Hint: it starts with {word[0]}!",
    }


def score_guess(guess, word):
    result = [None] * 5
    remaining = list(word)

    for i, (g, w) in enumerate(zip(guess, word)):
        if g == w:
            result[i] = (g, GREEN)
            remaining[i] = None

    for i, (g, _) in enumerate(zip(guess, word)):
        if result[i] is not None:
            continue
        if g in remaining:
            result[i] = (g, YELLOW)
            remaining[remaining.index(g)] = None
        else:
            result[i] = (g, DARK_GREY)

    return result


def draw_tile(surface, letter, colour_bg, x, y, size=None, border=TILE_EDGE, reveal=True):
    if size is None:
        size = TILE_SIZE
    rect = pygame.Rect(x, y, size, size)
    if reveal and colour_bg not in (TILE_EMPTY, None):
        pygame.draw.rect(surface, colour_bg, rect, border_radius=sx(6))
    else:
        pygame.draw.rect(surface, TILE_EMPTY, rect, border_radius=sx(6))
        pygame.draw.rect(surface, border, rect, sx(3), border_radius=sx(6))

    if letter:
        text_colour = TEXT_LIGHT if (reveal and colour_bg == DARK_GREY) else TEXT_DARK
        surf = font_tile.render(letter, True, text_colour)
        surface.blit(surf, surf.get_rect(center=rect.center))


def draw_grid(surface, game):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = GRID_X + col * (TILE_SIZE + TILE_GAP)
            y = GRID_Y + row * (TILE_SIZE + TILE_GAP)

            if row < len(game["guesses"]):
                scored = score_guess(game["guesses"][row], game["word"])
                letter, colour = scored[col]
                draw_tile(surface, letter, colour, x, y)
            elif row == len(game["guesses"]) and game["state"] == "playing":
                letter = game["current"][col] if col < len(game["current"]) else ""
                draw_tile(surface, letter, TILE_EMPTY, x, y, reveal=False)
            else:
                draw_tile(surface, "", TILE_EMPTY, x, y, reveal=False)


def draw_keyboard(surface, game):
    for row_idx, row_keys in enumerate(KEY_ROWS):
        total_w = len(row_keys) * (KEY_SIZE + KEY_GAP) - KEY_GAP
        start_x = (W - total_w) // 2
        y = KEY_Y_START + row_idx * (KEY_SIZE + KEY_GAP)

        for ki, key in enumerate(row_keys):
            x = start_x + ki * (KEY_SIZE + KEY_GAP)
            rect = pygame.Rect(x, y, KEY_SIZE, KEY_SIZE)
            colour = game["key_colours"].get(key, KEY_BG)
            pygame.draw.rect(surface, colour, rect, border_radius=sx(5))
            text_colour = TEXT_LIGHT if colour in (DARK_GREY, KEY_BG) else TEXT_DARK
            surf = font_key.render(key, True, text_colour)
            surface.blit(surf, surf.get_rect(center=rect.center))


def update_key_colours(game, scored):
    for letter, colour in scored:
        current = game["key_colours"].get(letter)
        if current != GREEN and (current != YELLOW or colour == GREEN):
            game["key_colours"][letter] = colour


def handle_key(game, key_name):
    if game["state"] != "playing":
        return

    if key_name == "BACKSPACE":
        game["current"] = game["current"][:-1]
    elif key_name == "RETURN" or key_name == "KP_ENTER":
        if len(game["current"]) == 5:
            guess = game["current"]
            if guess not in VALID_WORDS:
                game["message"] = "Not in word list!"
                return
            scored = score_guess(guess, game["word"])
            update_key_colours(game, scored)
            game["guesses"].append(guess)
            game["current"] = ""

            if guess == game["word"]:
                game["state"] = "won"
                game["message"] = random.choice([
                    "Purrfect! You're a cat genius!",
                    "Meow-velous! You got it!",
                    "You're the cat's whiskers!",
                    "Paw-some job! Well done!",
                    "Fur-bulous! You nailed it!",
                ])
            elif len(game["guesses"]) >= GRID_ROWS:
                game["state"] = "lost"
                game["message"] = f"It was {game['word']}! Hiss! Try again!"
        else:
            game["message"] = "Meow! Need 5 letters!"
    elif len(key_name) == 1 and key_name.isalpha() and len(game["current"]) < 5:
        game["current"] += key_name.upper()
        game["message"] = ""


def draw(surface, game):
    surface.fill(GREY_BG)

    # side cats in screen margins
    if _ox > 40:
        surface.blit(cat_grey_sm,  (_ox // 2 - cat_grey_sm.get_width() // 2,  H // 2 - cat_grey_sm.get_height() // 2))
        surface.blit(cat_black_sm, (W - _ox // 2 - cat_black_sm.get_width() // 2, H // 2 - cat_black_sm.get_height() // 2))

    title = font_title.render("CatWordle", True, BLACK)
    surface.blit(title, title.get_rect(centerx=W // 2, y=py(14)))

    hint_surf = font_msg.render(game["hint"], True, BLACK)
    surface.blit(hint_surf, hint_surf.get_rect(centerx=W // 2, y=py(68)))

    draw_grid(surface, game)
    draw_keyboard(surface, game)

    if game["message"]:
        msg_surf = font_msg.render(game["message"], True, BLACK)
        surface.blit(msg_surf, msg_surf.get_rect(centerx=W // 2, y=H - sx(50)))

    pygame.display.flip()


def run_gen(scr, clk=None):
    global screen, clock
    screen = scr
    clock = clk or pygame.time.Clock()
    if not (yield from start_screen()):
        return
    game = new_game()
    end_timer = 0

    while True:
        events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                handle_key(game, pygame.key.name(event.key).upper())
        draw(screen, game)
        if game["state"] != "playing":
            end_timer += 1
            if end_timer >= 90:
                yield from end_screen(game)
                return


if __name__ == "__main__":
    clock = pygame.time.Clock()
    gen = run_gen(screen, clock)
    next(gen)
    while True:
        try:
            gen.send(pygame.event.get())
        except StopIteration:
            break
        clock.tick(60)
    pygame.quit()
