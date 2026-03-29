import array
import math
import os
import random
import subprocess
import threading

import pygame

FPS = 60
ASSETS = os.path.dirname(os.path.abspath(__file__))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = (174, 207, 223)
GOLD = (229, 178, 93)
TAN = (184, 125, 75)
GREEN = (130, 210, 100)
RED = (210, 85, 75)
PURPLE = (176, 123, 172)
GREY = (180, 160, 140)
CREAM = (250, 243, 220)

CAT_FILES = [
    os.path.join(ASSETS, "Images", "Colours", "Brown_cat.png"),
    os.path.join(ASSETS, "Images", "Colours", "White_cat.png"),
    os.path.join(ASSETS, "Images", "Colours", "Grey_cat.png"),
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

os.environ["SDL_RENDER_SCALE_QUALITY"] = "0"
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Meow Spelling!")
clock = pygame.time.Clock()

W, H = screen.get_size()
BASE_W, BASE_H = 800, 600
_s  = min(W / BASE_W, H / BASE_H)
_ox = (W - int(BASE_W * _s)) // 2
_oy = (H - int(BASE_H * _s)) // 2

def sx(v): return int(v * _s)
def px(v): return _ox + int(v * _s)
def py(v): return _oy + int(v * _s)

font_title = pygame.font.SysFont("Comic Sans MS", sx(56), bold=True)
font_big   = pygame.font.SysFont("Comic Sans MS", sx(44), bold=True)
font_med   = pygame.font.SysFont("Comic Sans MS", sx(32), bold=True)
font_small = pygame.font.SysFont("Comic Sans MS", sx(24))
font_input = pygame.font.SysFont("Comic Sans MS", sx(38), bold=True)

CAT_SIZE = sx(180)

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
        try:
            import asyncio
            import edge_tts
            import tempfile

            async def _tts():
                comm = edge_tts.Communicate(text, "en-GB-SoniaNeural")
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    path = f.name
                await comm.save(path)
                return path

            path = asyncio.run(_tts())
            subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 'Add-Type -AssemblyName PresentationCore; '
                 '$mp = New-Object System.Windows.Media.MediaPlayer; '
                 f'$mp.Open([Uri]"file:///{path.replace(chr(92), "/")}"); '
                 '$mp.Play(); '
                 'do { Start-Sleep -Milliseconds 100 } '
                 'while (-not $mp.NaturalDuration.HasTimeSpan -or '
                 '$mp.Position -lt $mp.NaturalDuration.TimeSpan); '
                 '$mp.Close()'],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            os.unlink(path)
        except Exception:
            subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 f'Add-Type -AssemblyName System.Speech; '
                 f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                 f'$v = $s.GetInstalledVoices() | Where-Object {{ $_.VoiceInfo.Culture.Name -eq "en-GB" }} | Select-Object -First 1; '
                 f'if ($v) {{ $s.SelectVoice($v.VoiceInfo.Name) }}; '
                 f'$s.Speak("{text}")'],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
    threading.Thread(target=_run, daemon=True).start()


def draw_bg():
    screen.fill(BG)
    for gx in range(sx(60), W, sx(130)):
        for gy in range(sx(60), H, sx(130)):
            pygame.draw.circle(screen, GOLD, (gx, gy), sx(6))

def blit_cat(index: int, cx: int, cy: int):
    surf = CAT_IMAGES[index]
    rect = surf.get_rect(center=(cx, cy))
    card = rect.inflate(sx(20), sx(20))
    pygame.draw.rect(screen, WHITE, card, border_radius=sx(18))
    pygame.draw.rect(screen, TAN, card, 2, border_radius=sx(18))
    screen.blit(surf, rect)

def draw_text(text: str, font, color, cx: int, cy: int):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=(cx, cy)))

def draw_button(rect: pygame.Rect, text: str, color, hover: bool = False):
    shade = tuple(max(0, c - 35) for c in color)
    pygame.draw.rect(screen, shade if hover else color, rect, border_radius=sx(14))
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=sx(14))
    draw_text(text, font_small, BLACK, rect.centerx, rect.centery)

def draw_hearts(lives: int):
    for i in range(3):
        c = TAN if i < lives else GREY
        cx = px(700) + i * sx(32)
        pygame.draw.circle(screen, c, (cx, py(28)), sx(10))

def draw_score_badge(score: int, total: int):
    draw_text(f"Score: {score}/{total}", font_small, GOLD, px(90), py(28))

