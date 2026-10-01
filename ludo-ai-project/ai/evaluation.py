def evaluate_state(state: dict, ai_color: str) -> float:
    score = 0.0
    for color, data in state.items():
        weight = 1.0 if color == ai_color else -1.2
        for pos in data["pawns"]:
            if pos == 57:
                score += 150 * weight
            elif pos == -1:
                score -= 15 * weight
            else:
                score += (pos * 3.0) * weight
    return score
