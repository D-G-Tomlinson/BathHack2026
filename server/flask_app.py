from flask import Flask, request, abort, jsonify
import random
import datetime
import json

BOARD_SIZE = 10
DEFAULT_BAG = {'a':9,'b':2,'c':2,'d':4,'e':12,'f':2,'g':3,'h':2,'i':9,'j':1,'k':1,'l':9,'m':2,'n':6,'o':8,'p':2,'q':1,'r':6,'s':4,'t':6,'u':4,'v':2,'w':2,'x':1,'y':2,'z':1}
START_RACK_SIZE = 7

class Pieces:
    def __init__(self):
        temp = ""
        for (key, value) in DEFAULT_BAG.items():
            temp += key*value
        self.bag = list(temp)
        random.shuffle(self.bag)
        self.p1 = ""
        for _ in range(START_RACK_SIZE):
            self.p1 += self.bag.pop()
        self.p2 = ""
        for _ in range(START_RACK_SIZE):
            self.p2 += self.bag.pop()

app = Flask(__name__)

games = {}

class Game:
    def __init__(self,p1):
        self.player1Next = True
        self.scores=(0,0)
        self.board=[]
        for _ in range(BOARD_SIZE):
            self.board.append([])
        self.pieces = Pieces()
        self.player1Name = p1
        self.player2Name = None
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def make_new_game(name):
    code = str(random.randint(100000, 999999))
    games[code] = Game(name)
    return code

@app.get('/')
def hello_world():
    return "Scrabble Scrabble Scrabble Cats!"

@app.delete('/game')
def delete_game():
    global games
    todel=request.args.get("delete")
    if todel == None:
        games = {}
        return "Success",200
    try:
        todel = int(todel)
        games.pop(todel)
        return "Success",200
    except:
        abort(403, description="that game doesn't exist")

@app.get('/game_codes')
def get_game_codes():
    return (jsonify(games.keys()),200)

@app.get('/game')
def get_game():
    code = request.args.get('code')
    if code in games:
        return games[code].toJSON(),200
    else:
        abort(403, description="that game: " + code +" doesn't exist")

@app.post('/new_game')
def new_game():
    userid = str(request.args.get("userid"))
    if userid is None:
        abort(403, description="userid is required")
    code = make_new_game(userid)
    return jsonify({"code":code}),200

@app.patch('/join_game')
def join_game():
    userid = str(request.args.get("userid"))
    if userid is None:
        abort(403, description="userid is required")
    code = request.args.get("code")
    if code not in games:
        abort(403, description="code is invalid")
    game = games[code]
    if game.player1Name == userid:
        abort(403, description="userid is already taken")
    game.player2Name = userid
    return "Success",200

@app.patch('make_move')
def make_move():
    # code, userid, new_board, new_rack, new_bag, change in score
    code = request.args.get("code")
    if code not in games:
        abort(403, description="code is invalid")
    game = games[code]
    isP1 = game.player1Next
    userid = str(request.args.get("userid"))
    if (isP1 and not(userid==game.player1Name)) or (not isP1 and not(userid==game.player2Name)):
        abort(403, description="userid is invalid")
    score_change = request.args.get("score_change")
    if score_change.isdecimal() and int(score_change) > 0:
        (a,b) = game.scores
        if isP1:
            a = a + score_change
        else:
            b = b + score_change
        game.scores = (a,b)
    else:
        abort(403, description="score_change is invalid")
    new_board = request.args.get("new_board")
    new_rack = request.args.get("new_rack")
    new_bag = request.args.get("new_bag")
    game.board = new_board
    game.pieces.bag = new_bag
    if isP1:
        game.pieces.p1 = new_rack
    else:
        game.pieces.p2 = new_rack
    game.player1Next = not isP1
    return "Success",200