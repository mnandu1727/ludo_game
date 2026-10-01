import pygame
import math
from config import WHITE, BLACK, RED, GREEN, YELLOW, BLUE, GRAY
from game.board import (
    OUTER_PATH, HOME_PATHS, HOME_CENTERS, 
    BASE_POSITIONS, START_POSITIONS, SAFE_ZONES, TRACK_LENGTH
)
from game.rules import Rules

COLOR_MAP = {"RED": RED, "GREEN": GREEN, "YELLOW": YELLOW, "BLUE": BLUE}

class GameScreen:
    def __init__(self, screen, board_origin=(80, 100), board_size=600):
        self.screen = screen
        self.ox, self.oy = board_origin
        self.board_size = board_size
        self.cell_size = board_size // 15
        self.font = pygame.font.SysFont("Helvetica", 16, bold=True)
        # Cross-platform font selection (macOS Apple Symbols / Arial / Default)
        self.star_font = pygame.font.SysFont("Apple Symbols", 22) if "Apple Symbols" in pygame.font.get_fonts() else pygame.font.SysFont("Arial", 20, bold=True)

    def grid_to_pixel(self, col: float, row: float) -> tuple[int, int]:
        return int(self.ox + col * self.cell_size + self.cell_size / 2), int(self.oy + row * self.cell_size + self.cell_size / 2)

    def get_pawn_pixel_pos(self, color: str, pawn_idx: int, step_pos: int) -> tuple[int, int]:
        if step_pos == -1:
            col, row = BASE_POSITIONS[color][pawn_idx]
            return int(self.ox + col * self.cell_size), int(self.oy + row * self.cell_size)
        if step_pos < 52:
            global_idx = (START_POSITIONS[color] + step_pos) % TRACK_LENGTH
            return self.grid_to_pixel(*OUTER_PATH[global_idx])
        if 52 <= step_pos <= 56:
            return self.grid_to_pixel(*HOME_PATHS[color][step_pos - 52])
        return self.grid_to_pixel(*HOME_CENTERS[color])

    def draw_base_corner(self, start_col: int, start_row: int, color: tuple, bg_color: str):
        x = self.ox + start_col * self.cell_size
        y = self.oy + start_row * self.cell_size
        size = 6 * self.cell_size
        pygame.draw.rect(self.screen, color, (x, y, size, size))
        pad = int(self.cell_size * 0.8)
        pygame.draw.rect(self.screen, WHITE, (x + pad, y + pad, size - 2 * pad, size - 2 * pad), border_radius=8)
        for col, row in BASE_POSITIONS[bg_color]:
            px = int(self.ox + col * self.cell_size)
            py = int(self.oy + row * self.cell_size)
            pygame.draw.circle(self.screen, color, (px, py), int(self.cell_size * 0.35))
            pygame.draw.circle(self.screen, BLACK, (px, py), int(self.cell_size * 0.35), 2)

    def draw_center_triangle(self):
        cx, cy = self.ox + 7.5 * self.cell_size, self.oy + 7.5 * self.cell_size
        tl = (self.ox + 6 * self.cell_size, self.oy + 6 * self.cell_size)
        tr = (self.ox + 9 * self.cell_size, self.oy + 6 * self.cell_size)
        bl = (self.ox + 6 * self.cell_size, self.oy + 9 * self.cell_size)
        br = (self.ox + 9 * self.cell_size, self.oy + 9 * self.cell_size)
        pygame.draw.polygon(self.screen, RED, [(cx, cy), tl, bl])
        pygame.draw.polygon(self.screen, GREEN, [(cx, cy), tl, tr])
        pygame.draw.polygon(self.screen, YELLOW, [(cx, cy), tr, br])
        pygame.draw.polygon(self.screen, BLUE, [(cx, cy), bl, br])

    def draw_grid_tracks(self):
        for row in range(15):
            for col in range(15):
                if (col < 6 and row < 6) or (col > 8 and row < 6) or (col < 6 and row > 8) or (col > 8 and row > 8) or (6 <= col <= 8 and 6 <= row <= 8):
                    continue
                x, y = self.ox + col * self.cell_size, self.oy + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                cell_color = WHITE
                if (col, row) in HOME_PATHS["RED"] or (col, row) == (1, 6): cell_color = RED
                elif (col, row) in HOME_PATHS["GREEN"] or (col, row) == (8, 1): cell_color = GREEN
                elif (col, row) in HOME_PATHS["YELLOW"] or (col, row) == (13, 8): cell_color = YELLOW
                elif (col, row) in HOME_PATHS["BLUE"] or (col, row) == (6, 13): cell_color = BLUE
                pygame.draw.rect(self.screen, cell_color, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                for s_idx in SAFE_ZONES:
                    if (col, row) == OUTER_PATH[s_idx]:
                        star = self.star_font.render("★", True, BLACK)
                        self.screen.blit(star, star.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2)))

    def draw_pulsating_glow(self, center_x: int, center_y: int):
        pulse = (math.sin(pygame.time.get_ticks() * 0.008) + 1.0) / 2.0
        base_radius = int(self.cell_size * 0.38)
        glow_radius = int(base_radius + 4 + pulse * 7)
        alpha = int(100 + pulse * 140)
        dim = (glow_radius + 8) * 2
        glow_surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        center = (dim // 2, dim // 2)
        pygame.draw.circle(glow_surf, (0, 230, 115, max(30, int(alpha * 0.4))), center, glow_radius + 4)
        pygame.draw.circle(glow_surf, (0, 255, 128, alpha), center, glow_radius, width=3)
        self.screen.blit(glow_surf, (center_x - center[0], center_y - center[1]))

    def draw_pawn_circle(self, x: int, y: int, color: str, label_text: str, is_active=False):
        r = int(self.cell_size * 0.38)
        if is_active: pygame.draw.circle(self.screen, (30, 30, 30, 100), (x + 3, y + 4), r + 2)
        pygame.draw.circle(self.screen, BLACK, (x, y), r + 2)
        pygame.draw.circle(self.screen, COLOR_MAP[color], (x, y), r)
        pygame.draw.circle(self.screen, WHITE, (x, y), int(r * 0.55))
        lbl = self.font.render(label_text, True, BLACK)
        self.screen.blit(lbl, lbl.get_rect(center=(x, y)))

    def draw_pawns(self, game_state: dict, current_player: str, last_roll: int | None, animator=None):
        occupied, pawns = {}, []
        for color, pdata in game_state.items():
            for idx, pos in enumerate(pdata["pawns"]):
                if animator and animator.is_animating and animator.active_pawn_info == (color, idx):
                    continue
                px, py = self.get_pawn_pixel_pos(color, idx, pos)
                off = occupied.get((px, py), 0)
                occupied[(px, py)] = off + 1
                dx, dy = px + (off * 4), py + (off * 4)
                eligible = (color == current_player and last_roll is not None and (not animator or not animator.is_animating) and Rules.can_move(pos, last_roll))
                pawns.append((dx, dy, color, str(idx + 1), eligible))
        for dx, dy, color, label, eligible in pawns:
            if eligible: self.draw_pulsating_glow(dx, dy)
        for dx, dy, color, label, eligible in pawns:
            self.draw_pawn_circle(dx, dy, color, label)
        if animator and animator.is_animating:
            c, idx = animator.active_pawn_info
            self.draw_pawn_circle(int(animator.curr_pos[0]), int(animator.curr_pos[1]), c, str(idx + 1), is_active=True)

    def render(self, game_state: dict, current_player: str, last_roll: int | None, animator=None):
        pygame.draw.rect(self.screen, WHITE, (self.ox, self.oy, self.board_size, self.board_size))
        self.draw_base_corner(0, 0, RED, "RED")
        self.draw_base_corner(9, 0, GREEN, "GREEN")
        self.draw_base_corner(9, 9, YELLOW, "YELLOW")
        self.draw_base_corner(0, 9, BLUE, "BLUE")
        self.draw_grid_tracks()
        self.draw_center_triangle()
        pygame.draw.rect(self.screen, BLACK, (self.ox, self.oy, self.board_size, self.board_size), 3)
        self.draw_pawns(game_state, current_player, last_roll, animator)
