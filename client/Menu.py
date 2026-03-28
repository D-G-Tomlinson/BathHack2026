import pygame
import sys
import importlib.util
import os

os.environ["SDL_RENDER_SCALE_QUALITY"] = "0"
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Cat Mini Games")

W, H = screen.get_size()
BASE_W, BASE_H = 800, 600
_s  = min(W / BASE_W, H / BASE_H)
_ox = (W - int(BASE_W * _s)) // 2
_oy = (H - int(BASE_H * _s)) // 2

def sx(v): return int(v * _s)
def px(v): return _ox + int(v * _s)
def py(v): return _oy + int(v * _s)

BG = (174, 207, 223)
BLACK = (10, 10, 10)
DARK = (140, 80, 35)

font_title = pygame.font.SysFont("Comic Sans MS", sx(48), bold=True)
font_btn = pygame.font.SysFont("Comic Sans MS", sx(22), bold=True)

BASE = os.path.dirname(os.path.abspath(__file__))

effect = lambda difficulty: 1 + difficulty

GAMES = [
    ("Cat Connections", "ConnectionsMiniGame.py", (229, 178, 93), (210, 158, 73), (70, 40, 0), 5),
    ("Maths Mini Game", "MathsMiniGame.py", (174, 207, 223), (154, 187, 203), (20, 60, 100), 4),
    ("Karaoke", "KaraokeMiniGame.py", (176, 123, 172), (156, 103, 152), (60, 20, 80), 1),
    ("Wordle", "WordleMiniGame.py", (167, 201, 149), (147, 181, 129), (20, 60, 20), 2),
    ("Spelling Bee", "SpellingMiniGame.py", (184, 125, 75), (164, 105, 55), (255, 250, 240), 3),
]

BTN_W   = sx(300)
BTN_H   = sx(55)
BTN_GAP = sx(12)
START_Y = py(160)

BUTTONS = [
    pygame.Rect(W // 2 - BTN_W // 2, START_Y + i * (BTN_H + BTN_GAP), BTN_W, BTN_H)
    for i in range(len(GAMES))
]
BTN_QUIT = pygame.Rect(W // 2 - BTN_W // 2, START_Y + len(GAMES) * (BTN_H + BTN_GAP) + sx(10), BTN_W, BTN_H)
QUIT_COLOURS = ((220, 220, 215), (200, 200, 195), DARK)


def draw_button(label, rect, colour, hover_colour, text_colour, hovered):
    bg = hover_colour if hovered else colour
    pygame.draw.rect(screen, bg, rect, border_radius=sx(8))
    pygame.draw.rect(screen, DARK, rect, 2, border_radius=sx(8))
    t = font_btn.render(label, True, text_colour)
    screen.blit(t, (rect.x + (rect.w - t.get_width()) // 2,
                    rect.y + (rect.h - t.get_height()) // 2))


def launch(script):
    name = script.replace('.py', '')
    _orig_set_mode = pygame.display.set_mode
    pygame.display.set_mode = lambda *a, **kw: screen
    try:
        if name not in sys.modules:
            spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, script))
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        mod = sys.modules[name]
    finally:
        pygame.display.set_mode = _orig_set_mode
    mod.run(screen, clock)
    pygame.event.clear()
    pygame.display.set_caption("Cat Games")


input_score = int(sys.argv[1]) if len(sys.argv) > 1 else None

clock = pygame.time.Clock()
selected_idx = None

while True:
    mx, my = pygame.mouse.get_pos()
    launch_script = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            launch_script = "quit"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(BUTTONS):
                if rect.collidepoint(mx, my):
                    launch_script = GAMES[i][1]
                    selected_idx = i
            if BTN_QUIT.collidepoint(mx, my):
                launch_script = "quit"

    if launch_script == "quit":
        break
    elif launch_script:
        try:
            launch(launch_script)
        except SystemExit:
            break
        if input_score is not None:
            _, _, _, _, _, difficulty = GAMES[selected_idx]
            print(input_score * effect(difficulty))
            break

    screen.fill(BG)

    t = font_title.render("Cat Games", True, BLACK)
    screen.blit(t, (W // 2 - t.get_width() // 2, py(90)))

    for i, (label, _, col, hcol, tcol, *_) in enumerate(GAMES):
        draw_button(label, BUTTONS[i], col, hcol, tcol, BUTTONS[i].collidepoint(mx, my))
    draw_button("Quit", BTN_QUIT, *QUIT_COLOURS, BTN_QUIT.collidepoint(mx, my))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
