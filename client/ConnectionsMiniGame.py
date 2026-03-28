import os
import pygame
import random
import sys
import math
from collections import Counter

os.environ["SDL_RENDER_SCALE_QUALITY"] = "0"
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Cat Connections")

W, H = screen.get_size()
BASE_W, BASE_H = 800, 650
_s  = min(W / BASE_W, H / BASE_H)
_ox = (W - int(BASE_W * _s)) // 2
_oy = (H - int(BASE_H * _s)) // 2

def sx(v): return int(v * _s)
def px(v): return _ox + int(v * _s)
def py(v): return _oy + int(v * _s)

font_title   = pygame.font.SysFont("Comic Sans MS", sx(34), bold=True)
font_sub     = pygame.font.SysFont("Comic Sans MS", sx(15))
font_word    = pygame.font.SysFont("Comic Sans MS", sx(17), bold=True)
font_word_sm = pygame.font.SysFont("Comic Sans MS", sx(13), bold=True)
font_cat     = pygame.font.SysFont("Comic Sans MS", sx(14), bold=True)
font_ui      = pygame.font.SysFont("Comic Sans MS", sx(14))
font_msg     = pygame.font.SysFont("Comic Sans MS", sx(19), bold=True)
font_btn     = pygame.font.SysFont("Comic Sans MS", sx(15), bold=True)

BG          = (174, 207, 223)
WHITE       = (255, 255, 255)
BLACK       = (10, 10, 10)
LIGHT_GREY  = (250, 243, 220)
GREY        = (200, 170, 130)
DARK        = (140, 80, 35)
TILE_UNSEL  = (250, 243, 220)
TILE_SEL    = (184, 125, 75)
TILE_SEL_T  = (255, 250, 240)
TILE_UNSEL_T = (55, 30, 8)

CAT_COLOURS = [
    (229, 178, 93),
    (184, 125, 75),
    (174, 207, 223),
    (176, 123, 172),
]
CAT_TEXT = [
    (70, 40, 0),
    (255, 250, 240),
    (20, 60, 100),
    (60, 20, 80),
]

PUZZLES = [
    {
        "title": "Puzzle 1 - Cat World",
        "categories": [
            {
                "name": "Sounds Cats Make",
                "words": ["MEOW", "PURR", "HISS", "CHIRP"],
                "difficulty": 0,
            },
            {
                "name": "Cat Breeds",
                "words": ["SIAMESE", "BENGAL", "PERSIAN", "RAGDOLL"],
                "difficulty": 1,
            },
            {
                "name": "Things Cats Do",
                "words": ["SLEEPING", "PLAYING", "ZOOMIES", "GROOMING"],
                "difficulty": 2,
            },
            {
                "name": "Famous Cartoon Cats",
                "words": ["FELIX", "GARFIELD", "TOM", "SYLVESTER"],
                "difficulty": 3,
            },
        ],
    },
    {
        "title": "Puzzle 2 - Cat Anatomy",
        "categories": [
            {
                "name": "Cat Body Parts",
                "words": ["WHISKERS", "PAWS", "TAIL", "CLAWS"],
                "difficulty": 0,
            },
            {
                "name": "Things Cats Love",
                "words": ["CATNIP", "TUNA", "MILK", "TREATS"],
                "difficulty": 1,
            },
            {
                "name": "Cat Coat Patterns",
                "words": ["CALICO", "TUXEDO", "TABBY", "SPOTTED"],
                "difficulty": 2,
            },
            {
                "name": "Famous Fictional Cats",
                "words": ["CHESHIRE", "DUCHESS", "FIGARO", "PUSS"],
                "difficulty": 3,
            },
        ],
    },
    {
        "title": "Puzzle 3 - Cat Culture",
        "categories": [
            {
                "name": "Cat Colours",
                "words": ["GINGER", "WHITE", "BLACK", "GREY"],
                "difficulty": 0,
            },
            {
                "name": "Cute Cat Breeds",
                "words": ["PERSIAN", "RAGDOLL", "MUNCHKIN", "SCOTTISH"],
                "difficulty": 1,
            },
            {
                "name": "Things Cats Do",
                "words": ["STRETCH", "GROOM", "POUNCE", "STALK"],
                "difficulty": 2,
            },
            {
                "name": "Where Cats Nap",
                "words": ["SOFA", "BED", "BOX", "LAP"],
                "difficulty": 3,
            },
        ],
    },
]

TILE_W   = sx(170)
TILE_H   = sx(58)
TILE_GAP = sx(10)
COLS     = 4
BAR_W    = TILE_W * COLS + TILE_GAP * (COLS - 1)
GRID_X   = (W - BAR_W) // 2
GRID_Y   = py(100)
ROW_H    = TILE_H + TILE_GAP


