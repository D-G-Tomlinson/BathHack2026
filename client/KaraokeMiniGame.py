import pygame
import sys
import os

BLACK  = (0,   0,   0)
YELLOW = (229, 178,  93)   # E5B25D - golden
RED    = (176, 123, 172)   # B07BAC - purple

LYRICS = [
    # Verse 1  (0–6s)
    (0,     "Scrabble, Scrabble, Scrabble Cats"),
    (1500,  "Scrabble Cats, Scrabble Cats"),
    (3500,  "Scrabble, Scrabble, Scrabble, Scrabble"),
    (4500,  "Scrabble, Scrabble Cats"),
    (5500,  "MEOW!"),
    # Verse 2  (6–12s)
    (6000,  "Scrabble, Scrabble, Scrabble Cats"),
    (7000,  "Scrabble Cats, Scrabble Cats"),
    (8500,  "Scrabble, Scrabble, Scrabble, Scrabble"),
    (10500, "Scrabble, Scrabble Cats"),
    (11500, "MEOW!"),
    # Verse 3  (12–17s)
    (12000, "Scrabble, Scrabble, Scrabble Cats"),
    (13000, "Scrabble Cats, Scrabble Cats"),
    (14500, "Scrabble, Scrabble, Scrabble, Scrabble"),
    (15500, "Scrabble, Scrabble Cats"),
    (16500, "MEOW!"),
]

ANIM_MS = 200  


def ease_out(t):
    return 1 - (1 - t) ** 2


_HERE = os.path.dirname(os.path.abspath(__file__))
_CAT_SIZE = 240  # pixel size to render each corner cat

_CAT_FILES = [
    ("Images/Brown cat.png",  "topleft"),
    ("Images/Grey cat.png",   "topright"),
    ("Images/Orange cat.png", "bottomleft"),
    ("Images/White cat.png",  "bottomright"),
]


def _load_cat(filename):
    path = os.path.join(_HERE, filename)
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, (_CAT_SIZE, _CAT_SIZE))


def run(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    font_normal = pygame.font.SysFont("Comic Sans MS", 80, bold=True)
    font_meow   = pygame.font.SysFont("Comic Sans MS", 120, bold=True)

    cat_images = [(pygame.transform.smoothscale(_load_cat(f), (_CAT_SIZE, _CAT_SIZE)), corner)
                  for f, corner in _CAT_FILES]

    try:
        pygame.mixer.music.load("hall_of_the_mountain_king.mp3")
        pygame.mixer.music.play(0)
    except FileNotFoundError:
        pass  # run without audio if file not found

    start_time = pygame.time.get_ticks()
    next_lyric = 0
    active = []  # list of word-state dicts

    running = True
    while running:
        clock.tick(60)
        now     = pygame.time.get_ticks()
        elapsed = now - start_time

        # Trigger new words
        while next_lyric < len(LYRICS) and elapsed >= LYRICS[next_lyric][0]:
            _, word = LYRICS[next_lyric]
            # Start exit animation on any word still on screen
            for w in active:
                if w["exit_time"] is None:
                    w["exit_time"] = now
            is_meow = word == "MEOW!"
            if next_lyric + 1 < len(LYRICS):
                duration = LYRICS[next_lyric + 1][0] - LYRICS[next_lyric][0]
            else:
                duration = 1000
            active.append({
                "word":       word,
                "font":       font_meow if is_meow else font_normal,
                "color":      RED if is_meow else YELLOW,
                "enter_time": now,
                "exit_time":  None,
                "duration":   duration,
            })
            next_lyric += 1

        # Drop words that have finished exiting
        active = [w for w in active
                  if w["exit_time"] is None or (now - w["exit_time"]) < ANIM_MS]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        screen.fill(BLACK)

        for surf, corner in cat_images:
            w_img, h_img = surf.get_size()
            if corner == "topleft":
                pos = (0, 0)
            elif corner == "topright":
                pos = (WIDTH - w_img, 0)
            elif corner == "bottomleft":
                pos = (0, HEIGHT - h_img)
            else:  # bottomright
                pos = (WIDTH - w_img, HEIGHT - h_img)
            screen.blit(surf, pos)

        for w in active:
            dim_color   = tuple(c // 4 for c in w["color"])
            surf_dim    = w["font"].render(w["word"], True, dim_color)
            surf_bright = w["font"].render(w["word"], True, w["color"])
            y        = HEIGHT // 2 - surf_dim.get_height() // 2
            target_x = WIDTH  // 2 - surf_dim.get_width()  // 2

            if w["exit_time"] is None:
                # Slide in from the right
                progress = min(1.0, (now - w["enter_time"]) / ANIM_MS)
                x = WIDTH + surf_dim.get_width() + (target_x - WIDTH - surf_dim.get_width()) * ease_out(progress)
            else:
                # Slide out to the left
                progress = min(1.0, (now - w["exit_time"]) / ANIM_MS)
                x = target_x + (-WIDTH - surf_dim.get_width() - target_x) * ease_out(progress)

            # Dim base
            screen.blit(surf_dim, (int(x), y))

            # Bright highlight sweeps left-to-right over the line's duration
            if w["exit_time"] is None:
                sweep = min(1.0, (now - w["enter_time"]) / w["duration"])
                highlight_w = int(surf_bright.get_width() * sweep)
                if highlight_w > 0:
                    screen.blit(surf_bright, (int(x), y),
                                pygame.Rect(0, 0, highlight_w, surf_bright.get_height()))

        if elapsed > 18000:
            running = False

        pygame.display.flip()

    pygame.mixer.music.stop()


def launch():
    """Run the karaoke mini-game as a standalone window."""
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Karaoke Mini Game")
    clock = pygame.time.Clock()
    run(screen, clock)
    pygame.quit()


if __name__ == "__main__":
    launch()
