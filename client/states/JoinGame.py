import pygame as pg

from backend_handler import join_game

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HOVER = (200, 200, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


FONT = pg.font.SysFont("centurygothic", 48)
BUTTON_FONT = pg.font.SysFont("centurygothic", 28)
INPUT_FONT  = pg.font.SysFont("centurygothic", 32)
TITLE_FONT = pg.font.SysFont("centurygothic",72)
TIMER_FONT = pg.font.SysFont("centurygothic", 24)

info = pg.display.Info()
(width, height) = info.current_w, info.current_h

title_text = TITLE_FONT.render("Join Game!", True, BLUE)
title_rect = title_text.get_rect(midtop=(width // 2, 20))

BOX_WIDTH = 150
BOX_HEIGHT = 40
START_X = (width - BOX_WIDTH) // 2
username_box = pg.Rect(START_X, 100, BOX_WIDTH, BOX_HEIGHT)
game_code_box = pg.Rect(START_X, 170, BOX_WIDTH, BOX_HEIGHT)
game_code_text = ""

NONE = 0
USERNAME = 1
CODE = 2

active = NONE

username_label_text = INPUT_FONT.render("Username:", True, BLUE)
username_label_rect = username_label_text.get_rect(midright=(240, 120))
game_code_label_text = INPUT_FONT.render("Game code:", True, BLUE)
game_code_label_rect = game_code_label_text.get_rect(midright=(240, 190))

button_rect = pg.Rect((width - 160) // 2, height - 110, 300, 60)
button_text = INPUT_FONT.render("Join", True, BLUE)
button_text_rect = button_text.get_rect(center=button_rect.center)


error_message = ""

cursor_visible = False
cursor_time = 0


def draw(game, screen):
    screen.blit(title_text, title_rect)
    screen.blit(username_label_text, username_label_rect)
    screen.blit(game_code_label_text, game_code_label_rect)

    pg.draw.rect(screen, WHITE, username_box, 0)
    pg.draw.rect(screen, WHITE, game_code_box, 0)

    button_color_to_use = WHITE if not button_rect.collidepoint(
        pg.mouse.get_pos()) else HOVER
    pg.draw.rect(screen, button_color_to_use, button_rect)
    screen.blit(button_text, button_text_rect)

    username_surface = INPUT_FONT.render(game.userid, True, BLUE)
    screen.blit(username_surface,
                (username_box.x + 5, username_box.y + (username_box.height - username_surface.get_height()) // 2))

    game_code_surface = INPUT_FONT.render(game_code_text, True, BLUE)
    screen.blit(game_code_surface,
                (game_code_box.x + 5,
                 game_code_box.y + (game_code_box.height - game_code_surface.get_height()) // 2))

    error_message_surface = TITLE_FONT.render(error_message, True, RED)
    screen.blit(error_message_surface,
                ((width - error_message_surface.get_width()) // 2,
                 height - error_message_surface.get_height() - 10))
    if active != NONE and cursor_visible:
        if active == USERNAME:
            cursor_x = username_box.x + 5 + username_surface.get_width()
            cursor_y = username_box.y + 5
        else:
            cursor_x = game_code_box.x + 5 + game_code_surface.get_width()
            cursor_y = game_code_box.y + 5
        pg.draw.line(screen, BLUE, (cursor_x, cursor_y), (cursor_x, cursor_y + BOX_HEIGHT - 10), 2)


def update(game, events):
    global cursor_time
    global cursor_visible
    global active

    global game_code_text
    global error_message

    current_time = pg.time.get_ticks()
    if current_time - cursor_time > 500:
        cursor_visible = not cursor_visible
        cursor_time = current_time
    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN:
            if username_box.collidepoint(event.pos):
                active = USERNAME
            elif game_code_box.collidepoint(event.pos):
                active = CODE
            else:
                active = NONE

            if button_rect.collidepoint(event.pos) and game.userid.strip() and len(game_code_text) == 6:
                join_game(game_code_text, game.userid)
                game.isPlayer1 = False
                game.code = game_code_text
                return "board"
        elif event.type == pg.KEYDOWN:
            if active == USERNAME:
                if event.key == pg.K_BACKSPACE:
                    game.userid = game.userid[:-1]
                elif event.key == pg.K_TAB:
                    active = CODE
                elif event.unicode and event.unicode.isprintable():
                    game.userid += event.unicode
            elif active == CODE:
                if event.key == pg.K_BACKSPACE:
                    game_code_text = game_code_text[:-1]
                elif event.key == pg.K_TAB:
                    active = USERNAME
                elif event.key == pg.K_RETURN and game.userid.strip() and len(game_code_text) == 6:
                    join_game(game_code_text, game.userid)
                    game.isPlayer1 = False
                    game.code = game_code_text
                    return "board"
                elif event.unicode and event.unicode.isdigit() and len(game_code_text) < 6:
                    game_code_text += event.unicode
    return "join_game"


def init(game):
    global cursor_visible
    global cursor_time

    cursor_visible = False
    cursor_time = pg.time.get_ticks()

    game.userid = ""
    game.code=""


functions = (update, draw, init)