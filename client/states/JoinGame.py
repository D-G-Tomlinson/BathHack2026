import pygame as pg
import os

from backend_handler import join_game

# Palette
GOLD  = (229, 178,  93)
BROWN = (184, 125,  75)
SKY   = (174, 207, 223)
MAUVE = (176, 123, 172)
WHITE = (255, 255, 255)
BLACK = ( 30,  30,  30)
RED   = (200,  50,  50)
HOVER = BROWN

TITLE_FONT  = pg.font.SysFont("comicsansms", 64)
BUTTON_FONT = pg.font.SysFont("comicsansms", 36)
INPUT_FONT  = pg.font.SysFont("comicsansms", 36)
LABEL_FONT  = pg.font.SysFont("comicsansms", 36)
ERROR_FONT  = pg.font.SysFont("comicsansms", 30)

info = pg.display.Info()
width, height = info.current_w, info.current_h

title_text = TITLE_FONT.render("Join Game", True, MAUVE)
title_rect = title_text.get_rect(midtop=(width // 2, int(height * 0.06)))

BOX_WIDTH  = int(width * 0.28)
BOX_HEIGHT = int(height * 0.07)
BOX_X      = (width - BOX_WIDTH) // 2

username_box   = pg.Rect(BOX_X, int(height * 0.35), BOX_WIDTH, BOX_HEIGHT)
game_code_box  = pg.Rect(BOX_X, int(height * 0.52), BOX_WIDTH, BOX_HEIGHT)

username_label_text  = LABEL_FONT.render("Username:", True, BLACK)
username_label_rect  = username_label_text.get_rect(midbottom=(width // 2, username_box.y - 8))
game_code_label_text = LABEL_FONT.render("Game code:", True, BLACK)
game_code_label_rect = game_code_label_text.get_rect(midbottom=(width // 2, game_code_box.y - 8))

button_w    = int(width * 0.18)
button_h    = int(height * 0.09)
button_rect = pg.Rect((width - button_w) // 2, int(height * 0.70), button_w, button_h)
button_text = BUTTON_FONT.render("Join", True, BLACK)
button_text_rect = button_text.get_rect(center=button_rect.center)

_IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "Images", "Colours")

def _load_cat(name, size):
    img = pg.image.load(os.path.join(_IMG_DIR, name)).convert_alpha()
    w, h = img.get_size()
    scale = size / max(w, h)
    return pg.transform.smoothscale(img, (int(w * scale), int(h * scale)))

_cat_size = int(height * 0.28)
_cats = [
    (_load_cat("Black_cat.png",      _cat_size), int(width * 0.08),  height - int(height * 0.12)),
    (_load_cat("Light_grey_cat.png", _cat_size), int(width * 0.92),  height - int(height * 0.12)),
]

game_code_text = ""
error_message  = ""

NONE     = 0
USERNAME = 1
CODE     = 2
active = NONE

cursor_visible = False
cursor_time    = 0


def draw(game, screen):
    screen.fill(SKY)

    for img, cx, cy in _cats:
        screen.blit(img, img.get_rect(center=(cx, cy)))

    screen.blit(title_text, title_rect)
    screen.blit(username_label_text,  username_label_rect)
    screen.blit(game_code_label_text, game_code_label_rect)

    # Input boxes
    for box in (username_box, game_code_box):
        pg.draw.rect(screen, WHITE, box, border_radius=8)
        pg.draw.rect(screen, BROWN, box, 3, border_radius=8)

    username_surface = INPUT_FONT.render(game.userid, True, BLACK)
    screen.blit(username_surface,
                (username_box.x + 8,
                 username_box.y + (username_box.height - username_surface.get_height()) // 2))

    game_code_surface = INPUT_FONT.render(game_code_text, True, BLACK)
    screen.blit(game_code_surface,
                (game_code_box.x + 8,
                 game_code_box.y + (game_code_box.height - game_code_surface.get_height()) // 2))

    # Cursor
    if active != NONE and cursor_visible:
        if active == USERNAME:
            cx = username_box.x + 8 + username_surface.get_width()
            cy = username_box.y
            ch = username_box.height
        else:
            cx = game_code_box.x + 8 + game_code_surface.get_width()
            cy = game_code_box.y
            ch = game_code_box.height
        pg.draw.line(screen, BLACK, (cx, cy + 6), (cx, cy + ch - 6), 2)

    # Button
    col = HOVER if button_rect.collidepoint(pg.mouse.get_pos()) else GOLD
    pg.draw.rect(screen, col,   button_rect, border_radius=12)
    pg.draw.rect(screen, BROWN, button_rect, 3, border_radius=12)
    screen.blit(button_text, button_text_rect)

    # Error message
    if error_message:
        err_surf = ERROR_FONT.render(error_message, True, RED)
        screen.blit(err_surf, ((width - err_surf.get_width()) // 2,
                                height - err_surf.get_height() - int(height * 0.03)))


def update(game, events):
    global cursor_time, cursor_visible, active, game_code_text, error_message

    current_time = pg.time.get_ticks()
    if current_time - cursor_time > 500:
        cursor_visible = not cursor_visible
        cursor_time = current_time

    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN:
            if username_box.collidepoint(event.pos):
                active = USERNAME
            elif game_code_box.collidepoint(event.pos):
                active = CODE
            else:
                active = NONE

            if button_rect.collidepoint(event.pos) and game.userid.strip() and len(game_code_text) == 6:
                join_game(game_code_text, game.userid)
                game.isPlayer1 = False
                game.code = game_code_text
                return "board"

        elif event.type == pg.KEYDOWN:
            if active == USERNAME:
                if event.key == pg.K_BACKSPACE:
                    game.userid = game.userid[:-1]
                elif event.key == pg.K_TAB:
                    active = CODE
                elif event.unicode and event.unicode.isprintable():
                    game.userid += event.unicode
            elif active == CODE:
                if event.key == pg.K_BACKSPACE:
                    game_code_text = game_code_text[:-1]
                elif event.key == pg.K_TAB:
                    active = USERNAME
                elif event.key == pg.K_RETURN and game.userid.strip() and len(game_code_text) == 6:
                    join_game(game_code_text, game.userid)
                    game.isPlayer1 = False
                    game.code = game_code_text
                    return "board"
                elif event.unicode and event.unicode.isdigit() and len(game_code_text) < 6:
                    game_code_text += event.unicode

    return "join_game"


def init(game):
    global cursor_visible, cursor_time
    cursor_visible = False
    cursor_time = pg.time.get_ticks()
    game.userid = ""
    game.code = ""


functions = (update, draw, init)
