import pygame
import random
import os

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
pygame.display.set_caption("Scrabble Maths")
clock = pygame.time.Clock()

W, H = screen.get_size()
BASE_W, BASE_H = 800, 600
_s  = min(W / BASE_W, H / BASE_H)
_ox = (W - int(BASE_W * _s)) // 2
_oy = (H - int(BASE_H * _s)) // 2

def sx(v): return int(v * _s)
def px(v): return _ox + int(v * _s)
def py(v): return _oy + int(v * _s)

TILE_VALUES = {
    'A': 1, 'E': 1, 'I': 1, 'O': 1, 'U': 1,
    'L': 1, 'N': 1, 'S': 1, 'T': 1, 'R': 1,
    'D': 2, 'G': 2,
    'B': 3, 'C': 3, 'M': 3, 'P': 3,
    'F': 4, 'H': 4, 'V': 4, 'W': 4, 'Y': 4,
    'K': 5, 'J': 8, 'X': 8, 'Q': 10, 'Z': 10,
}
EASY = [l for l, v in TILE_VALUES.items() if v <= 5]


BG     = (174, 207, 223)
BROWN  = (140, 80, 35)
TAN    = (184, 125, 75)
PURPLE = (176, 123, 172)
LIME   = (80, 160, 60)
CREAM  = (250, 243, 220)
INK    = (55, 30, 8)
RED    = (210, 85, 75)
GOLD   = (229, 178, 93)

QTW, QTH = sx(110), sx(110)
ATW, ATH = sx(95),  sx(95)

fO  = pygame.font.SysFont("Comic Sans MS", sx(44), bold=True)
fA  = pygame.font.SysFont("Comic Sans MS", sx(38), bold=True)
fU  = pygame.font.SysFont("Comic Sans MS", sx(26), bold=True)
fB  = pygame.font.SysFont("Comic Sans MS", sx(52), bold=True)
fS  = pygame.font.SysFont("Comic Sans MS", sx(18))

TOTAL_QUESTIONS = 5

# 4 answer tiles in a row
SPOTS = [px(133), px(310), px(487), px(664)]
ANS_Y = py(490)

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Images", "Colours")

def _cat(name, h):
    img = pygame.image.load(os.path.join(IMG_DIR, name)).convert_alpha()
    w = int(img.get_width() * h / img.get_height())
    return pygame.transform.smoothscale(img, (w, h))

# large flanking cats for start screen
cat_orange   = _cat("Orange_cat.png",         sx(115))
cat_tabby    = _cat("Tabby_cat.png",           sx(115))
# sleeping cat for end screen
cat_sleeping = _cat("Sleeping_tabby_cat.png", sx(100))
# small cats for game screen side margins
cat_grey_sm  = _cat("Grey_cat.png",            sx(85))
cat_black_sm = _cat("Black_cat.png",           sx(85))
# bottom row of cats for start screen
cat_row = [
    _cat("Orange_cat.png",  sx(88)),
    _cat("Grey_cat.png",     sx(88)),
    _cat("Black_cat.png",    sx(88)),
    _cat("Brown_cat.png",    sx(88)),
    _cat("White_cat.png",    sx(88)),
]


