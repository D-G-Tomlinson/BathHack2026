import pygame as pg
import sys

import traceback
import time

pg.init()
pg.mixer.init()

_info = pg.display.Info()
WIDTH, HEIGHT = _info.current_w, _info.current_h  # native resolution — no scaling

class GameState:
    def __init__(self):
        self.code = ""
        self.userid = ""
        self.effect = None
        self.isPlayer1 = None
    def update(self, code, userid):
        self.code = code
        self.userid = userid
gameState = GameState()

screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)

import states.MainMenu as MM
import states.NewGame as NG
import states.Lobby as LB
import states.JoinGame as JG
import states.Board as BD

states = {"main_menu": MM.functions,"new_game": NG.functions, "lobby": LB.functions,"join_game": JG.functions,"board": BD.functions}
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
                else:
                    draw(state)
            else:
                draw(state)
        except Exception as e:

            traceback.print_exc()
            pg.quit() # possibly check for game and quit
            sys.exit()

