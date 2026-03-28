"""
scrabble.py — Game Logic
=========================
Contains all Scrabble game logic.
No HTTP calls live here — all server communication
goes through backend_handler.py.

Classes:
  Tile          — a single letter tile with point value
  Board         — the 10x10 grid, display, and serialisation
  Player        — local player's rack and score
  ScrabbleGame  — game controller: validation, scoring, turn loop
"""

import json
import time
import backend_handler as bh

# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────

BOARD_SIZE = 10
RACK_SIZE  = 7
CENTER     = (4, 4)   # (row, col) — first word must cover this
BONUS_SQUARES = {(1, 2), (3, 7), (7, 1), (8, 8)}


# letter → (count in bag, point value)
TILE_DATA: dict[str, tuple[int, int]] = {
    " ": (2,  0),
    "A": (9,  1),  "B": (2,  3),  "C": (2,  3),  "D": (4,  2),
    "E": (12, 1),  "F": (2,  4),  "G": (3,  2),  "H": (2,  4),
    "I": (9,  1),  "J": (1,  8),  "K": (1,  5),  "L": (4,  1),
    "M": (2,  3),  "N": (6,  1),  "O": (8,  1),  "P": (2,  3),
    "Q": (1, 10),  "R": (6,  1),  "S": (4,  1),  "T": (6,  1),
    "U": (4,  1),  "V": (2,  4),  "W": (2,  4),  "X": (1,  8),
    "Y": (2,  4),  "Z": (1, 10),
}


# ══════════════════════════════════════════════
# CLASS 1 — Tile
# ══════════════════════════════════════════════

class Tile:
    """A single Scrabble tile — letter + point value."""

    def __init__(self, letter: str, points: int) -> None:
        self.letter = letter.upper()
        self.points = points

    def __repr__(self) -> str:
        return f"Tile({self.letter!r}, {self.points})"


# ══════════════════════════════════════════════
# CLASS 2 — Board
# ══════════════════════════════════════════════

class Board:
    """
    The 10x10 game board.

    grid[r][c] is either:
      None      → empty square
      Tile      → a placed tile

    Also handles converting to/from the format sent to the server:
      to_list()        → list[list[str|None]]  for sending
      load_from_list() → rebuilds Tile objects from server data
    """

    def __init__(self) -> None:
        self.grid: list[list[Tile | None]] = [
            [None] * BOARD_SIZE for _ in range(BOARD_SIZE)
        ]
        self.first_move_done: bool = False

    # ── display ──────────────────────────────

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
                    if (r == cr and c == cc):
                        symbol = "*"
                    elif (r, c) in BONUS_SQUARES:
                        symbol = "+"
                    else:
                        symbol = "."
                    print(f" {symbol} ", end="")
                else:
                    print(f" {cell.letter} ", end="")
            print("|")
        print("   +" + "---" * BOARD_SIZE + "+")
        print(f"      (* = centre square at row {cr}, col {cc})")

    # ── cell access ──────────────────────────

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get(self, row: int, col: int) -> "Tile | None":
        return self.grid[row][col]

    def place(self, row: int, col: int, tile: Tile) -> None:
        self.grid[row][col] = tile

    def covers_center(self, positions: list[tuple[int, int]]) -> bool:
        return CENTER in positions

    # ── server serialisation ─────────────────

    def to_list(self) -> list[list[str | None]]:
        """
        Convert board to list[list[str|None]] for sending to server.
        e.g. [["F", None, None, ...], ["A", None, ...], ...]
        """
        return [
            [self.grid[r][c].letter if self.grid[r][c] else None
             for c in range(BOARD_SIZE)]
            for r in range(BOARD_SIZE)
        ]

    def load_from_list(self, data: list[list[str | None]]) -> None:
        """
        Rebuild Tile objects from server data.
        data is a list[list[str|None]] — letters or None per cell.
        """
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = data[r][c]
                if cell is not None:
                    letter = cell.upper()
                    points = TILE_DATA.get(letter, (0, 0))[1]
                    self.grid[r][c] = Tile(letter, points)
                else:
                    self.grid[r][c] = None


# ══════════════════════════════════════════════
# CLASS 3 — Player
# ══════════════════════════════════════════════

