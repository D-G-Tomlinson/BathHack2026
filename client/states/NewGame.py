import pygame as pg

from backend_handler import new_game

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


title_text = TITLE_FONT.render("New Game", True, BLUE)
title_rect = title_text.get_rect(midtop=(width//2,20))

label_text = TITLE_FONT.render("Name: ", True, BLUE)
label_rect = title_text.get_rect(midtop=(width//2,height//2))

userid = ""

username_box_width = 280
username_box_x = (width // 2) - (username_box_width // 2)
username_box = pg.Rect(username_box_x, 120, username_box_width, 40)

username_active = True

cursor_visible = False
cursor_time = 0

username_label_text = INPUT_FONT.render("Enter Username:", True, BLACK)
username_label_rect = username_label_text.get_rect(midright=(username_box.x - 10, username_box.y + 20))

title_text = TITLE_FONT.render("Create New Game", True, BLACK)
title_text_rect = title_text.get_rect(center=(width // 2, 60))


button_rect = pg.Rect((width - 300) // 2, height - 110, 300, 60)
button_text = BUTTON_FONT.render("Generate Join Code", True, BLACK)
button_text_rect = button_text.get_rect(center=button_rect.center)


def draw(game, screen):
    screen.blit(title_text, title_text_rect)

    screen.blit(username_label_text, username_label_rect)
    pg.draw.rect(screen, WHITE, username_box, 0)

    username_surface = INPUT_FONT.render(userid, True, BLACK)
    screen.blit(username_surface,
                (username_box.x + 5, username_box.y + (username_box.height - username_surface.get_height()) // 2))

    # Draw the cursor if it's active
    if username_active and cursor_visible:
        cursor_x = username_box.x + 5 + username_surface.get_width()  # Position the cursor after the text
        pg.draw.line(screen, BLACK, (cursor_x, username_box.y + 5),
                     (cursor_x, username_box.y + username_box.height - 5), 2)

    # Draw the "Generate Join Code" button
    button_color_to_use = WHITE if not button_rect.collidepoint(
        pg.mouse.get_pos()) else HOVER
    pg.draw.rect(screen, button_color_to_use, button_rect)
    screen.blit(button_text, button_text_rect)


def update(game, events):
    global cursor_time
    global cursor_visible
    global username_active
    global userid

    current_time = pg.time.get_ticks()
    if current_time - cursor_time > 500:
        cursor_visible = not cursor_visible
        cursor_time = current_time

    for event in events:
        if event.type == pg.MOUSEBUTTONDOWN:
            username_active = username_box.collidepoint(event.pos)
            if button_rect.collidepoint(event.pos) and game.userid.strip():
                code = new_game(userid)
                game.update(code,userid)
                game.isPlayer1 = True
                return "lobby"
        elif event.type == pg.KEYDOWN and username_active:
            if event.key == pg.K_BACKSPACE:
                userid = userid[:-1]
            elif event.key == pg.K_RETURN:
                code = new_game(userid)
                game.update(code,userid)
                game.isPlayer1 = True
                return "lobby"
            elif event.unicode and event.unicode.isprintable():
                userid += event.unicode


def init(game):
    global cursor_visible
    global cursor_time

    cursor_visible = False
    cursor_time = pg.time.get_ticks()


functions = (update, draw, init)