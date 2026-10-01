# game/game_state.py
from game.rules import Rules
from game.board import START_POSITIONS, TRACK_LENGTH

class GameState:
    def __init__(self, mode: str = "1v1_AI", custom_players: list[str] | None = None):
        self.mode = mode
        self.last_roll = None
        self.turn_idx = 0
        self.winner = None
        
        # 1. Custom Player List (Used for Dynamic 2-4 Player LAN Matches)
        if custom_players:
            self.players = list(custom_players)
            self.ai_players = set()
            self.teams = {p: p for p in self.players}
        # 2. Preset Modes
        elif mode == "1v1_AI":
            self.players = ["RED", "YELLOW"]
            self.ai_players = {"YELLOW"}
            self.teams = {"RED": "RED", "YELLOW": "YELLOW"}
        elif mode == "1v1_LOCAL":
            self.players = ["RED", "YELLOW"]
            self.ai_players = set()
            self.teams = {"RED": "RED", "YELLOW": "YELLOW"}
        elif mode == "4P_AI":
            self.players = ["RED", "GREEN", "YELLOW", "BLUE"]
            self.ai_players = {"GREEN", "YELLOW", "BLUE"}
            self.teams = {p: p for p in self.players}
        elif mode == "4P_LOCAL":
            self.players = ["RED", "GREEN", "YELLOW", "BLUE"]
            self.ai_players = set()
            self.teams = {p: p for p in self.players}
        elif mode == "2V2_TEAM":
            self.players = ["RED", "GREEN", "YELLOW", "BLUE"]
            self.ai_players = {"GREEN", "BLUE"}
            self.teams = {"RED": "TEAM_A", "YELLOW": "TEAM_A", "GREEN": "TEAM_B", "BLUE": "TEAM_B"}
        else:
            self.players = ["RED", "YELLOW"]
            self.ai_players = {"YELLOW"}
            self.teams = {"RED": "RED", "YELLOW": "YELLOW"}

        self.state = {
            p: {"pawns": [-1, -1, -1, -1], "is_ai": (p in self.ai_players)}
            for p in self.players
        }

    @property
    def current_player(self) -> str:
        return self.players[self.turn_idx]

    @property
    def is_current_ai(self) -> bool:
        return self.current_player in self.ai_players

    def has_any_valid_move(self) -> bool:
        if self.last_roll is None:
            return False
        return any(Rules.can_move(p, self.last_roll) for p in self.state[self.current_player]["pawns"])

    def switch_turn(self):
        self.turn_idx = (self.turn_idx + 1) % len(self.players)
        self.last_roll = None

    def check_victory(self) -> str | None:
        if self.mode == "2V2_TEAM":
            team_a_won = all(p == 57 for p in self.state["RED"]["pawns"] + self.state["YELLOW"]["pawns"])
            team_b_won = all(p == 57 for p in self.state["GREEN"]["pawns"] + self.state["BLUE"]["pawns"])
            if team_a_won:
                return "TEAM A (RED & YELLOW)"
            if team_b_won:
                return "TEAM B (GREEN & BLUE)"
        else:
            for color in self.players:
                if all(p == 57 for p in self.state[color]["pawns"]):
                    return color
        return None

    def finalize_move(self, pawn_idx: int, target_pos: int):
        color = self.current_player
        self.state[color]["pawns"][pawn_idx] = target_pos

        # Check Captures
        if target_pos <= 51:
            global_pos = (START_POSITIONS[color] + target_pos) % TRACK_LENGTH
            captured = Rules.check_capture(color, global_pos, self.state)
            if captured:
                opp_color, opp_idx = captured
                if not (self.mode == "2V2_TEAM" and self.teams[color] == self.teams[opp_color]):
                    self.state[opp_color]["pawns"][opp_idx] = -1

        won = self.check_victory()
        if won:
            self.winner = won
            return

        # Roll 6 grants another turn
        if self.last_roll != 6:
            self.switch_turn()
        else:
            self.last_roll = None