class Player:
    """
    The LOCAL player only.
    Opponent's rack is never stored locally — it stays on the server.
    """

    def __init__(self, name: str) -> None:
        self.name:  str        = name
        self.rack:  list[Tile] = []
        self.score: int        = 0

    # ── display ──────────────────────────────

    def show_rack(self) -> None:
        rack_str = ", ".join(f"{t.letter}({t.points})" for t in self.rack)
        print(f"  Your rack: [ {rack_str} ]")

    # ── rack helpers ─────────────────────────

    def rack_from_str(self, rack_str: str) -> None:
        """Rebuild rack list from a string e.g. 'ETRSONI'."""
        self.rack = [
            Tile(l.upper(), TILE_DATA.get(l.upper(), (0, 0))[1])
            for l in rack_str
        ]

    def rack_to_str(self) -> str:
        """Convert rack to string for sending to server e.g. 'ETRSONI'."""
        return "".join(t.letter for t in self.rack)

    # ── letter checks ─────────────────────────

    def has_letters(self, letters: list[str]) -> bool:
        """
        True if rack contains all letters.
        Blank tiles (" ") substitute for any letter.
        """
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
        """
        Remove and return tiles for the given letters.
        Uses a blank tile if the exact letter isn't in the rack.
        """
        used: list[Tile] = []
        for letter in letters:
            matched = next((t for t in self.rack if t.letter == letter), None)
            if matched:
                self.rack.remove(matched)
                used.append(matched)
            else:
                blank = next(t for t in self.rack if t.letter == " ")
                self.rack.remove(blank)
                used.append(Tile(letter, 0))   # blank used as this letter = 0 pts
        return used

    def add_score(self, points: int) -> None:
        self.score += points


# ══════════════════════════════════════════════
# CLASS 4 — ScrabbleGame
# ══════════════════════════════════════════════

