from game.board import TRACK_LENGTH, START_POSITIONS, SAFE_ZONES

class Rules:
    @staticmethod
    def can_move(pawn_pos: int, roll: int) -> bool:
        if pawn_pos == -1:
            return roll == 6
        return (pawn_pos + roll) <= 57

    @staticmethod
    def get_next_position(pawn_pos: int, roll: int) -> int:
        if pawn_pos == -1 and roll == 6:
            return 0
        return pawn_pos + roll

    @staticmethod
    def check_capture(player_color: str, target_global_pos: int, all_players: dict) -> tuple[str, int] | None:
        if target_global_pos in SAFE_ZONES or target_global_pos > 51:
            return None
        
        for color, state in all_players.items():
            if color == player_color:
                continue
            for idx, pos in enumerate(state["pawns"]):
                if pos == -1 or pos > 51:
                    continue
                opp_global = (START_POSITIONS[color] + pos) % TRACK_LENGTH
                if opp_global == target_global_pos:
                    return color, idx
        return None