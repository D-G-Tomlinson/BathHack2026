import pygame as pg
import os

from backend_handler import new_game

# Palette
GOLD  = (229, 178,  93)
BROWN = (184, 125,  75)
SKY   = (174, 207, 223)
MAUVE = (176, 123, 172)
WHITE = (255, 255, 255)
BLACK = ( 30,  30,  30)
HOVER = BROWN

TITLE_FONT  = pg.font.SysFont("comicsansms", 64)
BUTTON_FONT = pg.font.SysFont("comicsansms", 36)
INPUT_FONT  = pg.font.SysFont("comicsansms", 36)
LABEL_FONT  = pg.font.SysFont("comicsansms", 36)

info = pg.display.Info()
width, height = info.current_w, info.current_h

title_text      = TITLE_FONT.render("Create New Game", True, MAUVE)
title_text_rect = title_text.get_rect(midtop=(width // 2, int(height * 0.06)))

username_label_text = LABEL_FONT.render("Username:", True, BLACK)

username_box_width = int(width * 0.28)
username_box_x     = (width - username_box_width) // 2
username_box_y     = int(height * 0.42)
username_box       = pg.Rect(username_box_x, username_box_y, username_box_width, int(height * 0.07))
username_label_rect = username_label_text.get_rect(midbottom=(width // 2, username_box_y - 8))

button_w    = int(width * 0.28)
button_h    = int(height * 0.09)
button_rect = pg.Rect((width - button_w) // 2, int(height * 0.65), button_w, button_h)
button_text = BUTTON_FONT.render("Generate Join Code", True, BLACK)
button_text_rect = button_text.get_rect(center=button_rect.center)

_IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "Images", "Colours")

def _load_cat(name, size):
    img = pg.image.load(os.path.join(_IMG_DIR, name)).convert_alpha()
    w, h = img.get_size()
    scale = size / max(w, h)
    return pg.transform.smoothscale(img, (int(w * scale), int(h * scale)))

_cat_size = int(height * 0.28)
_cats = [
    (_load_cat("Sleeping_tabby_cat.png", _cat_size), int(width * 0.08),  height - int(height * 0.12)),
    (_load_cat("White_cat.png",          _cat_size), int(width * 0.92),  height - int(height * 0.12)),
]

userid         = ""
username_active = True
cursor_visible  = False
cursor_time     = 0


def draw(game, screen):
    screen.fill(SKY)

    for img, cx, cy in _cats:
        screen.blit(img, img.get_rect(center=(cx, cy)))

    screen.blit(title_text, title_text_rect)
    screen.blit(username_label_text, username_label_rect)

    # Input box
    pg.draw.rect(screen, WHITE,  username_box, border_radius=8)
    pg.draw.rect(screen, BROWN,  username_box, 3, border_radius=8)

    username_surface = INPUT_FONT.render(userid, True, BLACK)
    screen.blit(username_surface,
                (username_box.x + 8,
                 username_box.y + (username_box.height - username_surface.get_height()) // 2))

    if username_active and cursor_visible:
        cursor_x = username_box.x + 8 + username_surface.get_width()
        pg.draw.line(screen, BLACK,
                     (cursor_x, username_box.y + 6),
                     (cursor_x, username_box.y + username_box.height - 6), 2)

    # Button
    col = HOVER if button_rect.collidepoint(pg.mouse.get_pos()) else GOLD
    pg.draw.rect(screen, col,   button_rect, border_radius=12)
    pg.draw.rect(screen, BROWN, button_rect, 3, border_radius=12)
    screen.blit(button_text, button_text_rect)


def update(game, events):
    global cursor_time, cursor_visible, username_active, userid

    current_time = pg.time.get_ticks()
    if current_time - cursor_time > 500:
        cursor_visible = not cursor_visible
        cursor_time = current_time

    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN:
            username_active = username_box.collidepoint(event.pos)
            if button_rect.collidepoint(event.pos) and userid.strip():
                code = new_game(userid)
                game.update(code, userid)
                game.isPlayer1 = True
                return "lobby"
        elif event.type == pg.KEYDOWN and username_active:
            if event.key == pg.K_BACKSPACE:
                userid = userid[:-1]
            elif event.key == pg.K_RETURN:
                code = new_game(userid)
                game.update(code, userid)
                game.isPlayer1 = True
                return "lobby"
            elif event.unicode and event.unicode.isprintable():
                userid += event.unicode


def init(game):
    global cursor_visible, cursor_time
    cursor_visible = False
    cursor_time = pg.time.get_ticks()


functions = (update, draw, init)
