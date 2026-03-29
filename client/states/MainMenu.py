import pygame as pg
import os

# Palette
GOLD  = (229, 178,  93)   # E5B25D
BROWN = (184, 125,  75)   # B87D4B
SKY   = (174, 207, 223)   # AECFDF
MAUVE = (176, 123, 172)   # B07BAC
GREEN = (181, 231, 137)   # B5E789
WHITE = (255, 255, 255)
BLACK = ( 30,  30,  30)

FONT = pg.font.SysFont("comicsansms", 48)

info = pg.display.Info()
width, height = info.current_w, info.current_h

new_text = FONT.render("New Game", True, BLACK)
join_text = FONT.render("Join Game", True, BLACK)

_btn_h      = new_text.get_height() + 16   # padded button height
_btn_gap    = 20                            # gap between buttons
_btn_block  = _btn_h * 2 + _btn_gap
_btn_top    = (height - _btn_block) // 2 + int(height * 0.18)

new_rect  = new_text.get_rect(midtop=(width // 2, _btn_top))
join_rect = join_text.get_rect(midtop=(width // 2, _btn_top + _btn_h + _btn_gap))

_IMG_DIR  = os.path.join(os.path.dirname(__file__), "..", "Images", "Colours")
_LOGO_DIR = os.path.join(os.path.dirname(__file__), "..", "Images")

def _load_cat(name, size):
    img = pg.image.load(os.path.join(_IMG_DIR, name)).convert_alpha()
    orig_w, orig_h = img.get_size()
    scale = size / max(orig_w, orig_h)
    return pg.transform.smoothscale(img, (int(orig_w * scale), int(orig_h * scale)))

def _load_logo(max_w, max_h):
    img = pg.image.load(os.path.join(_LOGO_DIR, "Scrabblekittens_logo_transparent.png")).convert_alpha()
    orig_w, orig_h = img.get_size()
    scale = min(max_w / orig_w, max_h / orig_h)
    return pg.transform.smoothscale(img, (int(orig_w * scale), int(orig_h * scale)))

_logo      = _load_logo(int(width * 0.75), int(height * 0.45))
_logo_rect = _logo.get_rect(midtop=(width // 2, int(height * 0.04)))

_cat_size = int(height * 0.28)
_cats = [
    (_load_cat("Orange_cat.png",  _cat_size), int(width * 0.08),  height - int(height * 0.12)),
    (_load_cat("Tabby_cat.png",   _cat_size), int(width * 0.92),  height - int(height * 0.12)),
    (_load_cat("Grey_cat.png",    _cat_size), int(width * 0.12),  int(height * 0.52)),
    (_load_cat("Brown_cat.png",   _cat_size), int(width * 0.88),  int(height * 0.52)),
]


def update(state, events):
    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN:
            if new_rect.collidepoint(event.pos):
                return "new_game"
            elif join_rect.collidepoint(event.pos):
                return "join_game"


def draw(state, screen):
    screen.fill(SKY)

    # Cat images — centred on their anchor points
    for img, cx, cy in _cats:
        screen.blit(img, img.get_rect(center=(cx, cy)))

    # Logo
    screen.blit(_logo, _logo_rect)

    mouse_pos = pg.mouse.get_pos()

    # New Game button
    col = BROWN if new_rect.collidepoint(mouse_pos) else GOLD
    padded_new = new_rect.inflate(30, 16)
    pg.draw.rect(screen, col,   padded_new, border_radius=12)
    pg.draw.rect(screen, BROWN, padded_new, 3, border_radius=12)
    screen.blit(new_text, new_rect)

    # Join Game button
    col = BROWN if join_rect.collidepoint(mouse_pos) else GOLD
    padded_join = join_rect.inflate(30, 16)
    pg.draw.rect(screen, col,   padded_join, border_radius=12)
    pg.draw.rect(screen, BROWN, padded_join, 3, border_radius=12)
    screen.blit(join_text, join_rect)


def init(state):
    pass


functions = (update, draw, init)