class ScrabbleGame:
    """
    Main game controller — one instance per laptop.

    What lives locally:
      Board       — rebuilt from server at start of every turn
      My rack     — rebuilt from server at start of every turn
      Bag         — list[str], rebuilt from server at start of every turn
      Game logic  — ALL validation, scoring, placement runs locally

    What goes to the server after every move:
      new_board   — list[list[str|None]] → JSON string
      new_rack    — str  e.g. "ETRSONI"
      new_bag     — str  e.g. "ABCDDEEL..."
      new_score   — int  (our TOTAL score, not just the change)

    Server fields we read:
      board              → list[list[str|None]]
      pieces.p1 / p2     → str  (racks)
      pieces.bag         → str  (remaining tiles)
      scores             → [int, int]
      player1Next        → bool  (whose turn)
      player1Name        → str
      player2Name        → str
      cancelled          → int
                            0 = game in progress
                            1 = game over naturally (tiles/passes)
                            2 = a player quit

    NOTE on passes:
      The server requires new_score > 0. For passes, we send the player's
      current total score (unchanged). If the score is 0 and both players
      keep passing, this will fail — a server-side fix is needed to allow
      score=0 through make_move. For now this handles the common case.
    """

    def __init__(self, my_name: str, code: str, is_player1: bool) -> None:
        self.my_name:    str  = my_name
        self.code:       str  = code
        self.is_player1: bool = is_player1
        self.game_over:  bool = False

        # All rebuilt from server each turn
        self.board:              Board     = Board()
        self.bag_letters:        list[str] = []
        self.me:                 Player    = Player(my_name)
        self.opponent_name:      str       = ""
        self.opponent_score:     int       = 0
        self.consecutive_passes: int       = 0

        # Load initial state from server
        state = bh.get_game(code)
        self._load_state(state)

    # ════════════════════════════════════════
    # State sync helpers
    # ════════════════════════════════════════

    def _load_state(self, state: dict) -> None:
        """
        Rebuild ALL local state from a server response dict.

        Conversions:
          board (str or list) → Board with Tile objects
          rack str            → list[Tile]
          bag str             → list[str]  (so we can pop())
        """
        # ── Board ──────────────────────────────────────────────────────
        self.board = Board()
        raw_board = state["board"]
        if isinstance(raw_board, str):
            raw_board = json.loads(raw_board)
        # raw_board may be [[None,...], ...] or [[], [], ...] on first load
        if raw_board and isinstance(raw_board[0], list) and len(raw_board[0]) == BOARD_SIZE:
            self.board.load_from_list(raw_board)
        # else board is still all-None (start of game), which is correct

        self.board.first_move_done = any(self.board.grid[r][c] is not None
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
        )

        # ── Bag ────────────────────────────────────────────────────────
        bag_raw = state["pieces"]["bag"]
        self.bag_letters = list(bag_raw)   # str → list[str] so we can pop()

        # ── My rack ────────────────────────────────────────────────────
        rack_str = state["pieces"]["p1"] if self.is_player1 else state["pieces"]["p2"]
        self.me.rack_from_str(rack_str)

        # ── Scores ─────────────────────────────────────────────────────
        scores = state["scores"]
        self.me.score       = int(scores[0] if self.is_player1 else scores[1])
        self.opponent_score = int(scores[1] if self.is_player1 else scores[0])

        # ── Names ──────────────────────────────────────────────────────
        self.opponent_name = (
            state.get("player2Name") if self.is_player1 else state.get("player1Name")
        ) or "Opponent"

        # ── Flags ──────────────────────────────────────────────────────
        self.consecutive_passes = state.get("consecutive_passes", 0)

    def _push_to_server(self) -> None:
        """
        Push updated board, rack, bag, and total score to server.
        Called after every successful move or pass.

        Sends:
          new_board  → JSON-dumped list[list[str|None]]
          new_rack   → str e.g. "ETRSONI"
          new_bag    → str e.g. "ABCDDEEL..."
          new_score  → int  (our TOTAL accumulated score)
        """
        bh.make_move(
            code      = self.code,
            userid    = self.my_name,
            new_board = json.dumps(self.board.to_list()),
            new_rack  = self.me.rack_to_str(),
            new_bag   = "".join(self.bag_letters),
            new_score = self.me.score,
        )

    # ════════════════════════════════════════
    # Polling — waiting for our turn
    # ════════════════════════════════════════

    def _wait_for_my_turn(self) -> "dict | str":
        """
        Poll the server every 2 seconds until:
          cancelled == 2  → opponent quit          → return "QUIT"
          cancelled == 1  → natural game over      → return "GAME_OVER"
          it's our turn   → player1Next matches us → return state dict

        The server DELETES the game once cancelled != 0, so we capture
        the state before it disappears.
        """
        while True:
            state = bh.get_game(self.code)

            # ── Game ended ────────────────────────────────────────────
            if state.get("cancelled", 0) == 2:
                return "QUIT"
            if state.get("cancelled", 0) == 1:
                return "GAME_OVER"

            # ── Our turn ──────────────────────────────────────────────
            if state["player1Next"] == self.is_player1:
                return state

            # ── Not our turn yet — wait ───────────────────────────────
            print("  Waiting for opponent...  ", end="\r")
            time.sleep(2)

    # ════════════════════════════════════════
    # Bag management
    # ════════════════════════════════════════

    def _draw_tiles(self) -> None:
        """
        Refill our rack up to RACK_SIZE by popping from bag_letters.
        bag_letters is list[str] so pop() works directly.
        """
        needed = RACK_SIZE - len(self.me.rack)
        for _ in range(min(needed, len(self.bag_letters))):
            letter = self.bag_letters.pop()
            points = TILE_DATA.get(letter.upper(), (0, 0))[1]
            self.me.rack.append(Tile(letter.upper(), points))

    def _bag_is_empty(self) -> bool:
        return len(self.bag_letters) == 0

    # ════════════════════════════════════════
    # Position helper
    # ════════════════════════════════════════

    def _get_positions(
        self, row: int, col: int, direction: str, word: str
    ) -> list[tuple[int, int]]:
        """
        List of (row, col) cells that `word` would occupy.
        H = horizontal (same row, cols increase)
        V = vertical   (same col, rows increase)
        """
        positions = []
        for i in range(len(word)):
            r = row + (i if direction == "V" else 0)
            c = col + (i if direction == "H" else 0)
            positions.append((r, c))
        return positions

    # ════════════════════════════════════════
    # Validation
    # ════════════════════════════════════════

    def _validate_placement(
        self, row: int, col: int, direction: str, word: str
    ) -> tuple[bool, "str | list[str]"]:
        """
        Check all Scrabble placement rules.

        Rules:
          1. All cells within the 10x10 board
          2. Occupied cells must match the word's letter (no overwriting)
          3. At least one NEW tile must be placed
          4. We must have the required letters in our rack
          5. Connectivity:
               First move → must cover centre (4,4) and be ≥ 2 letters
               Later moves → word must CROSS THROUGH an existing tile

        Returns:
          (True,  letters_needed)  — legal, letters_needed is what we supply
          (False, error_message)   — illegal, reason why
        """
        positions = self._get_positions(row, col, direction, word)

        # ── Rule 1: in bounds ─────────────────────────────────────────
        for r, c in positions:
            if not self.board.in_bounds(r, c):
                return False, f"Word goes out of bounds at ({r}, {c})."

        # ── Rule 2: collect letters we need + check no conflicts ───────
        letters_needed: list[str] = []
        intersects_existing       = False

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
                intersects_existing = True   # word crosses an existing tile ✓

        # ── Rule 3: at least one new tile ────────────────────────────
        if not letters_needed:
            return False, "No new tiles would be placed — word already on the board."

        # ── Rule 4: rack check ────────────────────────────────────────
        if not self.me.has_letters(letters_needed):
            rack_str = ", ".join(f"{t.letter}({t.points})" for t in self.me.rack)
            return (
                False,
                f"Rack [ {rack_str} ] doesn't have {letters_needed}.",
            )

        # ── Rule 5: connectivity ──────────────────────────────────────
        if not self.board.first_move_done:
            # First move must cover the centre square
            if not self.board.covers_center(positions):
                cr, cc = CENTER
                return False, f"First word must cover the centre square ({cr}, {cc})."
            if len(word) < 2:
                return False, "First word must be at least 2 letters."
        else:
            # Every later word must physically cross an existing tile
            # (being merely adjacent is NOT enough)
            if not intersects_existing:
                return (
                    False,
                    "Word must cross through a letter already on the board.\n"
                    "  → e.g. if FAN is vertical at col 4, play a horizontal\n"
                    "         word whose path passes through F, A, or N.",
                )

        return True, letters_needed

    # ════════════════════════════════════════
    # Scoring
    # ════════════════════════════════════════

    def _calculate_score(
        self, word: str, positions: list[tuple[int, int]]
    ) -> int:
        """
        Sum point values for every letter in the word.
        Cells already on the board → use stored tile value (blank = 0).
        New cells → look up TILE_DATA.
        """
        total = 0
        bonus = 0
        for i, (r, c) in enumerate(positions):
            existing = self.board.get(r, c)
            if existing:
                total += existing.points
            else:
                total += TILE_DATA.get(word[i], (0, 0))[1]
            if (r, c) in BONUS_SQUARES:
                bonus += 2
        if bonus:
            print(f"  ⭐ Bonus square! +{bonus} extra pts")
        return total + bonus
        return total

    # ════════════════════════════════════════
    # Move execution
    # ════════════════════════════════════════

    def place_word(
        self, row: int, col: int, direction: str, word: str
    ) -> bool:
        """
        Validate → place → score → draw → push to server.
        Returns True on success, False if invalid (player retries).
        """
        word = word.upper()

        # Step 1 — validate
        valid, result = self._validate_placement(row, col, direction, word)
        if not valid:
            print(f"\n  ✗ Invalid: {result}")
            return False

        letters_needed: list[str] = result          # type: ignore[assignment]
        positions = self._get_positions(row, col, direction, word)

        # Step 2 — remove tiles from rack
        used_tiles = self.me.remove_letters(letters_needed)
        tile_queue = list(used_tiles)

        # Step 3 — place tiles on board (skip occupied cells)
        for r, c in positions:
            if self.board.get(r, c) is None:
                self.board.place(r, c, tile_queue.pop(0))

        self.board.first_move_done = True
        self.consecutive_passes    = 0

        # Step 4 — score
        score = self._calculate_score(word, positions)
        self.me.add_score(score)
        print(f"\n  ✓ '{word}' placed!  +{score} pts  "
              f"(your total: {self.me.score})")

        # Step 5 — refill rack from bag
        self._draw_tiles()

        # Step 6 — push everything to server
        self._push_to_server()

        return True

    def pass_turn(self) -> None:
        """
        Skip our turn.
        Increments consecutive_passes and pushes to server.
        Score is unchanged — we send our current total.
        """
        print(f"\n  {self.my_name} passes.")
        self.consecutive_passes += 1
        self._push_to_server()

    # ════════════════════════════════════════
    # End-of-game detection
    # ════════════════════════════════════════

    def _check_game_over(self) -> bool:
        """
        Game ends when:
          (a) Rack is empty AND bag is empty, OR
          (b) 4 consecutive passes (both players passed twice)
        """
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
        """Print game over banner and final scores."""
        print("\n" + "=" * 45)
        print("  G A M E   O V E R")
        print("=" * 45)
        if reason:
            print(f"\n  {reason}")

        # Deduct our leftover tile values
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

    # ════════════════════════════════════════
    # Input parsing
    # ════════════════════════════════════════

    def _get_move(self) -> tuple:
        """
        Show prompt and read a command from the player.

        Returns one of:
          ('play', WORD, row, col, direction)
          ('pass',)
          ('quit',)
        """
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
            cmd   = parts[0].lower()

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

    # ════════════════════════════════════════
    # Main game loop
    # ════════════════════════════════════════

    def run(self) -> None:
        """
        Drive the full game.

        Per turn:
        ─────────
        1. Poll server (_wait_for_my_turn)
             "QUIT"      → opponent quit → show scores, stop
             "GAME_OVER" → natural end  → show scores, stop
             state dict  → our turn, load fresh state

        2. Load state from server (board, rack, bag, scores)

        3. Display board

        4. Inner loop — ask until valid move:
             quit  → tell server (cancelled=2), show scores, stop
             pass  → push to server, exit loop
             play  → validate + place + push, exit loop on success

        5. Check if game ended on our end
             True → tell server (cancelled=1), show scores, stop

        6. Repeat from step 1 (waiting for opponent)
        """
        cr, cc = CENTER
        print("=" * 45)
        print("  10×10 Scrabble — Networked")
        print(f"  {self.my_name}  vs  {self.opponent_name}")
        print(f"  Centre square: row {cr}, col {cc}  (marked * on board)")
        print(f"  Tiles in bag : {len(self.bag_letters)}")
        print("=" * 45)

        while not self.game_over:

            # ── Step 1: poll until our turn or game ends ──────────────
            print("\n  Checking server...")
            result = self._wait_for_my_turn()

            if result == "QUIT":
                # Other player quit
                final = bh.get_game(self.code)   # may already be deleted
                if final:
                    self._load_state(final)
                self.board.display()
                self._show_final_scores(reason=f"{self.opponent_name} quit the game.")
                break

            if result == "GAME_OVER":
                # Natural game over triggered by the other side
                self.board.display()
                self._show_final_scores(reason="Game over — tiles or passes exhausted.")
                break

            # ── Step 2: load fresh state ──────────────────────────────
            self._load_state(result)

            # ── Step 3: display board ─────────────────────────────────
            self.board.display()

            # ── Step 4: inner move loop ───────────────────────────────
            while True:
                move = self._get_move()

                if move[0] == "quit":
                    print("\n  You quit the game.")
                    self.game_over = True
                    bh.quit(self.code)           # cancelled = 2 on server
                    self.board.display()
                    self._show_final_scores(reason="You quit.")
                    break

                if move[0] == "pass":
                    self.pass_turn()             # pushes to server inside
                    break

                if move[0] == "play":
                    _, word, row, col, direction = move
                    if self.place_word(row, col, direction, word):
                        break                    # success — exit inner loop
                    # invalid — loop continues, player retries

            if self.game_over:
                break

            # ── Step 5: check if game ended on our end ────────────────
            if self._check_game_over():
                bh.game_over(self.code)          # cancelled = 1 on server
                self.board.display()
                self._show_final_scores()
                break

            # ── Step 6: loop — now opponent's turn ───────────────────
