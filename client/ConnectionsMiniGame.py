import pygame
import random
import sys
import math
from collections import Counter

pygame.init()

WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Cat Connections")

# Fonts
font_title  = pygame.font.SysFont("segoeui", 34, bold=True)
font_sub    = pygame.font.SysFont("segoeui", 15)
font_word   = pygame.font.SysFont("segoeui", 17, bold=True)
font_word_sm = pygame.font.SysFont("segoeui", 13, bold=True)
font_cat    = pygame.font.SysFont("segoeui", 14, bold=True)
font_ui     = pygame.font.SysFont("segoeui", 14)
font_msg    = pygame.font.SysFont("segoeui", 19, bold=True)
font_btn    = pygame.font.SysFont("segoeui", 15, bold=True)

# Colors
BG          = (250, 248, 245)
WHITE       = (255, 255, 255)
BLACK       = ( 10,  10,  10)
LIGHT_GRAY  = (240, 240, 235)
GRAY        = (200, 200, 195)
DARK        = ( 58,  58,  58)
TILE_UNSEL  = (239, 239, 230)
TILE_SEL    = ( 90,  89,  78)
TILE_SEL_T  = (255, 255, 255)
TILE_UNSEL_T = (10,  10,  10)

CAT_COLORS = [
    (229, 178,  93),   # E5B25D - easy
    (184, 125,  75),   # B87D4B - medium
    (174, 207, 223),   # AECFDF - hard
    (176, 123, 172),   # B07BAC - tricky
]
CAT_TEXT = [
    ( 70,  40,   0),
    (255, 250, 240),
    ( 20,  60, 100),
    ( 60,  20,  80),
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
                "words": ["SIAMESE", "BENGAL", "PERSIAN", "BURMESE"],
                "difficulty": 1,
            },
            {
                "name": "Cat Behaviours",
                "words": ["KNEADING", "LOAFING", "ZOOMIES", "BUNTING"],
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
                "words": ["CATNIP", "TUNA", "KIBBLE", "TREATS"],
                "difficulty": 1,
            },
            {
                "name": "Cat Coat Patterns",
                "words": ["CALICO", "TUXEDO", "TABBY", "TORTOISESHELL"],
                "difficulty": 2,
            },
            {
                "name": "Famous Fictional Cats",
                "words": ["CHESHIRE", "CROOKSHANKS", "DUCHESS", "BINX"],
                "difficulty": 3,
            },
        ],
    },
    {
        "title": "Puzzle 3 - Cat Culture",
        "categories": [
            {
                "name": "___ Cat (Internet Meme)",
                "words": ["NYAN", "GRUMPY", "KEYBOARD", "CEILING"],
                "difficulty": 0,
            },
            {
                "name": "Unusual Cat Breeds",
                "words": ["SPHYNX", "MUNCHKIN", "RAGDOLL", "ABYSSINIAN"],
                "difficulty": 1,
            },
            {
                "name": "Things Cats Do",
                "words": ["STRETCH", "GROOM", "POUNCE", "STALK"],
                "difficulty": 2,
            },
            {
                "name": "Cat in Other Languages",
                "words": ["NEKO", "CHAT", "GATO", "KATZE"],
                "difficulty": 3,
            },
        ],
    },
]

# Grid layout constants
TILE_W   = 170
TILE_H   = 58
TILE_GAP = 10
COLS     = 4
BAR_W    = TILE_W * COLS + TILE_GAP * (COLS - 1)   # 710 px
GRID_X   = (WIDTH - BAR_W) // 2                      # 45 px
GRID_Y   = 85
ROW_H    = TILE_H + TILE_GAP                         # 68 px


