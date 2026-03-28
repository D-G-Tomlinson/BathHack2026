import pygame as pg
import sys

import traceback
import time

from pandas.core.interchange.from_dataframe import primitive_column_to_ndarray

pg.init()
pg.mixer.init()

WIDTH, HEIGHT = 700, 360

class GameState:
    def __init__(self):
        self.code = None
        self.userid = None
        self.effect = None
    def update(self, code, userid):
        self.code = code
        self.userid = userid
gameState = GameState()

WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN | pg.SCALED)

import states.MainMenu as MM
import states.NewGame as NG

states = {"main_menu": MM.functions,"new_game": NG.functions}
state = "main_menu"

def update(state):
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            if not gameState is None:
                pass # quit game
            pg.quit() # possibly check for game and quit
            sys.exit()
    return states[state][0](gameState,events)

def draw(state):
    screen.fill((0, 0, 0))
    states[state][1](gameState,screen)
    pg.display.flip()

if __name__ == "__main__":
    while True:
        try:
            new_state = update(state)
            if not (new_state is None):
                if state != new_state:
                    states[new_state][2](gameState)
                state = new_state
            draw(state)
        except Exception as e:

            traceback.print_exc()
            pg.quit() # possibly check for game and quit
            sys.exit()

