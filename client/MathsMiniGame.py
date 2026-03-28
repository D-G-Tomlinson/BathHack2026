import pygame
import random

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
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
BROWN  = (140,  80,  35)
TAN    = (184, 125,  75)
PURPLE = (176, 123, 172)
LIME   = ( 80, 160,  60)
CREAM  = (250, 243, 220)
INK    = ( 55,  30,   8)
RED    = (210,  85,  75)
GOLD   = (229, 178,  93)

QTW, QTH = sx(110), sx(110)   # question tile size
ATW, ATH = sx(95),  sx(95)    # answer tile size

fO  = pygame.font.SysFont("Comic Sans MS", sx(44), bold=True)
fA  = pygame.font.SysFont("Comic Sans MS", sx(38), bold=True)
fU  = pygame.font.SysFont("Comic Sans MS", sx(26), bold=True)
fB  = pygame.font.SysFont("Comic Sans MS", sx(52), bold=True)
fS  = pygame.font.SysFont("Comic Sans MS", sx(18))

TOTAL_QUESTIONS = 5

# 4 answer tiles in a row
SPOTS = [px(133), px(310), px(487), px(664)]
ANS_Y = py(490)


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


def run_game():
    score = 0
    q_num = 1
    a, av, op, b, bv, ans, opts = new_question()
    feedback = None
    picked = None

    while True:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
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
        clock.tick(60)


def end_screen(score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
        screen.fill(BG)
        pygame.draw.rect(screen, CREAM, (px(160), py(170), sx(480), sx(240)), border_radius=sx(16))
        pygame.draw.rect(screen, TAN, (px(160), py(170), sx(480), sx(240)), sx(3), border_radius=sx(16))
        screen.blit(fB.render("Finished!", True, PURPLE), (W//2 - fB.size("Finished!")[0]//2, py(200)))
        screen.blit(fB.render(f"Score: {score}", True, TAN), (W//2 - fB.size(f"Score: {score}")[0]//2, py(268)))
        screen.blit(fS.render("Press any key to continue", True, TAN), (W//2 - fS.size("Press any key to continue")[0]//2, py(360)))
        pygame.display.flip()
        clock.tick(60)


try:
    end_screen(run_game())
except Exception as e:
    import traceback
    traceback.print_exc()
    input("Press Enter to close...")
finally:
    pygame.quit()
