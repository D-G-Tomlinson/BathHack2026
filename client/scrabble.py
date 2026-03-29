import json
import time
import backend_handler as bh

BOARD_SIZE = 10
RACK_SIZE  = 7
CENTER     = (4, 4)  

TILE_DATA: dict[str, tuple[int, int]] = {
    " ": (2,  0), "A": (9,  1),  "B": (2,  3),  "C": (2,  3),  "D": (4,  2), "E": (12, 1),  "F": (2,  4),  "G": (3,  2),  "H": (2,  4), "I": (9,  1),  "J": (1,  8),  "K": (1,  5),  "L": (4,  1), "M": (2,  3),  "N": (6,  1),  "O": (8,  1),  "P": (2,  3), "Q": (1, 10),  "R": (6,  1),  "S": (4,  1),  "T": (6,  1), "U": (4,  1),  "V": (2,  4),  "W": (2,  4),  "X": (1,  8), "Y": (2,  4),  "Z": (1, 10),
}


class Tile:

    def __init__(self, letter: str, points: int) -> None:
        self.letter = letter.upper()
        self.points = points

    def __repr__(self) -> str:
        return f"Tile({self.letter!r}, {self.points})"



class Board:
    def __init__(self) -> None:
        self.grid: list[list[Tile | None]] = [
            [None] * BOARD_SIZE for _ in range(BOARD_SIZE)
        ]
        self.first_move_done: bool = False


    def display(self) -> None:
        cr, cc = CENTER
        print("\n    ", end="")
        for c in range(BOARD_SIZE):
            print(f" {c} ", end="")
        print()
        print("   +" + "---" * BOARD_SIZE + "+")
        for r in range(BOARD_SIZE):
            print(f"{r:2} |", end="")
            for c in range(BOARD_SIZE):
                cell = self.grid[r][c]
                if cell is None:
                    symbol = "*" if (r == cr and c == cc) else "."
                    print(f" {symbol} ", end="")
                else:
                    print(f" {cell.letter} ", end="")
            print("|")
        print("   +" + "---" * BOARD_SIZE + "+")
        print(f"      (* = centre square at row {cr}, col {cc})")


    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get(self, row: int, col: int) -> "Tile | None":
        return self.grid[row][col]

    def place(self, row: int, col: int, tile: Tile) -> None:
        self.grid[row][col] = tile

    def covers_center(self, positions: list[tuple[int, int]]) -> bool:
        return CENTER in positions


    def to_list(self) -> list[list[str | None]]:
        return [
            [self.grid[r][c].letter if self.grid[r][c] else None
             for c in range(BOARD_SIZE)]
            for r in range(BOARD_SIZE)
        ]

    def load_from_list(self, data: list[list[str | None]]) -> None:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = data[r][c]
                if cell is not None:
                    letter = cell.upper()
                    points = TILE_DATA.get(letter, (0, 0))[1]
                    self.grid[r][c] = Tile(letter, points)
                else:
                    self.grid[r][c] = None


class Player:

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.rack: list[Tile] = []
        self.score: int = 0

    def show_rack(self) -> None:
        rack_str = ", ".join(f"{t.letter}({t.points})" for t in self.rack)
        print(f"  Your rack: [ {rack_str} ]")


    def rack_from_str(self, rack_str: str) -> None:
        self.rack = [
            Tile(l.upper(), TILE_DATA.get(l.upper(), (0, 0))[1])
            for l in rack_str
        ]

    def rack_to_str(self) -> str:
        return "".join(t.letter for t in self.rack)


    def has_letters(self, letters: list[str]) -> bool:
        available = list(self.rack)
        for letter in letters:
            matched = next((t for t in available if t.letter == letter), None)
            if matched:
                available.remove(matched)
            else:
                blank = next((t for t in available if t.letter == " "), None)
                if blank:
                    available.remove(blank)
                else:
                    return False
        return True

    def remove_letters(self, letters: list[str]) -> list[Tile]:
        used: list[Tile] = []
        for letter in letters:
            matched = next((t for t in self.rack if t.letter == letter), None)
            if matched:
                self.rack.remove(matched)
                used.append(matched)
            else:
                blank = next(t for t in self.rack if t.letter == " ")
                self.rack.remove(blank)
                used.append(Tile(letter, 0))  
        return used

    def add_score(self, points: int) -> None:
        self.score += points


