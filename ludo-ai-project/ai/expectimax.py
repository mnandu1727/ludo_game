import copy
from game.rules import Rules
from ai.evaluation import evaluate_state

class ExpectimaxAI:
    def __init__(self, color: str = "YELLOW", depth: int = 2):
        self.color = color
        self.depth = depth

    def get_best_move(self, game_state, roll: int) -> int | None:
        valid_moves = [
            i for i, pos in enumerate(game_state.state[self.color]["pawns"])
            if Rules.can_move(pos, roll)
        ]
        if not valid_moves:
            return None

        best_score = float('-inf')
        best_pawn = valid_moves[0]

        for pawn_idx in valid_moves:
            temp_state = copy.deepcopy(game_state.state)
            curr_pos = temp_state[self.color]["pawns"][pawn_idx]
            new_pos = Rules.get_next_position(curr_pos, roll)
            temp_state[self.color]["pawns"][pawn_idx] = new_pos
            
            score = self._expectimax(temp_state, depth=self.depth - 1, is_chance=True)
            if score > best_score:
                best_score = score
                best_pawn = pawn_idx

        return best_pawn

    def _expectimax(self, state: dict, depth: int, is_chance: bool) -> float:
        if depth <= 0:
            return evaluate_state(state, self.color)
        if is_chance:
            total = 0.0
            for _ in range(1, 7):
                total += (1.0 / 6.0) * self._expectimax(state, depth - 1, is_chance=False)
            return total
        else:
            return evaluate_state(state, self.color)
