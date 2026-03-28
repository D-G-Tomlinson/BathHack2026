import pygame
import random
import os

pygame.init()

SCREEN_W, SCREEN_H = 520, 870
TILE_SIZE = 62
TILE_GAP = 8
GRID_COLS = 5
GRID_ROWS = 8
GRID_X = (SCREEN_W - (GRID_COLS * (TILE_SIZE + TILE_GAP) - TILE_GAP)) // 2
GRID_Y = 110

KEY_ROWS = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
]
KEY_SIZE = 38
KEY_GAP = 6
KEY_Y_START = GRID_Y + GRID_ROWS * (TILE_SIZE + TILE_GAP) + 20

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY_BG = (174, 207, 223)
TILE_EMPTY = (255, 255, 255)
TILE_EDGE = (184, 125, 75)
GREEN = (181, 231, 137)
YELLOW = (229, 178, 93)
DARK_GRAY = (184, 125, 75)
KEY_BG = (176, 123, 172)
TEXT_DARK = (30, 30, 30)
TEXT_LIGHT = (255, 255, 255)

CAT_WORDS = [
    "KITTY", "TABBY", "PURRS", "MEOWS", "TIGER",
    "FLUFF", "FURRY", "CLAWS", "PERCH", "PROWL",
    "CHIRP", "SNIFF", "GROOM", "BASKS", "DROOL",
    "HISSY", "TUFTS", "LAZES", "PATCH", "PAWED",
]

dic_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dic.txt")
with open(dic_path) as f:
    VALID_WORDS = {w.strip().upper() for w in f if len(w.strip()) == 5} | set(CAT_WORDS)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("CatWordle - Guess the cat word!")

font_large = pygame.font.SysFont("segoeui", 32, bold=True)
font_tile  = pygame.font.SysFont("segoeui", 36, bold=True)
font_key   = pygame.font.SysFont("segoeui", 18, bold=True)
font_msg   = pygame.font.SysFont("segoeui", 26, bold=True)
font_title = pygame.font.SysFont("segoeui", 42, bold=True)


def new_game():
    word = random.choice(CAT_WORDS)
    return {
        "word": word,
        "guesses": [],
        "current": "",
        "state": "playing",
        "message": "",
        "key_colors": {},
        "hint": f"Hint: it starts with {word[0]}!",
    }


def score_guess(guess, word):
    result = [None] * 5
    remaining = list(word)

    for i, (g, w) in enumerate(zip(guess, word)):
        if g == w:
            result[i] = (g, GREEN)
            remaining[i] = None

    for i, (g, _) in enumerate(zip(guess, word)):
        if result[i] is not None:
            continue
        if g in remaining:
            result[i] = (g, YELLOW)
            remaining[remaining.index(g)] = None
        else:
            result[i] = (g, DARK_GRAY)

    return result


def draw_tile(surface, letter, color_bg, x, y, size=TILE_SIZE, border=TILE_EDGE, reveal=True):
    rect = pygame.Rect(x, y, size, size)
    if reveal and color_bg not in (TILE_EMPTY, None):
        pygame.draw.rect(surface, color_bg, rect, border_radius=6)
    else:
        pygame.draw.rect(surface, TILE_EMPTY, rect, border_radius=6)
        pygame.draw.rect(surface, border, rect, 3, border_radius=6)

    if letter:
        text_color = TEXT_LIGHT if (reveal and color_bg == DARK_GRAY) else TEXT_DARK
        surf = font_tile.render(letter, True, text_color)
        surface.blit(surf, surf.get_rect(center=rect.center))


def draw_grid(surface, game):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = GRID_X + col * (TILE_SIZE + TILE_GAP)
            y = GRID_Y + row * (TILE_SIZE + TILE_GAP)

            if row < len(game["guesses"]):
                scored = score_guess(game["guesses"][row], game["word"])
                letter, color = scored[col]
                draw_tile(surface, letter, color, x, y)
            elif row == len(game["guesses"]) and game["state"] == "playing":
                letter = game["current"][col] if col < len(game["current"]) else ""
                draw_tile(surface, letter, TILE_EMPTY, x, y, reveal=False)
            else:
                draw_tile(surface, "", TILE_EMPTY, x, y, reveal=False)


def draw_keyboard(surface, game):
    for row_idx, row_keys in enumerate(KEY_ROWS):
        total_w = len(row_keys) * (KEY_SIZE + KEY_GAP) - KEY_GAP
        start_x = (SCREEN_W - total_w) // 2
        y = KEY_Y_START + row_idx * (KEY_SIZE + KEY_GAP)

        for ki, key in enumerate(row_keys):
            x = start_x + ki * (KEY_SIZE + KEY_GAP)
            rect = pygame.Rect(x, y, KEY_SIZE, KEY_SIZE)
            color = game["key_colors"].get(key, KEY_BG)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            text_color = TEXT_LIGHT if color in (DARK_GRAY, KEY_BG) else TEXT_DARK
            surf = font_key.render(key, True, text_color)
            surface.blit(surf, surf.get_rect(center=rect.center))


def update_key_colors(game, scored):
    for letter, color in scored:
        current = game["key_colors"].get(letter)
        if current != GREEN and (current != YELLOW or color == GREEN):
            game["key_colors"][letter] = color


def handle_key(game, key_name):
    if game["state"] != "playing":
        return

    if key_name == "BACKSPACE":
        game["current"] = game["current"][:-1]
    elif key_name == "RETURN" or key_name == "KP_ENTER":
        if len(game["current"]) == 5:
            guess = game["current"]
            if guess not in VALID_WORDS:
                game["message"] = "Not in word list!"
                return
            scored = score_guess(guess, game["word"])
            update_key_colors(game, scored)
            game["guesses"].append(guess)
            game["current"] = ""

            if guess == game["word"]:
                game["state"] = "won"
                game["message"] = random.choice([
                    "Purrfect! You're a cat genius!",
                    "Meow-velous! You got it!",
                    "You're the cat's whiskers!",
                    "Paw-some job! Well done!",
                    "Fur-bulous! You nailed it!",
                ])
            elif len(game["guesses"]) >= GRID_ROWS:
                game["state"] = "lost"
                game["message"] = f"It was {game['word']}! Hiss! Try again!"
        else:
            game["message"] = "Meow! Need 5 letters!"
    elif len(key_name) == 1 and key_name.isalpha() and len(game["current"]) < 5:
        game["current"] += key_name.upper()
        game["message"] = ""


def draw(surface, game):
    surface.fill(GRAY_BG)

    title = font_title.render("CatWordle", True, BLACK)
    surface.blit(title, title.get_rect(centerx=SCREEN_W // 2, y=14))

    hint_surf = font_msg.render(game["hint"], True, BLACK)
    surface.blit(hint_surf, hint_surf.get_rect(centerx=SCREEN_W // 2, y=68))

    draw_grid(surface, game)
    draw_keyboard(surface, game)

    if game["message"]:
        msg_surf = font_msg.render(game["message"], True, BLACK)
        surface.blit(msg_surf, msg_surf.get_rect(centerx=SCREEN_W // 2, y=SCREEN_H - 50))

    if game["state"] != "playing":
        hint = font_key.render("Press ENTER or R to play again", True, DARK_GRAY)
        surface.blit(hint, hint.get_rect(centerx=SCREEN_W // 2, y=SCREEN_H - 28))

    pygame.display.flip()


game = new_game()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key).upper()

            if game["state"] != "playing" and key_name in ("RETURN", "KP_ENTER", "R"):
                game = new_game()
            else:
                handle_key(game, key_name)

    draw(screen, game)
    clock.tick(60)

pygame.quit()