class ScrabbleGame:

    def __init__(self, my_name: str, code: str, is_player1: bool) -> None:
        self.my_name: str  = my_name
        self.code: str = code
        self.is_player1: bool = is_player1
        self.game_over: bool = False

        self.board: Board = Board()
        self.bag_letters: list[str] = []
        self.me: Player = Player(my_name)
        self.opponent_name: str = ""
        self.opponent_score: int = 0
        self.consecutive_passes: int = 0

        state = bh.get_game(code)
        self._load_state(state)


    def _load_state(self, state: dict) -> None:
        self.board = Board()
        raw_board = state["board"]
        if isinstance(raw_board, str):
            raw_board = json.loads(raw_board)
        if raw_board and isinstance(raw_board[0], list) and len(raw_board[0]) == BOARD_SIZE:
            self.board.load_from_list(raw_board)
          
        self.board.first_move_done = state.get("first_move_done", False)

        bag_raw = state["pieces"]["bag"]
        self.bag_letters = list(bag_raw)   

        rack_str = state["pieces"]["p1"] if self.is_player1 else state["pieces"]["p2"]
        self.me.rack_from_str(rack_str)


        scores = state["scores"]
        self.me.score = scores[0] if self.is_player1 else scores[1]
        self.opponent_score = scores[1] if self.is_player1 else scores[0]


        self.opponent_name = (
            state.get("player2Name") if self.is_player1 else state.get("player1Name")
        ) or "Opponent"

        self.consecutive_passes = state.get("consecutive_passes", 0)

    def _push_to_server(self) -> None:
        bh.make_move(
            code = self.code,
            userid = self.my_name,
            new_board = json.dumps(self.board.to_list()),
            new_rack = self.me.rack_to_str(),
            new_bag = "".join(self.bag_letters),
            new_score = self.me.score,
        )
      
    def _wait_for_my_turn(self) -> "dict | str":
        while True:
            state = bh.get_game(self.code)

            if state.get("cancelled", 0) == 2:
                return "QUIT"
            if state.get("cancelled", 0) == 1:
                return "GAME_OVER"

            if state["player1Next"] == self.is_player1:
                return state

            print("  Waiting for opponent...  ", end="\r")
            time.sleep(2)

    def _draw_tiles(self) -> None:
        needed = RACK_SIZE - len(self.me.rack)
        for _ in range(min(needed, len(self.bag_letters))):
            letter = self.bag_letters.pop()
            points = TILE_DATA.get(letter.upper(), (0, 0))[1]
            self.me.rack.append(Tile(letter.upper(), points))

    def _bag_is_empty(self) -> bool:
        return len(self.bag_letters) == 0

    def _get_positions(
        self, row: int, col: int, direction: str, word: str
    ) -> list[tuple[int, int]]:
        positions = []
        for i in range(len(word)):
            r = row + (i if direction == "V" else 0)
            c = col + (i if direction == "H" else 0)
            positions.append((r, c))
        return positions


    def _validate_placement(
        self, row: int, col: int, direction: str, word: str
    ) -> tuple[bool, "str | list[str]"]:

        positions = self._get_positions(row, col, direction, word)

        for r, c in positions:
            if not self.board.in_bounds(r, c):
                return False, f"Word goes out of bounds at ({r}, {c})."

        letters_needed: list[str] = []
        intersects_existing = False

        for i, (r, c) in enumerate(positions):
            existing = self.board.get(r, c)
            if existing is None:
                letters_needed.append(word[i])
            else:
                if existing.letter != word[i]:
                    return (
                        False,
                        f"Conflict at ({r},{c}): board has '{existing.letter}'"
                        f" but word has '{word[i]}'.",
                    )
                intersects_existing = True   

        if not letters_needed:
            return False, "No new tiles would be placed - word already on the board."

        if not self.me.has_letters(letters_needed):
            rack_str = ", ".join(f"{t.letter}({t.points})" for t in self.me.rack)
            return (
                False,
                f"Rack [ {rack_str} ] doesn't have {letters_needed}.",
            )

        if not self.board.first_move_done:
            if not self.board.covers_center(positions):
                cr, cc = CENTER
                return False, f"First word must cover the centre square ({cr}, {cc})."
            if len(word) < 2:
                return False, "First word must be at least 2 letters."
        else:
            if not intersects_existing:
                return (
                    False,
                    "Word must cross through a letter already on the board.\n"
                    "  → e.g. if FAN is vertical at col 4, play a horizontal\n"
                    "         word whose path passes through F, A, or N.",
                )

        return True, letters_needed


    def _calculate_score(
        self, word: str, positions: list[tuple[int, int]]
    ) -> int:
        total = 0
        for i, (r, c) in enumerate(positions):
            existing = self.board.get(r, c)
            if existing:
                total += existing.points
            else:
                total += TILE_DATA.get(word[i], (0, 0))[1]
        return total

    def place_word(
        self, row: int, col: int, direction: str, word: str
    ) -> bool:
        word = word.upper()

        
        valid, result = self._validate_placement(row, col, direction, word)
        if not valid:
            print(f"\n  ✗ Invalid: {result}")
            return False

        letters_needed: list[str] = result
        positions = self._get_positions(row, col, direction, word)

        used_tiles = self.me.remove_letters(letters_needed)
        tile_queue = list(used_tiles)

        for r, c in positions:
            if self.board.get(r, c) is None:
                self.board.place(r, c, tile_queue.pop(0))

        self.board.first_move_done = True
        self.consecutive_passes = 0

        score = self._calculate_score(word, positions)
        self.me.add_score(score)
        print(f"\n  ✓ '{word}' placed!  +{score} pts  "
              f"(your total: {self.me.score})")

        self._draw_tiles()

        self._push_to_server()

        return True

    def pass_turn(self) -> None:
        print(f"\n  {self.my_name} passes.")
        self.consecutive_passes += 1
        self._push_to_server()

    def _check_game_over(self) -> bool:
        if not self.me.rack and self._bag_is_empty():
            self.game_over = True
            return True
        if self.consecutive_passes >= 4:
            self.game_over = True
            return True
        return False

    def _show_final_scores(
        self,
        reason: str = ""
    ) -> None:
        print("\n" + "=" * 45)
        print("  G A M E   O V E R")
        print("=" * 45)
        if reason:
            print(f"\n  {reason}")

        leftover = sum(t.points for t in self.me.rack)
        if leftover:
            self.me.score -= leftover
            tiles_str = ", ".join(t.letter for t in self.me.rack)
            print(f"\n  You: −{leftover} pts (unused: {tiles_str})")

        print("\n  Final Scores:")
        print(f"    {self.my_name:>15}: {self.me.score} pts")
        print(f"    {self.opponent_name:>15}: {self.opponent_score} pts")

        if self.me.score > self.opponent_score:
            print("\n  🏆  You win!")
        elif self.opponent_score > self.me.score:
            print(f"\n  🏆  {self.opponent_name} wins!")
        else:
            print("\n  It's a TIE!")


    def _get_move(self) -> tuple:
        print(f"\n{'─'*45}")
        print(f"  Your turn  |  Bag: {len(self.bag_letters)} tiles")
        print(f"  {self.my_name}: {self.me.score} pts  |  "
              f"{self.opponent_name}: {self.opponent_score} pts")
        self.me.show_rack()
        print()
        print("  Commands:")
        print("    play WORD ROW COL DIRECTION")
        print("      e.g.  play FAN  4 4 V   (F at row4 col4 going down ↓)")
        print("      e.g.  play OAF  5 3 H   (O at row5 col3 going right →)")
        print("    pass      skip your turn")
        print("    quit      end the game")
        print(f"{'─'*45}")

        while True:
            raw = input("  > ").strip()
            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd == "quit":
                return ("quit",)

            if cmd == "pass":
                return ("pass",)

            if cmd == "play":
                if len(parts) != 5:
                    print("  Usage: play WORD ROW COL DIRECTION")
                    print("  e.g.   play HELLO 4 4 H")
                    continue
                _, word_in, row_in, col_in, dir_in = parts
                try:
                    row = int(row_in)
                    col = int(col_in)
                except ValueError:
                    print("  ROW and COL must be numbers 0–9.")
                    continue
                direction = dir_in.upper()
                if direction not in ("H", "V"):
                    print("  DIRECTION must be H or V.")
                    continue
                return ("play", word_in.upper(), row, col, direction)

            print(f"  Unknown command '{cmd}'. Use play / pass / quit.")

    def run(self) -> None:

        cr, cc = CENTER
        print("=" * 45)
        print("  10×10 Scrabble — Networked")
        print(f"  {self.my_name}  vs  {self.opponent_name}")
        print(f"  Centre square: row {cr}, col {cc}  (marked * on board)")
        print(f"  Tiles in bag : {len(self.bag_letters)}")
        print("=" * 45)

        while not self.game_over:

            print("\n  Checking server...")
            result = self._wait_for_my_turn()

            if result == "QUIT":
                final = bh.get_game(self.code) 
                if final:
                    self._load_state(final)
                self.board.display()
                self._show_final_scores(reason=f"{self.opponent_name} quit the game.")
                break

            if result == "GAME_OVER":
                self.board.display()
                self._show_final_scores(reason="Game over — tiles or passes exhausted.")
                break

            self._load_state(result)

            self.board.display()

            while True:
                move = self._get_move()

                if move[0] == "quit":
                    print("\n  You quit the game.")
                    self.game_over = True
                    bh.quit(self.code)          
                    self.board.display()
                    self._show_final_scores(reason="You quit.")
                    break

                if move[0] == "pass":
                    self.pass_turn()             
                    break

                if move[0] == "play":
                    _, word, row, col, direction = move
                    if self.place_word(row, col, direction, word):
                        break                  

            if self.game_over:
                break

            if self._check_game_over():
                bh.game_over(self.code)          
                self.board.display()
                self._show_final_scores()
                break
