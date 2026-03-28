import pygame
import sys
import subprocess
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Cat Games")

BG = (250, 248, 245)
BLACK = (10, 10, 10)
DARK = (58, 58, 58)

font_title = pygame.font.SysFont("segoeui", 48, bold=True)
font_btn = pygame.font.SysFont("segoeui", 22, bold=True)

BASE = os.path.dirname(os.path.abspath(__file__))

GAMES = [
    ("Cat Connections", "ConnectionsMiniGame.py", (229, 178, 93), (210, 158, 73), (70, 40, 0)),
    ("Maths Mini Game", "MathsMiniGame.py", (174, 207, 223), (154, 187, 203), (20, 60, 100)),
    ("Karaoke", "KaraokeMiniGame.py", (176, 123, 172), (156, 103, 152), (60, 20, 80)),
    ("Wordle", "WordleMiniGame.py", (167, 201, 149), (147, 181, 129), (20, 60, 20)),
    ("Spelling Bee", "SpellingMiniGame.py", (184, 125, 75), (164, 105, 55), (255, 250, 240)),
]

BTN_W = 300
BTN_H = 55
BTN_GAP = 12
START_Y = 160

BUTTONS = [
    pygame.Rect(WIDTH // 2 - BTN_W // 2, START_Y + i * (BTN_H + BTN_GAP), BTN_W, BTN_H)
    for i in range(len(GAMES))
]
BTN_QUIT = pygame.Rect(WIDTH // 2 - BTN_W // 2, START_Y + len(GAMES) * (BTN_H + BTN_GAP) + 10, BTN_W, BTN_H)
QUIT_COLORS = ((220, 220, 215), (200, 200, 195), DARK)


def draw_button(label, rect, color, hover_color, text_color, hovered):
    bg = hover_color if hovered else color
    pygame.draw.rect(screen, bg, rect, border_radius=10)
    pygame.draw.rect(screen, DARK, rect, 2, border_radius=10)
    t = font_btn.render(label, True, text_color)
    screen.blit(t, (rect.x + (rect.w - t.get_width()) // 2,
                    rect.y + (rect.h - t.get_height()) // 2))


def launch(script):
    pygame.quit()
    subprocess.run([sys.executable, os.path.join(BASE, script)])
    pygame.init()
    s = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Cat Games")
    return s


clock = pygame.time.Clock()

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
            if BTN_QUIT.collidepoint(mx, my):
                launch_script = "quit"

    if launch_script == "quit":
        break
    elif launch_script:
        screen = launch(launch_script)

    screen.fill(BG)

    t = font_title.render("Cat Games", True, BLACK)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 90))

    for i, (label, _, col, hcol, tcol) in enumerate(GAMES):
        draw_button(label, BUTTONS[i], col, hcol, tcol, BUTTONS[i].collidepoint(mx, my))
    draw_button("Quit", BTN_QUIT, *QUIT_COLORS, BTN_QUIT.collidepoint(mx, my))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
