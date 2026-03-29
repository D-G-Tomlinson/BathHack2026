import pygame as pg
import os
import math
from backend_handler import get_game

# Palette
GOLD  = (229, 178,  93)
BROWN = (184, 125,  75)
SKY   = (174, 207, 223)
MAUVE = (176, 123, 172)
GREEN = (181, 231, 137)
WHITE = (255, 255, 255)
BLACK = ( 30,  30,  30)

TITLE_FONT = pg.font.SysFont("comicsansms", 64)
CODE_FONT  = pg.font.SysFont("comicsansms", 52)
SUB_FONT   = pg.font.SysFont("comicsansms", 30)

info   = pg.display.Info()
width, height = info.current_w, info.current_h

_IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "Images", "Colours")

def _load_cat(name, size):
    img = pg.image.load(os.path.join(_IMG_DIR, name)).convert_alpha()
    w, h = img.get_size()
    scale = size / max(w, h)
    return pg.transform.smoothscale(img, (int(w * scale), int(h * scale)))


# ── circular-cropped centre cat ──────────────────────────────────────
_CIRCLE_R   = int(height * 0.16)
_CIRCLE_D   = _CIRCLE_R * 2
_CAT_CX     = width  // 2
_CAT_CY     = int(height * 0.42)

def _make_circle_cat(name):
    raw = pg.image.load(os.path.join(_IMG_DIR, name)).convert_alpha()
    cat = pg.transform.smoothscale(raw, (_CIRCLE_D, _CIRCLE_D))
    # build circular mask
    mask = pg.Surface((_CIRCLE_D, _CIRCLE_D), pg.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pg.draw.circle(mask, (255, 255, 255, 255), (_CIRCLE_R, _CIRCLE_R), _CIRCLE_R)
    cat.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return cat

_circle_cat = _make_circle_cat("Orange_cat.png")

# ── spinner ring sits just outside the cat circle ────────────────────
_SPIN_R   = _CIRCLE_R + int(height * 0.055)
_NDOTS    = 10
_DOT_MAX  = int(height * 0.014)

# ── corner decoration cats ────────────────────────────────────────────
_deco_size = int(height * 0.20)
_deco_cats = [
    (_load_cat("Sleeping_tabby_cat.png", _deco_size), int(width * 0.06),  height - int(height * 0.06)),
    (_load_cat("White_cat.png",          _deco_size), int(width * 0.94),  height - int(height * 0.06)),
]

code_text  = None
code_rect  = None
_last_poll = 0


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw(game, screen):
    screen.fill(SKY)
    t = pg.time.get_ticks()

    # ── corner cats ───────────────────────────────────────────────────
    for img, cx, cy in _deco_cats:
        screen.blit(img, img.get_rect(midbottom=(cx, cy)))

    # ── title ─────────────────────────────────────────────────────────
    title = TITLE_FONT.render("Waiting for Player 2", True, MAUVE)
    screen.blit(title, title.get_rect(midtop=(width // 2, int(height * 0.05))))

    # ── spinner ring (drawn behind the cat) ───────────────────────────
    angle_offset = (t / 900.0) * math.tau
    for i in range(_NDOTS):
        frac   = (i + 1) / _NDOTS
        fade   = frac ** 1.6
        angle  = angle_offset + math.tau * i / _NDOTS
        dx     = math.cos(angle) * _SPIN_R
        dy     = math.sin(angle) * _SPIN_R
        colour = _lerp_color(SKY, MAUVE, fade)
        r      = max(3, int(_DOT_MAX * (0.35 + 0.65 * fade)))
        pg.draw.circle(screen, colour, (int(_CAT_CX + dx), int(_CAT_CY + dy)), r)

    # ── circular cat border ring ──────────────────────────────────────
    pg.draw.circle(screen, GOLD,  (_CAT_CX, _CAT_CY), _CIRCLE_R + 6)
    pg.draw.circle(screen, BROWN, (_CAT_CX, _CAT_CY), _CIRCLE_R + 6, 4)

    # ── bouncing circular cat ─────────────────────────────────────────
    bob = math.sin(t / 500.0) * int(height * 0.012)
    rect = _circle_cat.get_rect(center=(_CAT_CX, int(_CAT_CY + bob)))
    screen.blit(_circle_cat, rect)

    # ── code card ─────────────────────────────────────────────────────
    if code_text:
        pad = 28
        box = code_rect.inflate(pad * 2, pad * 2)
        pg.draw.rect(screen, GOLD,  box, border_radius=16)
        pg.draw.rect(screen, BROWN, box, 4, border_radius=16)
        screen.blit(code_text, code_rect)

        hint = SUB_FONT.render("Share this code with your opponent!", True, BROWN)
        screen.blit(hint, hint.get_rect(midtop=(width // 2, box.bottom + 12)))


def update(game, events):
    global _last_poll
    now = pg.time.get_ticks()
    if now - _last_poll >= 2000:
        _last_poll = now
        state = get_game(game.code)
        if state.get("player2Name") is not None:
            return "board"


def init(game):
    global code_text, code_rect, _last_poll
    _last_poll = 0
    code_text = CODE_FONT.render("Code:  " + game.code, True, BLACK)
    code_rect = code_text.get_rect(center=(width // 2, int(height * 0.72)))


functions = (update, draw, init)
