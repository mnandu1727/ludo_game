def build_step_sequence(color: str, from_pos: int, to_pos: int) -> list[int]:
    if from_pos == -1:
        return [0]
    return list(range(from_pos + 1, to_pos + 1))

class PawnAnimator:
    def __init__(self, speed: float = 0.18):
        self.speed = speed
        self.is_animating = False
        self.active_pawn_info = None
        self.path_coords = []
        self.curr_target_idx = 0
        self.curr_pos = [0.0, 0.0]
        self.on_complete_callback = None

    def start_animation(self, color: str, pawn_idx: int, from_pos: int, to_pos: int, board_ui, on_complete):
        steps = build_step_sequence(color, from_pos, to_pos)
        self.path_coords = []
        start_px, start_py = board_ui.get_pawn_pixel_pos(color, pawn_idx, from_pos)
        self.curr_pos = [float(start_px), float(start_py)]

        for step in steps:
            target_px, target_py = board_ui.get_pawn_pixel_pos(color, pawn_idx, step)
            self.path_coords.append((target_px, target_py))

        self.active_pawn_info = (color, pawn_idx)
        self.curr_target_idx = 0
        self.is_animating = True
        self.on_complete_callback = on_complete

    def update(self):
        if not self.is_animating:
            return

        if self.curr_target_idx >= len(self.path_coords):
            self.finish()
            return

        target_x, target_y = self.path_coords[self.curr_target_idx]
        dx = target_x - self.curr_pos[0]
        dy = target_y - self.curr_pos[1]
        dist = (dx**2 + dy**2) ** 0.5

        if dist < 3.0:
            self.curr_pos[0] = float(target_x)
            self.curr_pos[1] = float(target_y)
            self.curr_target_idx += 1
            if self.curr_target_idx >= len(self.path_coords):
                self.finish()
        else:
            self.curr_pos[0] += dx * self.speed
            self.curr_pos[1] += dy * self.speed

    def finish(self):
        self.is_animating = False
        if self.on_complete_callback:
            cb = self.on_complete_callback
            self.on_complete_callback = None
            cb()
