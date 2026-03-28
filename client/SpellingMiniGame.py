import array
import math
import os
import random
import subprocess
import sys
import threading

import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
ASSETS = os.path.dirname(os.path.abspath(__file__))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = (240, 248, 255)
PINK = (255, 182, 193)
DARK_PINK = (210, 80, 120)
GREEN = (60, 180, 100)
RED = (210, 60, 60)
YELLOW = (255, 220, 60)
PURPLE = (160, 80, 210)
GRAY = (160, 160, 160)
PANEL = (255, 245, 250)
BORDER = (200, 160, 180)

# 0=Brown (title/playing), 1=White (correct), 2=Grey (wrong)
CAT_FILES = [
    os.path.join(ASSETS, "Images", "Brown Cat.png"),
    os.path.join(ASSETS, "Images", "White cat.png"),
    os.path.join(ASSETS, "Images", "Grey cat.png"),
]

WORDS = [
    ("cat",     "A furry pet that says meow"),
    ("kitten",  "A baby cat"),
    ("paw",     "A cat's foot"),
    ("purr",    "Sound a happy cat makes"),
    ("claw",    "A cat's sharp nail"),
    ("tail",    "The thing cats wag"),
    ("fur",     "A cat's soft coat"),
    ("meow",    "The sound a cat makes"),
    ("milk",    "Cats love to drink this"),
    ("fish",    "A cat's favourite snack"),
    ("yarn",    "Cats love to play with this"),
    ("nap",     "Cats sleep 16 hours a day!"),
    ("leap",    "Cats jump really high"),
    ("hunt",    "What cats do outside"),
    ("play",    "Kittens love to do this"),
    ("bowl",    "Where a cat drinks from"),
    ("door",    "Cats always want to go through this"),
    ("mat",     "A cat loves to sit on this"),
    ("box",     "Cats always climb inside these"),
    ("spot",    "A patch of colour on a cat"),
    ("soft",    "How a cat's fur feels"),
    ("hiss",    "The angry sound a cat makes"),
    ("lick",    "How a cat cleans itself"),
    ("jump",    "Cats do this onto high places"),
    ("sleep",   "Cats do this for most of the day"),
    ("whisk",   "The long hairs on a cat's face"),
    ("grass",   "Cats like to chew on this outside"),
    ("cream",   "A pale colour, like some cats"),
    ("fluff",   "A very fluffy cat is full of this"),
    ("mouse",   "A small animal cats love to chase"),
    ("bird",    "Another animal cats like to watch"),
    ("home",    "Where a pet cat lives"),
    ("cuddle",  "A warm hug you give your cat"),
    ("brush",   "Used to groom a cat's coat"),
    ("collar",  "Worn around a cat's neck"),
    ("treat",   "A small yummy snack for a cat"),
    ("friend",  "A cat can be your best one"),
    ("window",  "Cats love to sit and look out of this"),
    ("sunny",   "Cats love to lie somewhere warm and this"),
    ("stripe",  "A pattern on a tabby cat"),
]

TOTAL_ROUNDS = 5

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Meow Spelling!")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Comic Sans MS", 56, bold=True)
font_big   = pygame.font.SysFont("Comic Sans MS", 44, bold=True)
font_med   = pygame.font.SysFont("Comic Sans MS", 32, bold=True)
font_small = pygame.font.SysFont("Comic Sans MS", 24)
font_input = pygame.font.SysFont("Comic Sans MS", 38, bold=True)

CAT_SIZE = 180

def _scale_cat(path):
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    scale = CAT_SIZE / max(w, h)
    return pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))

CAT_IMAGES = [_scale_cat(p) for p in CAT_FILES]


def make_tone(freq: float, duration: float, volume: float = 0.4):
    rate = 44100
    n = int(rate * duration)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / rate
        fade = max(0.0, 1.0 - (t / duration) * 1.5)
        buf[i] = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * fade)
    return pygame.mixer.Sound(buffer=buf)

SND_CORRECT = make_tone(880, 0.30)
SND_WRONG   = make_tone(220, 0.40)


def speak(text: str):
    def _run():
        subprocess.run(
            ['powershell', '-Command',
             f'Add-Type -AssemblyName System.Speech; '
             f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text}")'],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    threading.Thread(target=_run, daemon=True).start()


def draw_bg():
    screen.fill(BG)
    for gx in range(60, WIDTH, 130):
        for gy in range(60, HEIGHT, 130):
            pygame.draw.circle(screen, PINK, (gx, gy), 6)

def blit_cat(index: int, cx: int, cy: int):
    surf = CAT_IMAGES[index]
    rect = surf.get_rect(center=(cx, cy))
    card = rect.inflate(20, 20)
    pygame.draw.rect(screen, WHITE, card, border_radius=18)
    pygame.draw.rect(screen, BORDER, card, 2, border_radius=18)
    screen.blit(surf, rect)

def draw_text(text: str, font, color, cx: int, cy: int):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=(cx, cy)))

def draw_button(rect: pygame.Rect, text: str, color, hover: bool = False):
    shade = tuple(max(0, c - 35) for c in color)
    pygame.draw.rect(screen, shade if hover else color, rect, border_radius=14)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=14)
    draw_text(text, font_small, BLACK, rect.centerx, rect.centery)

