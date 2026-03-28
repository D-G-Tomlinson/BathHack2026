import pygame
import os

BLACK  = (0,   0,   0)
YELLOW = (229, 178,  93)   # E5B25D - golden
RED    = (176, 123, 172)   # B07BAC - purple

LYRICS = [
    (0,     "Scrabble, Scrabble, Scrabble Cats"),
    (1500,  "Scrabble Cats, Scrabble Cats"),
    (3500,  "Scrabble, Scrabble, Scrabble, Scrabble"),
    (4500,  "Scrabble, Scrabble Cats"),
    (5500,  "MEOW!"),
    (6000,  "Scrabble, Scrabble, Scrabble Cats"),
    (7000,  "Scrabble Cats, Scrabble Cats"),
    (8500,  "Scrabble, Scrabble, Scrabble, Scrabble"),
    (10500, "Scrabble, Scrabble Cats"),
    (11500, "MEOW!"),
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


def _load_cats():
    """Load corner cat images; returns list of (surf, corner)."""
    return [(_load_cat(f), corner) for f, corner in _CAT_FILES]


def _draw_cats(screen, cat_images):
    WIDTH, HEIGHT = screen.get_size()
    for surf, corner in cat_images:
        w_img, h_img = surf.get_size()
        if corner == "topleft":
            pos = (0, 0)
        elif corner == "topright":
            pos = (WIDTH - w_img, 0)
        elif corner == "bottomleft":
            pos = (0, HEIGHT - h_img)
        else:
            pos = (WIDTH - w_img, HEIGHT - h_img)
        screen.blit(surf, pos)


def _draw_button(screen, text, rect, font):
    mouse = pygame.mouse.get_pos()
    hovered = pygame.Rect(rect).collidepoint(mouse)
    colour = YELLOW if hovered else RED
    pygame.draw.rect(screen, colour, rect, border_radius=16)
    pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=16)
    label = font.render(text, True, BLACK)
    lx = rect[0] + (rect[2] - label.get_width()) // 2
    ly = rect[1] + (rect[3] - label.get_height()) // 2
    screen.blit(label, (lx, ly))


def start_screen(screen, clock, cat_images):
    WIDTH, HEIGHT = screen.get_size()
    font_title = pygame.font.SysFont("Comic Sans MS", 100, bold=True)
    font_sub   = pygame.font.SysFont("Comic Sans MS", 40,  bold=True)
    font_btn   = pygame.font.SysFont("Comic Sans MS", 60,  bold=True)

    btn_w, btn_h = 320, 90
    btn_rect = (WIDTH // 2 - btn_w // 2, HEIGHT * 2 // 3, btn_w, btn_h)

    while True:
        events = yield
        screen.fill(BLACK)
        _draw_cats(screen, cat_images)

        title = font_title.render("Scrabble Cats", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))

        sub = font_sub.render("Karaoke Night!", True, RED)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 5 + title.get_height() + 10))

        _draw_button(screen, "Start", btn_rect, font_btn)
        pygame.display.flip()

        for event in events:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(btn_rect).collidepoint(event.pos):
                    return True


def end_screen(screen, clock, cat_images):
    WIDTH, HEIGHT = screen.get_size()
    font_title = pygame.font.SysFont("Comic Sans MS", 90,  bold=True)
    font_sub   = pygame.font.SysFont("Comic Sans MS", 40,  bold=True)
    font_btn   = pygame.font.SysFont("Comic Sans MS", 60,  bold=True)

    btn_w, btn_h = 320, 90
    btn_rect = (WIDTH // 2 - btn_w // 2, HEIGHT * 2 // 3, btn_w, btn_h)

    while True:
        events = yield
        screen.fill(BLACK)
        _draw_cats(screen, cat_images)

        title = font_title.render("Thanks for singing!", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))

        sub = font_sub.render("MEOW!", True, RED)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 5 + title.get_height() + 10))

        _draw_button(screen, "Quit", btn_rect, font_btn)
        pygame.display.flip()

        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(btn_rect).collidepoint(event.pos):
                    return


def _run_song(screen, clock, cat_images):
    WIDTH, HEIGHT = screen.get_size()
    font_normal = pygame.font.SysFont("Comic Sans MS", 80, bold=True)
    font_meow   = pygame.font.SysFont("Comic Sans MS", 120, bold=True)

    try:
        pygame.mixer.music.load("hall_of_the_mountain_king.mp3")
        pygame.mixer.music.play(0)
    except FileNotFoundError:
        pass  # run without audio if file not found

    start_time = pygame.time.get_ticks()
    next_lyric = 0
    active = []

    try:
        while True:
            events = yield
            now     = pygame.time.get_ticks()
            elapsed = now - start_time

            while next_lyric < len(LYRICS) and elapsed >= LYRICS[next_lyric][0]:
                _, word = LYRICS[next_lyric]
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
                    "colour":      RED if is_meow else YELLOW,
                    "enter_time": now,
                    "exit_time":  None,
                    "duration":   duration,
                })
                next_lyric += 1

            active = [w for w in active
                      if w["exit_time"] is None or (now - w["exit_time"]) < ANIM_MS]

            for event in events:
                if event.type == pygame.QUIT:
                    return
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
                dim_colour   = tuple(c // 4 for c in w["colour"])
                surf_dim    = w["font"].render(w["word"], True, dim_colour)
                surf_bright = w["font"].render(w["word"], True, w["colour"])
                y        = HEIGHT // 2 - surf_dim.get_height() // 2
                target_x = WIDTH  // 2 - surf_dim.get_width()  // 2

                if w["exit_time"] is None:
                    progress = min(1.0, (now - w["enter_time"]) / ANIM_MS)
                    x = WIDTH + surf_dim.get_width() + (target_x - WIDTH - surf_dim.get_width()) * ease_out(progress)
                else:
                    progress = min(1.0, (now - w["exit_time"]) / ANIM_MS)
                    x = target_x + (-WIDTH - surf_dim.get_width() - target_x) * ease_out(progress)

                screen.blit(surf_dim, (int(x), y))

                if w["exit_time"] is None:
                    sweep = min(1.0, (now - w["enter_time"]) / w["duration"])
                    highlight_w = int(surf_bright.get_width() * sweep)
                    if highlight_w > 0:
                        screen.blit(surf_bright, (int(x), y),
                                    pygame.Rect(0, 0, highlight_w, surf_bright.get_height()))

            if elapsed > 18000:
                return

            pygame.display.flip()
    finally:
        pygame.mixer.music.stop()


def run_gen(screen, clock):
    """Entry point called by the menu - shows start screen, song, then end screen."""
    cat_images = _load_cats()
    if not (yield from start_screen(screen, clock, cat_images)):
        return
    yield from _run_song(screen, clock, cat_images)
    yield from end_screen(screen, clock, cat_images)


def launch():
    """Run the karaoke mini-game as a standalone window."""
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "0"
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Karaoke Mini Game")
    clock = pygame.time.Clock()
    gen = run_gen(screen, clock)
    next(gen)
    while True:
        try:
            gen.send(pygame.event.get())
        except StopIteration:
            break
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    launch()
