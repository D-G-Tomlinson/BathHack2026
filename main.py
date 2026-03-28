"""
main.py — User-Facing Entry Point
===================================
Run this file on each laptop to play Scrabble.
 
  python main.py
 
You will be asked to:
  1. Enter your name
  2. Create a new game OR join one with a code
 
Files needed in the same folder:
  main.py             ← this file  (you are here)
  scrabble.py         ← all game logic
  backend_handler.py  ← all server communication
"""
 
import time
import backend_handler as bh
from scrabble import ScrabbleGame
 
 
def banner() -> None:
    print()
    print("╔═══════════════════════════════════════════╗")
    print("║        🐱  SCRABBLE CATS  🐱              ║")
    print("║          10x10 Two-Player Game             ║")
    print("╚═══════════════════════════════════════════╝")
    print()
 
 
def rules() -> None:
    print("  HOW TO PLAY")
    print("  ────────────────────────────────────────")
    print("  play WORD ROW COL DIRECTION")
    print("    e.g.  play FAN  4 4 V   <- F at row4,col4 going down")
    print("    e.g.  play OAF  5 3 H   <- O at row5,col3 going right")
    print()
    print("  Rules:")
    print("    * First word must cover centre square (4,4) marked *")
    print("    * Every word after must cross through an existing letter")
    print("    * You can only use letters in your rack")
    print()
    print("  Other commands:")
    print("    pass   -> skip your turn")
    print("    quit   -> end the game early")
    print("  ────────────────────────────────────────")
    print()
 
 
def _create_game(my_name: str) -> tuple:
    """Player 1: create game on server, wait for Player 2 to join."""
    print("  Creating game on server...")
    code = bh.new_game(my_name)
 
    print()
    print("  +─────────────────────────────────+")
    print(f"  |   Your game code:  {code}      |")
    print("  |                                 |")
    print("  |   Share this with your opponent |")
    print("  +─────────────────────────────────+")
    print()
    print("  Waiting for opponent to join", end="", flush=True)
 
    while True:
        state = bh.get_game(code)
        if state.get("player2Name") is not None:
            opponent = state["player2Name"]
            print(f"\n\n  {opponent} joined! Get ready...")
            time.sleep(1)
            return my_name, code, True
        print(".", end="", flush=True)
        time.sleep(2)
 
 
def _join_game(my_name: str) -> tuple:
    """Player 2: enter a code and join an existing game."""
    while True:
        code = input("  Enter game code: ").strip()
        if not code:
            continue
 
        try:
            state = bh.get_game(code)
        except Exception:
            print(f"  Game '{code}' not found. Try again.")
            continue
 
        if state.get("player2Name") is not None:
            print("  That game already has two players. Try another code.")
            continue
 
        bh.join_game(code, my_name)
        opponent = state.get("player1Name", "Opponent")
        print(f"\n  Joined! You are playing against {opponent}.")
        print("  They go first — wait for your turn...")
        time.sleep(1)
        return my_name, code, False
 
 
def setup() -> tuple:
    """
    Full pre-game setup.
    Returns (my_name, code, is_player1).
    """
    banner()
 
    # Check server
    try:
        response = bh.get()
        print(f"  Server: {response}")
    except Exception:
        print("  Cannot reach server. Check your internet connection.")
        raise SystemExit
 
    print()
 
    my_name = input("  Your name: ").strip() or "Player"
 
    print()
    print("  1.  Create a new game  (you go first)")
    print("  2.  Join an existing game")
    print()
 
    while True:
        choice = input("  Enter 1 or 2: ").strip()
        if choice in ("1", "2"):
            break
        print("  Please enter 1 or 2.")
 
    print()
 
    if choice == "1":
        return _create_game(my_name)
    else:
        return _join_game(my_name)
 
 
if __name__ == "__main__":
    my_name, code, is_player1 = setup()
 
    rules()
    input("  Press Enter when ready to start... ")
    print()
 
    game = ScrabbleGame(my_name, code, is_player1)
    game.run()
 
    print()
    print("  Thanks for playing! Goodbye.")
    print()