def draw_input_box(typed: str, active: bool, shake: int = 0):
    bw = sx(420)
    bh = sx(64)
    bx = (W - bw) // 2 + (random.randint(-sx(4), sx(4)) if shake else 0)
    by = py(380)
    rect = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(screen, WHITE, rect, border_radius=sx(12))
    pygame.draw.rect(screen, TAN if active else TAN, rect, sx(3), border_radius=sx(12))
    surf = font_input.render(typed.upper(), True, BLACK)
    screen.blit(surf, surf.get_rect(center=rect.center))
    if active and (pygame.time.get_ticks() // 500) % 2 == 0:
        cx = rect.centerx + surf.get_width() // 2 + sx(4)
        pygame.draw.line(screen, BLACK, (cx, by + sx(12)), (cx, by + bh - sx(12)), 2)


def title_screen():
    btn = pygame.Rect(px(300), py(460), sx(200), sx(60))
    while True:
        events = yield
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(mx, my):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        draw_bg()
        draw_text("Meow Spelling!", font_title, TAN, W // 2, py(60))
        draw_text("Read the clue and type the word!", font_small, BLACK, W // 2, py(108))
        blit_cat(0, W // 2, py(300))
        draw_button(btn, "Play!", GREEN, btn.collidepoint(mx, my))
        pygame.display.flip()


def result_screen(correct: bool, word: str, hint: str):
    btn = pygame.Rect(px(300), py(490), sx(200), sx(60))
    cat_idx = 1 if correct else 2
    while True:
        events = yield
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(mx, my):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        draw_bg()
        blit_cat(cat_idx, W // 2, py(200))
        if correct:
            draw_text("Purr-fect!", font_big, GREEN, W // 2, py(370))
            draw_text(f'"{word.upper()}" - {hint}', font_small, BLACK, W // 2, py(418))
        else:
            draw_text("Oh no!", font_big, RED, W // 2, py(370))
            draw_text(f"The word was:  {word.upper()}", font_med, TAN, W // 2, py(418))
        draw_button(btn, "Next >>", GOLD, btn.collidepoint(mx, my))
        pygame.display.flip()


def end_screen(score: int, total: int):
    btn = pygame.Rect(px(290), py(490), sx(220), sx(60))
    cat_idx = 1 if score >= total // 2 else 2
    while True:
        events = yield
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and btn.collidepoint(mx, my):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        draw_bg()
        blit_cat(cat_idx, W // 2, py(200))
        draw_text("Game Over!", font_big, PURPLE, W // 2, py(370))
        draw_text(f"You got  {score} / {total}  right!", font_med, BLACK, W // 2, py(418))
        if score == total:
            msg, col = "Amazing! You're a spelling cat!", GREEN
        elif score >= total // 2:
            msg, col = "Good job! Keep practising!", GOLD
        else:
            msg, col = "Keep trying, you can do it!", RED
        draw_text(msg, font_small, col, W // 2, py(456))
        draw_button(btn, "Exit", GOLD, btn.collidepoint(mx, my))
        pygame.display.flip()


def play_round(word: str, hint: str, score: int, round_num: int, lives: int):
    typed = ""
    shake = 0
    message = ""
    msg_col = BLACK
    msg_timer = 0
    speak(word)

    while True:
        events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return None, 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and typed:
                    if typed.lower() == word:
                        SND_CORRECT.play()
                        yield from result_screen(True, word, hint)
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
                            yield from result_screen(False, word, hint)
                            return False, 0

                elif event.key == pygame.K_BACKSPACE:
                    typed = typed[:-1]

                elif event.unicode.isalpha() and len(typed) < 16:
                    typed += event.unicode.lower()

        draw_bg()
        draw_hearts(lives)
        draw_score_badge(score, TOTAL_ROUNDS)
        draw_text(f"Round {round_num} of {TOTAL_ROUNDS}", font_small, BLACK, W // 2, py(28))

        blit_cat(0, W // 2, py(195))

        hint_rect = pygame.Rect(px(160), py(315), sx(480), sx(50))
        pygame.draw.rect(screen, CREAM,  hint_rect, border_radius=sx(10))
        pygame.draw.rect(screen, TAN, hint_rect, 2, border_radius=sx(10))
        draw_text(hint, font_small, TAN, W // 2, py(340))

        draw_input_box(typed, True, shake if shake > 0 else 0)
        if shake > 0:
            shake -= 1

        draw_text("Type the word and press  Enter", font_small, GREY, W // 2, py(462))

        if msg_timer > 0:
            draw_text(message, font_med, msg_col, W // 2, py(500))
            msg_timer -= 1

        pygame.display.flip()


def main():
    yield from title_screen()
    score = 0
    lives = 3
    pool = random.sample(WORDS, min(TOTAL_ROUNDS, len(WORDS)))
    for i, (word, hint) in enumerate(pool, 1):
        correct, lives = yield from play_round(word, hint, score, i, lives)
        if correct is None:
            return
        if correct:
            score += 1
        if lives == 0:
            break
    yield from end_screen(score, TOTAL_ROUNDS)


def run_gen(scr, clk):
    global screen, clock
    screen = scr
    clock = clk
    yield from main()


if __name__ == "__main__":
    gen = run_gen(screen, clock)
    next(gen)
    while True:
        try:
            gen.send(pygame.event.get())
        except StopIteration:
            break
        clock.tick(FPS)
    pygame.quit()
