import requests
import json

URL = "https://dgt.eu.pythonanywhere.com/"

def get():
    x = requests.get(URL)
    return x.text

def delete(code):
    requests.delete(URL+"game",params={"code":code})

def delete_all():
    requests.delete(URL+"game")

def get_codes():
    x = requests.get(URL+"game_codes")
    return json.loads(x.text)

def get_game(code):
    x = requests.get(URL+"game",params={"code":code})
    return json.loads(x.text)

def new_game(userid):
    x = requests.post(URL + 'new_game',params={"userid":userid})
    return json.loads(x.text)["code"]

def join_game(code,userid):
    requests.patch(URL+'join_game', params={"code":code,"userid":userid})
    
def make_move(code,userid, new_board, new_rack, new_bag, new_score):
    requests.patch(URL + 'make_move',params={
        "code":code,
        "userid":userid,
        "new_board":new_board,
        "new_rack":new_rack,
        "new_bag":new_bag,
        "new_score":new_score})

def end_game(code, is_quit):
    requests.post(URL + 'end_game',params={"code":code, "quit":str(is_quit)})