def draw_hearts(lives: int):
    for i in range(3):
        c = DARK_PINK if i < lives else GRAY
        cx = 700 + i * 32
        pygame.draw.circle(screen, c, (cx, 28), 10)

def draw_score_badge(score: int, total: int):
    draw_text(f"Score: {score}/{total}", font_small, YELLOW, 90, 28)

def draw_input_box(typed: str, active: bool, shake: int = 0):
    bw, bh = 420, 64
    bx = (WIDTH - bw) // 2 + (random.randint(-4, 4) if shake else 0)
    by = 380
    rect = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(screen, WHITE, rect, border_radius=12)
    pygame.draw.rect(screen, DARK_PINK if active else BORDER, rect, 3, border_radius=12)
    surf = font_input.render(typed.upper(), True, BLACK)
    screen.blit(surf, surf.get_rect(center=rect.center))
    if active and (pygame.time.get_ticks() // 500) % 2 == 0:
        cx = rect.centerx + surf.get_width() // 2 + 4
        pygame.draw.line(screen, BLACK, (cx, by + 12), (cx, by + bh - 12), 2)


def title_screen():
    btn = pygame.Rect(300, 460, 200, 60)
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(mx, my):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        draw_bg()
        draw_text("Meow Spelling!", font_title, DARK_PINK, WIDTH // 2, 60)
        draw_text("Read the clue and type the word!", font_small, BLACK, WIDTH // 2, 108)
        blit_cat(0, WIDTH // 2, 300)
        draw_button(btn, "Play!", GREEN, btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(FPS)


def result_screen(correct: bool, word: str, hint: str):
    btn = pygame.Rect(300, 490, 200, 60)
    cat_idx = 1 if correct else 2
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(mx, my):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        draw_bg()
        blit_cat(cat_idx, WIDTH // 2, 200)
        if correct:
            draw_text("Purr-fect!", font_big, GREEN, WIDTH // 2, 370)
            draw_text(f'"{word.upper()}" - {hint}', font_small, BLACK, WIDTH // 2, 418)
        else:
            draw_text("Oh no!", font_big, RED, WIDTH // 2, 370)
            draw_text(f"The word was:  {word.upper()}", font_med, DARK_PINK, WIDTH // 2, 418)
        draw_button(btn, "Next >>", YELLOW, btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(score: int, total: int):
    btn = pygame.Rect(290, 490, 220, 60)
    cat_idx = 1 if score >= total // 2 else 2
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(mx, my):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        draw_bg()
        blit_cat(cat_idx, WIDTH // 2, 200)
        draw_text("Game Over!", font_big, PURPLE, WIDTH // 2, 370)
        draw_text(f"You got  {score} / {total}  right!", font_med, BLACK, WIDTH // 2, 418)
        if score == total:
            msg, col = "Amazing! You're a spelling cat!", GREEN
        elif score >= total // 2:
            msg, col = "Good job! Keep practising!", YELLOW
        else:
            msg, col = "Keep trying, you can do it!", RED
        draw_text(msg, font_small, col, WIDTH // 2, 456)
        draw_button(btn, "Play Again", PINK, btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(FPS)


def play_round(word: str, hint: str, score: int, round_num: int, lives: int):
    typed = ""
    shake = 0
    message = ""
    msg_col = BLACK
    msg_timer = 0
    speak(word)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and typed:
                    if typed.lower() == word:
                        SND_CORRECT.play()
                        result_screen(True, word, hint)
                        return True, lives
                    else:
                        lives -= 1
                        SND_WRONG.play()
                        shake = 14
                        message = "Try again!" if lives > 0 else ""
                        msg_col = RED
                        msg_timer = 90
                        typed = ""
                        if lives == 0:
                            result_screen(False, word, hint)
                            return False, 0

                elif event.key == pygame.K_BACKSPACE:
                    typed = typed[:-1]

                elif event.unicode.isalpha() and len(typed) < 16:
                    typed += event.unicode.lower()

        draw_bg()
        draw_hearts(lives)
        draw_score_badge(score, TOTAL_ROUNDS)
        draw_text(f"Round {round_num} of {TOTAL_ROUNDS}", font_small, BLACK, WIDTH // 2, 28)

        blit_cat(0, WIDTH // 2, 195)

        hint_rect = pygame.Rect(160, 315, 480, 50)
        pygame.draw.rect(screen, PANEL,  hint_rect, border_radius=10)
        pygame.draw.rect(screen, BORDER, hint_rect, 2, border_radius=10)
        draw_text(hint, font_small, DARK_PINK, WIDTH // 2, 340)

        draw_input_box(typed, True, shake if shake > 0 else 0)
        if shake > 0:
            shake -= 1

        draw_text("Type the word and press  Enter", font_small, GRAY, WIDTH // 2, 462)

        if msg_timer > 0:
            draw_text(message, font_med, msg_col, WIDTH // 2, 500)
            msg_timer -= 1

        pygame.display.flip()
        clock.tick(FPS)


def main():
    while True:
        title_screen()
        score = 0
        lives = 3
        pool = random.sample(WORDS, min(TOTAL_ROUNDS, len(WORDS)))
        for i, (word, hint) in enumerate(pool, 1):
            correct, lives = play_round(word, hint, score, i, lives)
            if correct:
                score += 1
            if lives == 0:
                break
        end_screen(score, TOTAL_ROUNDS)

if __name__ == "__main__":
    main()