def draw_tile_img(surf, letter, cx, cy, size):
    pts = TILE_VALUES[letter]
    r = pygame.Rect(cx - size//2, cy - size//2, size, size)
    pygame.draw.rect(surf, GOLD, r, border_radius=sx(8))
    pygame.draw.rect(surf, BROWN, r, sx(3), border_radius=sx(8))
    ls = fO.render(letter, True, INK)
    surf.blit(ls, (cx - ls.get_width()//2, cy - ls.get_height()//2 - sx(4)))
    vs = fS.render(str(pts), True, INK)
    surf.blit(vs, (cx + size//2 - vs.get_width() - sx(8), cy + size//2 - vs.get_height() - sx(8)))


def draw_ans_tile(surf, num, cx, cy, col=None):
    size = ATW
    r = pygame.Rect(cx - size//2, cy - size//2, size, size)
    pygame.draw.rect(surf, col or GOLD, r, border_radius=sx(8))
    pygame.draw.rect(surf, BROWN, r, sx(3), border_radius=sx(8))
    ns = fA.render(str(num), True, INK)
    surf.blit(ns, (cx - ns.get_width()//2, cy - ns.get_height()//2))


def new_question():
    a = random.choice(EASY)
    b = random.choice(EASY)
    av, bv = TILE_VALUES[a], TILE_VALUES[b]

    ops = ['+', '+']
    if av > bv:
        ops.append('-')
    if av * bv <= 20:
        ops.append('x')
    if bv and av % bv == 0 and av // bv > 1:
        ops.append('÷')
    op = random.choice(ops)

    if op == '+': ans = av + bv
    elif op == '-': ans = av - bv
    elif op == 'x': ans = av * bv
    else: ans = av // bv

    wrong = set()
    for _ in range(400):
        w = ans + random.choice([-3, -2, -1, 1, 2, 3])
        if w != ans and w > 0:
            wrong.add(w)
        if len(wrong) == 3:
            break

    opts = [ans] + list(wrong)
    random.shuffle(opts)
    return a, av, op, b, bv, ans, opts


def start_screen():
    btn_w, btn_h = sx(200), sx(60)
    btn_x = W // 2 - btn_w // 2
    btn_y = py(420)
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    while True:
        events = yield
        mx, my = pygame.mouse.get_pos()
        hovered = btn_rect.collidepoint(mx, my)

        for event in events:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered:
                    return True

        screen.fill(BG)

        # cats flanking the instructions card
        screen.blit(cat_orange, (px(5), py(195)))
        screen.blit(cat_tabby,  (px(795) - cat_tabby.get_width(), py(195)))
        # bottom row of cats
        for img, cx in zip(cat_row, [px(80), px(240), px(400), px(560), px(720)]):
            screen.blit(img, (cx - img.get_width() // 2, py(502)))

        # Title
        title = fB.render("Scrabble Maths!", True, PURPLE)
        screen.blit(title, (W // 2 - title.get_width() // 2, py(60)))

        bonus = fS.render("x5 SCORE BONUS!", True, LIME)
        screen.blit(bonus, (W // 2 - bonus.get_width() // 2, py(140)))

        # Instructions card
        card_x, card_y, card_w, card_h = px(100), py(175), sx(600), sx(220)
        pygame.draw.rect(screen, CREAM, (card_x, card_y, card_w, card_h), border_radius=sx(14))
        pygame.draw.rect(screen, TAN, (card_x, card_y, card_w, card_h), sx(2), border_radius=sx(14))

        lines = [
            "Each Scrabble tile has a point value.",
            "You'll be shown two tiles and an operation.",
            "Pick the correct answer from 4 choices.",
            f"Answer {TOTAL_QUESTIONS} questions, good luck!",
        ]
        for i, line in enumerate(lines):
            s = fS.render(line, True, INK)
            screen.blit(s, (W // 2 - s.get_width() // 2, card_y + sx(24) + i * sx(46)))

        # Play button
        btn_color = LIME if hovered else TAN
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=sx(12))
        pygame.draw.rect(screen, BROWN, btn_rect, sx(3), border_radius=sx(12))
        play_label = fU.render("PLAY", True, CREAM)
        screen.blit(play_label, (W // 2 - play_label.get_width() // 2, btn_y + btn_h // 2 - play_label.get_height() // 2))

        pygame.display.flip()


def run_game():
    score = 0
    q_num = 1
    a, av, op, b, bv, ans, opts = new_question()
    feedback = None
    picked = None

    while True:
        events = yield
        now = pygame.time.get_ticks()

        for event in events:
            if event.type == pygame.QUIT:
                return score
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return score
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not feedback or (now - feedback[1]) > 700:
                    mx, my = event.pos
                    for i, tile_x in enumerate(SPOTS):
                        if pygame.Rect(tile_x - ATW//2, ANS_Y - ATH//2, ATW, ATH).collidepoint(mx, my):
                            picked = i
                            feedback = ('y' if opts[i] == ans else 'n', now)
                            if opts[i] == ans:
                                score += 1

        if feedback and (now - feedback[1]) > 700:
            if q_num >= TOTAL_QUESTIONS:
                return score
            feedback = None
            picked = None
            q_num += 1
            a, av, op, b, bv, ans, opts = new_question()

        screen.fill(BG)

        # cats in the side margins (only when there's room)
        if _ox > 40:
            screen.blit(cat_grey_sm,  (_ox // 2 - cat_grey_sm.get_width() // 2,  H // 2 - cat_grey_sm.get_height() // 2))
            screen.blit(cat_black_sm, (W - _ox // 2 - cat_black_sm.get_width() // 2, H // 2 - cat_black_sm.get_height() // 2))

        sc = fU.render(f"Score: {score}", True, TAN)
        screen.blit(sc, (px(18), py(14)))

        title = fU.render("Scrabble Maths!", True, TAN)
        screen.blit(title, (W//2 - title.get_width()//2, py(14)))

        prog = fU.render(f"Q {q_num}/{TOTAL_QUESTIONS}", True, TAN)
        screen.blit(prog, (W - _ox - prog.get_width() - sx(18), py(14)))

        # question card
        pygame.draw.rect(screen, CREAM, (px(60), py(78), sx(680), sx(220)), border_radius=sx(14))
        pygame.draw.rect(screen, TAN, (px(60), py(78), sx(680), sx(220)), sx(2), border_radius=sx(14))

        q_y = py(178)
        draw_tile_img(screen, a, px(200), q_y, QTW)
        op_s = fO.render(op, True, TAN)
        screen.blit(op_s, (px(310) - op_s.get_width()//2, q_y - op_s.get_height()//2))
        draw_tile_img(screen, b, px(420), q_y, QTW)
        eq = fO.render("= ?", True, PURPLE)
        screen.blit(eq, (px(490), q_y - eq.get_height()//2))

        hint = fS.render("Use the tile point values!", True, TAN)
        screen.blit(hint, (W//2 - hint.get_width()//2, py(262)))

        # answer panel
        pygame.draw.rect(screen, CREAM, (px(40), py(390), sx(720), sx(170)), border_radius=sx(14))
        pygame.draw.rect(screen, TAN, (px(40), py(390), sx(720), sx(170)), sx(2), border_radius=sx(14))

        if feedback:
            msg = "Great job!" if feedback[0] == 'y' else "Oops!"
            ms = fU.render(msg, True, LIME if feedback[0] == 'y' else RED)
            screen.blit(ms, (W//2 - ms.get_width()//2, py(338)))
        else:
            ps = fS.render("Pick the answer:", True, TAN)
            screen.blit(ps, (W//2 - ps.get_width()//2, py(340)))

        for i, tile_x in enumerate(SPOTS):
            if picked == i and feedback:
                c = LIME if feedback[0] == 'y' else RED
            elif feedback and feedback[0] == 'n' and opts[i] == ans:
                c = LIME
            else:
                c = None
            draw_ans_tile(screen, opts[i], tile_x, ANS_Y, c)

        pygame.display.flip()


def end_screen(score):
    btn_back = pygame.Rect(W // 2 - sx(75), py(354), sx(150), sx(48))

    while True:
        events = yield
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mx, my):
                    return

        screen.fill(BG)
        screen.blit(cat_sleeping, (W // 2 - cat_sleeping.get_width() // 2, py(55)))
        pygame.draw.rect(screen, CREAM, (px(160), py(170), sx(480), sx(260)), border_radius=sx(16))
        pygame.draw.rect(screen, TAN,   (px(160), py(170), sx(480), sx(260)), sx(3), border_radius=sx(16))
        screen.blit(fB.render("Finished!", True, PURPLE), (W//2 - fB.size("Finished!")[0]//2, py(200)))
        screen.blit(fB.render(f"Score: {score}/{TOTAL_QUESTIONS}", True, TAN), (W//2 - fB.size(f"Score: {score}/{TOTAL_QUESTIONS}")[0]//2, py(268)))

        bk_col = RED if btn_back.collidepoint(mx, my) else (200, 160, 120)
        pygame.draw.rect(screen, bk_col, btn_back, border_radius=sx(10))
        pygame.draw.rect(screen, BROWN,  btn_back, sx(2), border_radius=sx(10))
        bk_lbl = fU.render("Back", True, CREAM)
        screen.blit(bk_lbl, bk_lbl.get_rect(center=btn_back.center))

        pygame.display.flip()


def run_gen(scr, clk):
    global screen, clock
    screen = scr
    clock = clk
    if (yield from start_screen()):
        yield from end_screen((yield from run_game()))


if __name__ == "__main__":
    try:
        gen = run_gen(screen, clock)
        next(gen)
        while True:
            try:
                gen.send(pygame.event.get())
            except StopIteration:
                break
            clock.tick(60)
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")
    finally:
        pygame.quit()