def rounded_rect(surf, color, rect, r=8, border=0, bcol=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and bcol:
        pygame.draw.rect(surf, bcol, rect, border, border_radius=r)


def draw_btn(surf, label, rect, bg, fg, hover_bg=None, active=True):
    col = hover_bg if (hover_bg and rect.collidepoint(pygame.mouse.get_pos())) else bg
    if not active:
        col = LIGHT_GRAY
        fg  = GRAY
    rounded_rect(surf, col, rect, r=8)
    rounded_rect(surf, DARK if active else GRAY, rect, r=8, border=2, bcol=DARK if active else GRAY)
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
        self.selected  = set()
        self.solved    = []    # solved category dicts in order solved
        self.mistakes  = 4
        self.msg       = ""
        self.msg_color = BLACK
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
            # Correct guess
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
            self.set_msg(f'Correct! "{cat["name"]}"', CAT_COLORS[cat["difficulty"]])
            if len(self.solved) == 4:
                self.state = "won"
                self.set_msg("Purrfect! You solved it all!", CAT_COLORS[0])
        else:
            # Wrong guess
            self.mistakes -= 1
            if max(Counter(cats_in_sel).values()) == 3:
                self.set_msg("So close - one away!", (200, 120, 50))
            else:
                self.set_msg(f"Not quite! {self.mistakes} mistake(s) left.", (180, 60, 60))
            self.shake = 25
            if self.mistakes <= 0:
                self.state = "lost"
                self.set_msg("Game over! Better luck next time.", (180, 60, 60))

    def set_msg(self, m, col=None):
        self.msg       = m
        self.msg_color = col if col else BLACK
        self.msg_timer = 220

    def shuffle(self):
        uns = self.unsolved()
        random.shuffle(uns)
        self.words    = [w for w in self.words if w["solved"]] + uns
        self.selected = set()

    def deselect_all(self):
        self.selected = set()


def draw_mistake_pips(surf, mistakes, cx, y):
    """Draw small filled/empty circles indicating remaining mistakes."""
    pip_r   = 7
    spacing = 22
    total_w = 4 * spacing
    sx = cx - total_w // 2
    for i in range(4):
        col = (80, 80, 80) if i < mistakes else (210, 210, 205)
        pygame.draw.circle(surf, col, (sx + i * spacing + pip_r, y + pip_r), pip_r)
        pygame.draw.circle(surf, DARK, (sx + i * spacing + pip_r, y + pip_r), pip_r, 2)


def main():
    clock = pygame.time.Clock()
    game  = Game()

    while True:
        clock.tick(60)

        # Button rects (constant layout below the 4-row grid)
        btn_y    = GRID_Y + 4 * ROW_H + 18   # y = 375
        btn_sub  = pygame.Rect(WIDTH // 2 - 65,  btn_y,      130, 40)
        btn_shuf = pygame.Rect(WIDTH // 2 - 215, btn_y,      130, 40)
        btn_des  = pygame.Rect(WIDTH // 2 + 85,  btn_y,      130, 40)

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


        if game.msg_timer > 0:
            game.msg_timer -= 1
        if game.shake > 0:
            game.shake -= 1

        screen.fill(BG)

        t = font_title.render("Cat Connections", True, BLACK)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 10))

        t = font_sub.render(game.title, True, DARK)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 52))

        draw_mistake_pips(screen, game.mistakes, WIDTH // 2 + 180, 48)
        lbl = font_sub.render("Mistakes:", True, DARK)
        screen.blit(lbl, (WIDTH // 2 + 88, 52))

        for i, cat in enumerate(game.solved):
            bar  = pygame.Rect(GRID_X, GRID_Y + i * ROW_H, BAR_W, TILE_H)
            diff = cat["difficulty"]
            rounded_rect(screen, CAT_COLORS[diff], bar, r=8)
            nt = font_cat.render(cat["name"].upper(), True, CAT_TEXT[diff])
            screen.blit(nt, (bar.x + (bar.w - nt.get_width()) // 2, bar.y + 8))
            wt = font_ui.render("  ".join(cat["words"]), True, CAT_TEXT[diff])
            screen.blit(wt, (bar.x + (bar.w - wt.get_width()) // 2, bar.y + 30))

        uns     = game.unsolved()
        shake_x = int(math.sin(game.shake * 0.9) * 6) if game.shake > 0 else 0

        for i, w in enumerate(uns):
            row, col = divmod(i, COLS)
            sx  = shake_x if i in game.selected else 0
            r   = tile_rect(row, col, len(game.solved), sx)
            sel = i in game.selected
            rounded_rect(screen, TILE_SEL if sel else TILE_UNSEL, r, r=8)
            f = font_word_sm if len(w["text"]) > 10 else font_word
            t = f.render(w["text"], True, TILE_SEL_T if sel else TILE_UNSEL_T)
            screen.blit(t, (r.x + (r.w - t.get_width()) // 2,
                            r.y + (r.h - t.get_height()) // 2))

        if game.msg and game.msg_timer > 0:
            t = font_msg.render(game.msg, True, game.msg_color)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, btn_y - 33))

        if game.state == "playing":
            draw_btn(screen, "Shuffle",      btn_shuf, LIGHT_GRAY, BLACK, hover_bg=GRAY)
            draw_btn(screen, "Deselect All", btn_des,  LIGHT_GRAY, BLACK, hover_bg=GRAY)
            can_sub = len(game.selected) == 4
            draw_btn(screen, "Submit", btn_sub,
                     (70, 70, 70) if can_sub else LIGHT_GRAY,
                     WHITE       if can_sub else GRAY,
                     hover_bg=(100, 100, 100) if can_sub else None,
                     active=can_sub)


        pygame.display.flip()


if __name__ == "__main__":
    main()
