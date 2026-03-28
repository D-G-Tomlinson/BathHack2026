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

title_text = TITLE_FONT.render("Main Menu", True, BLUE)
title_rect = title_text.get_rect(midtop=(width//2,20))

new_text = TITLE_FONT.render("New Game", True, BLUE)
new_rect = title_text.get_rect(midtop=(width//2,height//2))

join_text = TITLE_FONT.render("Join Game", True, BLUE)
join_rect = title_text.get_rect(midtop=(width//2,int(height*0.7)))

def update(state, events):
    pass

def draw(state,screen):
    screen.blit(title_text,title_rect)

    col_to_use = WHITE if not new_rect.collidepoint(
        pg.mouse.get_pos()) else HOVER
    pg.draw.rect(screen, col_to_use, new_rect, width=0)
    pg.draw.rect(screen, WHITE, new_rect, 2)
    screen.blit(new_text,new_rect)


    col_to_use = WHITE if not join_rect.collidepoint(
        pg.mouse.get_pos()) else HOVER
    pg.draw.rect(screen, col_to_use, join_rect, width=0)
    pg.draw.rect(screen, WHITE, join_rect, 2)
    screen.blit(join_text,join_rect)

def init(state):
    pass

functions = (update, draw, init)