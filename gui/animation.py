# gui/animation.py
from game.board import OUTER_PATH, HOME_PATHS, HOME_CENTERS, BASE_POSITIONS, START_POSITIONS, TRACK_LENGTH

def build_step_sequence(color: str, from_pos: int, to_pos: int) -> list[int]:
    """Generates the exact list of intermediate step indices."""
    if from_pos == -1:
        # Spawning out of yard directly into base track index 0
        return [0]
    return list(range(from_pos + 1, to_pos + 1))


class PawnAnimator:
    def __init__(self, speed: float = 0.15):
        """
        speed: 0.0 to 1.0 (interpolation step per frame).
        0.15 gives a crisp, responsive hop between tiles.
        """
        self.speed = speed
        self.is_animating = False
        self.active_pawn_info = None  # (color, pawn_idx)
        self.path_coords = []         # List of (px, py) target waypoints
        self.curr_target_idx = 0
        self.curr_pos = [0.0, 0.0]    # [float_x, float_y]
        self.on_complete_callback = None

    def start_animation(self, color: str, pawn_idx: int, from_pos: int, to_pos: int, board_ui, on_complete):
        steps = build_step_sequence(color, from_pos, to_pos)
        self.path_coords = []

        # Current starting pixel coordinate
        start_px, start_py = board_ui.get_pawn_pixel_pos(color, pawn_idx, from_pos)
        self.curr_pos = [float(start_px), float(start_py)]

        # Collect pixel positions for every intermediate square along the route
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

        # Check if reached the current tile waypoint
        if dist < 3.0:
            self.curr_pos[0] = float(target_x)
            self.curr_pos[1] = float(target_y)
            self.curr_target_idx += 1
            if self.curr_target_idx >= len(self.path_coords):
                self.finish()
        else:
            # Linear interpolation (lerp) towards next waypoint
            self.curr_pos[0] += dx * self.speed
            self.curr_pos[1] += dy * self.speed

    def finish(self):
        self.is_animating = False
        if self.on_complete_callback:
            callback = self.on_complete_callback
            self.on_complete_callback = None
            callback()