def rounded_rect(surf, colour, rect, r=8, border=0, bcol=None):
    pygame.draw.rect(surf, colour, rect, border_radius=r)
    if border and bcol:
        pygame.draw.rect(surf, bcol, rect, border, border_radius=r)


def draw_btn(surf, label, rect, bg, fg, hover_bg=None, active=True):
    col = hover_bg if (hover_bg and rect.collidepoint(pygame.mouse.get_pos())) else bg
    if not active:
        col = LIGHT_GREY
        fg  = GREY
    rounded_rect(surf, col, rect, r=sx(8))
    rounded_rect(surf, DARK if active else GREY, rect, r=sx(8), border=sx(2), bcol=DARK if active else GREY)
    t = font_btn.render(label, True, fg)
    surf.blit(t, (rect.x + (rect.w - t.get_width()) // 2,
                  rect.y + (rect.h - t.get_height()) // 2))


def tile_rect(row, col, n_solved, shake_x=0):
    x = GRID_X + col * (TILE_W + TILE_GAP) + shake_x
    y = GRID_Y + n_solved * ROW_H + row * ROW_H
    return pygame.Rect(x, y, TILE_W, TILE_H)


class Game:
    def __init__(self):
        self.load_puzzle()

    def load_puzzle(self):
        p = random.choice(PUZZLES)
        self.title   = p["title"]
        self.cats    = p["categories"]
        self.words   = []
        for ci, cat in enumerate(self.cats):
            for w in cat["words"]:
                self.words.append({"text": w, "cat": ci, "solved": False})
        random.shuffle(self.words)
        self.selected   = set()
        self.solved     = []    # solved category dicts in order solved
        self.mistakes   = 6
        self.hints_left = 2
        self.msg       = ""
        self.msg_colour = BLACK
        self.msg_timer = 0
        self.state     = "playing"
        self.shake     = 0

    def unsolved(self):
        return [w for w in self.words if not w["solved"]]

    def toggle(self, idx):
        if idx in self.selected:
            self.selected.discard(idx)
        elif len(self.selected) < 4:
            self.selected.add(idx)

    def submit(self):
        if len(self.selected) != 4:
            return
        uns = self.unsolved()
        sel_words   = [uns[i] for i in self.selected]
        cats_in_sel = [w["cat"] for w in sel_words]

        if len(set(cats_in_sel)) == 1:
            ci = cats_in_sel[0]
            for w in sel_words:
                w["solved"] = True
            cat = self.cats[ci]
            self.solved.append({
                "name":       cat["name"],
                "words":      [w["text"] for w in sel_words],
                "difficulty": cat["difficulty"],
            })
            self.selected = set()
            self.set_msg(f'Correct! "{cat["name"]}"', CAT_COLOURS[cat["difficulty"]])
            if len(self.solved) == 4:
                self.state = "won"
                self.set_msg("Purrfect! You solved it all!", CAT_COLOURS[0])
        else:
            self.mistakes -= 1
            if max(Counter(cats_in_sel).values()) == 3:
                self.set_msg("So close - one away!", (200, 120, 50))
            else:
                self.set_msg(f"Not quite! {self.mistakes} tries left.", (180, 60, 60))
            self.shake = 25
            if self.mistakes <= 0:
                self.state = "lost"
                self.set_msg("Game over! Give it another try!", (180, 60, 60))

    def set_msg(self, m, col=None):
        self.msg       = m
        self.msg_colour = col if col else BLACK
        self.msg_timer = 220

    def shuffle(self):
        uns = self.unsolved()
        random.shuffle(uns)
        self.words    = [w for w in self.words if w["solved"]] + uns
        self.selected = set()

    def deselect_all(self):
        self.selected = set()

    def use_hint(self):
        if self.hints_left <= 0:
            self.set_msg("No hints left!", (180, 60, 60))
            return
        solved_names = {c["name"] for c in self.solved}
        unsolved_cats = [cat for cat in self.cats if cat["name"] not in solved_names]
        if unsolved_cats:
            cat = random.choice(unsolved_cats)
            self.hints_left -= 1
            self.set_msg(f'Hint: Find "{cat["name"]}"', CAT_COLOURS[cat["difficulty"]])


def draw_mistake_pips(surf, mistakes, cx, y):
    pip_r   = sx(6)
    spacing = sx(18)
    total_w = 6 * spacing
    start_x = cx - total_w // 2
    for i in range(6):
        col = (176, 123, 172) if i < mistakes else (210, 190, 170)
        pygame.draw.circle(surf, col, (start_x + i * spacing + pip_r, y + pip_r), pip_r)
        pygame.draw.circle(surf, DARK, (start_x + i * spacing + pip_r, y + pip_r), pip_r, 2)


def main():
    clock = pygame.time.Clock()
    game  = Game()

    while True:
        clock.tick(60)

        btn_y    = GRID_Y + 4 * ROW_H + sx(18)
        btn_w    = sx(100)
        btn_h    = sx(40)
        btn_shuf = pygame.Rect(W // 2 - sx(215), btn_y, btn_w, btn_h)
        btn_des  = pygame.Rect(W // 2 - sx(105), btn_y, btn_w, btn_h)
        btn_hint = pygame.Rect(W // 2 + sx(5),   btn_y, btn_w, btn_h)
        btn_sub  = pygame.Rect(W // 2 + sx(115), btn_y, btn_w, btn_h)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if game.state == "playing":
                    uns = game.unsolved()
                    for i, w in enumerate(uns):
                        r = tile_rect(i // COLS, i % COLS, len(game.solved))
                        if r.collidepoint(mx, my):
                            game.toggle(i)
                    if btn_sub.collidepoint(mx, my):
                        game.submit()
                    if btn_shuf.collidepoint(mx, my):
                        game.shuffle()
                    if btn_des.collidepoint(mx, my):
                        game.deselect_all()
                    if btn_hint.collidepoint(mx, my):
                        game.use_hint()


        if game.msg_timer > 0:
            game.msg_timer -= 1
        if game.shake > 0:
            game.shake -= 1

        screen.fill(BG)

        t = font_title.render("Cat Connections", True, BLACK)
        screen.blit(t, (W // 2 - t.get_width() // 2, py(10)))

        t = font_sub.render(game.title, True, DARK)
        screen.blit(t, (W // 2 - t.get_width() // 2, py(56)))

        pip_cx = px(740)
        lbl = font_sub.render("Mistakes:", True, DARK)
        screen.blit(lbl, (pip_cx - sx(44) - sx(8) - lbl.get_width(), py(56)))
        draw_mistake_pips(screen, game.mistakes, pip_cx, py(52))

        for i, cat in enumerate(game.solved):
            bar  = pygame.Rect(GRID_X, GRID_Y + i * ROW_H, BAR_W, TILE_H)
            diff = cat["difficulty"]
            rounded_rect(screen, CAT_COLOURS[diff], bar, r=sx(8))
            nt = font_cat.render(cat["name"].upper(), True, CAT_TEXT[diff])
            screen.blit(nt, (bar.x + (bar.w - nt.get_width()) // 2, bar.y + sx(8)))
            wt = font_ui.render("  ".join(cat["words"]), True, CAT_TEXT[diff])
            screen.blit(wt, (bar.x + (bar.w - wt.get_width()) // 2, bar.y + sx(30)))

        uns     = game.unsolved()
        shake_x = int(math.sin(game.shake * 0.9) * sx(6)) if game.shake > 0 else 0

        for i, w in enumerate(uns):
            row, col = divmod(i, COLS)
            tile_sx  = shake_x if i in game.selected else 0
            r   = tile_rect(row, col, len(game.solved), tile_sx)
            sel = i in game.selected
            rounded_rect(screen, TILE_SEL if sel else TILE_UNSEL, r, r=sx(8))
            f = font_word_sm if len(w["text"]) > 10 else font_word
            t = f.render(w["text"], True, TILE_SEL_T if sel else TILE_UNSEL_T)
            screen.blit(t, (r.x + (r.w - t.get_width()) // 2,
                            r.y + (r.h - t.get_height()) // 2))

        if game.msg and game.msg_timer > 0:
            t = font_msg.render(game.msg, True, game.msg_colour)
            screen.blit(t, (W // 2 - t.get_width() // 2, btn_y - sx(33)))

        if game.state == "playing":
            draw_btn(screen, "Shuffle",      btn_shuf, LIGHT_GREY, BLACK, hover_bg=GREY)
            draw_btn(screen, "Deselect All", btn_des,  LIGHT_GREY, BLACK, hover_bg=GREY)
            can_hint = game.hints_left > 0
            draw_btn(screen, f"Hint ({game.hints_left})", btn_hint,
                     (174, 207, 223) if can_hint else LIGHT_GREY,
                     BLACK          if can_hint else GREY,
                     hover_bg=(140, 180, 200) if can_hint else None,
                     active=can_hint)
            can_sub = len(game.selected) == 4
            draw_btn(screen, "Submit", btn_sub,
                     (176, 123, 172) if can_sub else LIGHT_GREY,
                     WHITE          if can_sub else GREY,
                     hover_bg=(150, 100, 148) if can_sub else None,
                     active=can_sub)


        pygame.display.flip()


if __name__ == "__main__":
    main()
