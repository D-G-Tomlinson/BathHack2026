import pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HOVER = (200, 200, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


TITLE_FONT = pg.font.SysFont("centurygothic",72)
FONT = pg.font.SysFont("centurygothic", 48)

info = pg.display.Info()
(width, height) = info.current_w, info.current_h

title_text = TITLE_FONT.render("Waiting for Player 2", True, BLUE)
title_rect = title_text.get_rect(midtop=(width//2,20))

code_text = None
code_rect = title_text.get_rect(midtop=(width//2,height//2))

def update(game, events):
    pass

def draw(game, screen):
    screen.blit(title_text,title_rect)
    screen.blit(code_text,code_rect)

def init(game):
    global code_text
    code_text = TITLE_FONT.render("Code: " + game.code, True, BLUE)

functions = (update, draw, init)