import pygame
import math
from config import WHITE, BLACK, RED, GREEN, YELLOW, BLUE, GRAY
from game.board import (
    OUTER_PATH, HOME_PATHS, HOME_CENTERS, 
    BASE_POSITIONS, START_POSITIONS, SAFE_ZONES, TRACK_LENGTH
)
from game.rules import Rules

# Modern High-Saturation Arcade Palette
THEME = {
    "RED":    {"primary": (235, 47, 60),  "light": (255, 100, 110), "dark": (140, 15, 25),  "glow": (255, 60, 80)},
    "GREEN":  {"primary": (38, 194, 129), "light": (80, 230, 165),  "dark": (15, 100, 60),  "glow": (46, 213, 115)},
    "YELLOW": {"primary": (255, 180, 0),  "light": (255, 215, 70),  "dark": (160, 100, 0),  "glow": (255, 200, 40)},
    "BLUE":   {"primary": (30, 144, 255), "light": (90, 185, 255),  "dark": (10, 70, 150),  "glow": (0, 168, 255)},
}

class GameScreen:
    def __init__(self, screen, board_origin=(75, 80), board_size=650):
        self.screen = screen
        self.ox, self.oy = board_origin
        self.board_size = board_size
        self.cell_size = board_size // 15
        self.font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.hud_font = pygame.font.SysFont("Helvetica", 16, bold=True)
        self.hud_sub = pygame.font.SysFont("Helvetica", 12)
        self.btn_font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.star_font = pygame.font.SysFont("Arial", 20, bold=True)

        # Header Exit Button
        self.exit_btn_rect = pygame.Rect(self.ox + self.board_size - 100, 22, 100, 36)
        
        # Modal
        self.show_exit_modal = False
        self.modal_rect = pygame.Rect(200, 270, 400, 220)
        self.confirm_exit_btn = pygame.Rect(235, 410, 150, 44)
        self.cancel_exit_btn = pygame.Rect(415, 410, 150, 44)

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

    def draw_3d_board_slab(self):
        x, y, s = self.ox, self.oy, self.board_size
        depth = 14

        # Table Ground Shadow
        for d in range(depth + 14, 0, -3):
            shadow_rect = pygame.Rect(x - d // 2, y + depth - 2, s + d, s + d // 2)
            pygame.draw.rect(self.screen, (10, 12, 18), shadow_rect, border_radius=22)

        # 3D Slab Thickness
        pygame.draw.rect(self.screen, (18, 22, 32), (x, y + depth, s, s), border_radius=18)
        pygame.draw.rect(self.screen, (24, 30, 44), (x, y + depth - 3, s, s), border_radius=18)

        # Premium Wooden / Slate Surface
        pygame.draw.rect(self.screen, (245, 247, 252), (x, y, s, s), border_radius=18)

        # Golden Outer Rim
        pygame.draw.rect(self.screen, (212, 175, 55), (x, y, s, s), width=3, border_radius=18)
        pygame.draw.rect(self.screen, (255, 255, 255, 60), (x + 3, y + 3, s - 6, 2), border_radius=18)

    def draw_3d_base_corner(self, start_col: int, start_row: int, color_key: str):
        x = self.ox + start_col * self.cell_size
        y = self.oy + start_row * self.cell_size
        size = 6 * self.cell_size
        pad = int(self.cell_size * 0.75)
        c = THEME[color_key]

        # Colored Base Housing
        pygame.draw.rect(self.screen, c["dark"], (x, y + 4, size, size), border_radius=12)
        pygame.draw.rect(self.screen, c["primary"], (x, y, size, size), border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255, 80), (x + 2, y + 2, size - 4, 3), border_radius=8)

        # Inner Sunken Tray
        inner_rect = pygame.Rect(x + pad, y + pad, size - 2 * pad, size - 2 * pad)
        pygame.draw.rect(self.screen, (220, 225, 235), (inner_rect.x, inner_rect.y + 3, inner_rect.w, inner_rect.h), border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), inner_rect, border_radius=10)
        pygame.draw.rect(self.screen, (180, 190, 210), inner_rect, 2, border_radius=10)

        # Sunken Pawn Sockets
        for col, row in BASE_POSITIONS[color_key]:
            px = int(self.ox + col * self.cell_size)
            py = int(self.oy + row * self.cell_size)
            r = int(self.cell_size * 0.38)
            # Socket hole
            pygame.draw.circle(self.screen, (190, 195, 210), (px, py + 2), r + 2)
            pygame.draw.circle(self.screen, c["primary"], (px, py), r)
            pygame.draw.circle(self.screen, (255, 255, 255, 90), (px - 2, py - 2), r - 3, width=2)

    def draw_3d_tracks(self):
        for row in range(15):
            for col in range(15):
                if (col < 6 and row < 6) or (col > 8 and row < 6) or \
                   (col < 6 and row > 8) or (col > 8 and row > 8) or \
                   (6 <= col <= 8 and 6 <= row <= 8):
                    continue

                x, y = self.ox + col * self.cell_size, self.oy + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                # Dynamic tile color selection
                cell_color = (255, 255, 255)
                is_home_lane = False
                theme_c = None

                if (col, row) in HOME_PATHS["RED"] or (col, row) == (1, 6):
                    theme_c = THEME["RED"]; is_home_lane = True
                elif (col, row) in HOME_PATHS["GREEN"] or (col, row) == (8, 1):
                    theme_c = THEME["GREEN"]; is_home_lane = True
                elif (col, row) in HOME_PATHS["YELLOW"] or (col, row) == (13, 8):
                    theme_c = THEME["YELLOW"]; is_home_lane = True
                elif (col, row) in HOME_PATHS["BLUE"] or (col, row) == (6, 13):
                    theme_c = THEME["BLUE"]; is_home_lane = True

                if is_home_lane:
                    pygame.draw.rect(self.screen, theme_c["dark"], (x, y + 2, self.cell_size, self.cell_size))
                    pygame.draw.rect(self.screen, theme_c["primary"], rect)
                    pygame.draw.line(self.screen, (255, 255, 255, 70), (x + 1, y + 1), (x + self.cell_size - 1, y + 1), 2)
                else:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)
                    pygame.draw.rect(self.screen, (215, 222, 235), rect, 1)

                # Render Star on Safe Zone
                for s_idx in SAFE_ZONES:
                    if (col, row) == OUTER_PATH[s_idx]:
                        star_shadow = self.star_font.render("★", True, (160, 120, 20))
                        star = self.star_font.render("★", True, (255, 215, 0))
                        self.screen.blit(star_shadow, star_shadow.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
                        self.screen.blit(star, star.get_rect(center=rect.center))

    def draw_3d_center_pyramid(self):
        cx, cy = self.ox + 7.5 * self.cell_size, self.oy + 7.5 * self.cell_size
        tl = (self.ox + 6 * self.cell_size, self.oy + 6 * self.cell_size)
        tr = (self.ox + 9 * self.cell_size, self.oy + 6 * self.cell_size)
        bl = (self.ox + 6 * self.cell_size, self.oy + 9 * self.cell_size)
        br = (self.ox + 9 * self.cell_size, self.oy + 9 * self.cell_size)

        pygame.draw.polygon(self.screen, THEME["RED"]["primary"], [(cx, cy), tl, bl])
        pygame.draw.polygon(self.screen, THEME["GREEN"]["primary"], [(cx, cy), tl, tr])
        pygame.draw.polygon(self.screen, THEME["YELLOW"]["primary"], [(cx, cy), tr, br])
        pygame.draw.polygon(self.screen, THEME["BLUE"]["primary"], [(cx, cy), bl, br])

        # Gold Ridge Bevels
        pygame.draw.line(self.screen, (255, 230, 130), (cx, cy), tl, 2)
        pygame.draw.line(self.screen, (255, 230, 130), (cx, cy), tr, 2)
        pygame.draw.line(self.screen, (255, 230, 130), (cx, cy), bl, 2)
        pygame.draw.line(self.screen, (255, 230, 130), (cx, cy), br, 2)
        
        # Golden Crown Center Gem
        pygame.draw.circle(self.screen, (255, 215, 0), (int(cx), int(cy)), 7)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(cx - 2), int(cy - 2)), 3)

    def draw_pulsating_halo(self, center_x: int, center_y: int, color_key: str):
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks * 0.009) + 1.0) / 2.0
        base_r = int(self.cell_size * 0.40)
        glow_r = int(base_r + 4 + pulse * 9)
        alpha = int(90 + pulse * 150)
        
        glow_surf = pygame.Surface(((glow_r + 10) * 2, (glow_r + 10) * 2), pygame.SRCALPHA)
        center = (glow_r + 10, glow_r + 10)
        
        c = THEME[color_key]["glow"]
        pygame.draw.circle(glow_surf, (*c, int(alpha * 0.35)), center, glow_r + 5)
        pygame.draw.circle(glow_surf, (*c, alpha), center, glow_r, width=3)
        pygame.draw.circle(glow_surf, (255, 255, 255, min(255, alpha + 50)), center, glow_r - 2, width=1)
        self.screen.blit(glow_surf, (center_x - center[0], center_y - center[1]))

    def draw_3d_pawn(self, x: int, y: int, color_key: str, label_text: str, is_active=False):
        r = int(self.cell_size * 0.38)
        c = THEME[color_key]
        elevation = 7 if is_active else 3

        # Realistic Soft Drop Shadow
        shadow_surf = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (15, 20, 30, 120 if is_active else 75), (0, 0, r * 2 + 8, r * 2 - 2))
        self.screen.blit(shadow_surf, (x - r - 4, y - r + elevation + 3))

        # Bottom Extruded Cylinder
        pygame.draw.circle(self.screen, c["dark"], (x, y - elevation + 5), r)

        # Main Crown Cap
        pygame.draw.circle(self.screen, (20, 24, 34), (x, y - elevation), r + 1)
        pygame.draw.circle(self.screen, c["primary"], (x, y - elevation), r)

        # Gloss Surface Highlight
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y - elevation), int(r * 0.58))
        pygame.draw.circle(self.screen, c["light"], (x, y - elevation), int(r * 0.50))

        # Specular Glint
        spec_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(spec_surf, (255, 255, 255, 160), (r // 2, 2, r, r // 2))
        self.screen.blit(spec_surf, (x - r, y - elevation - r))

        # Number
        lbl = self.font.render(label_text, True, (20, 24, 34))
        self.screen.blit(lbl, lbl.get_rect(center=(x, y - elevation)))

    def draw_pawns(self, game_state: dict, current_player: str, last_roll: int | None, animator=None):
        occupied = {}
        pawns_to_draw = []

        for color, pdata in game_state.items():
            for idx, pos in enumerate(pdata["pawns"]):
                if animator and animator.is_animating and animator.active_pawn_info == (color, idx):
                    continue

                px, py = self.get_pawn_pixel_pos(color, idx, pos)
                off = occupied.get((px, py), 0)
                occupied[(px, py)] = off + 1

                dx, dy = px + (off * 4), py + (off * 4)
                eligible = (
                    color == current_player 
                    and last_roll is not None 
                    and (not animator or not animator.is_animating) 
                    and Rules.can_move(pos, last_roll)
                )
                pawns_to_draw.append((dx, dy, color, str(idx + 1), eligible))

        for dx, dy, color, label, eligible in pawns_to_draw:
            if eligible:
                self.draw_pulsating_halo(dx, dy, color)

        for dx, dy, color, label, eligible in pawns_to_draw:
            self.draw_3d_pawn(dx, dy, color, label, is_active=eligible)

        if animator and animator.is_animating:
            c, idx = animator.active_pawn_info
            self.draw_3d_pawn(int(animator.curr_pos[0]), int(animator.curr_pos[1]), c, str(idx + 1), is_active=True)

    def draw_player_hud_cards(self, current_player: str, is_my_turn: bool):
        """Draws top HUD banner with active player turn highlight and glowing badges."""
        badge_w, badge_h = 190, 48
        bx, by = self.ox, 18
        
        c = THEME[current_player]
        # Active Player Card
        pygame.draw.rect(self.screen, (10, 14, 22), (bx, by + 4, badge_w, badge_h), border_radius=10)
        pygame.draw.rect(self.screen, (26, 32, 48), (bx, by, badge_w, badge_h), border_radius=10)
        pygame.draw.rect(self.screen, c["primary"], (bx, by, badge_w, badge_h), 2, border_radius=10)

        # Dot
        pygame.draw.circle(self.screen, c["primary"], (bx + 20, by + badge_h // 2), 10)
        pygame.draw.circle(self.screen, (255, 255, 255), (bx + 20, by + badge_h // 2), 4)

        t_lbl = self.hud_font.render(f"{current_player}'s TURN", True, WHITE)
        self.screen.blit(t_lbl, (bx + 38, by + 8))

        sub_txt = "🎲 YOUR TURN!" if is_my_turn else "Waiting..."
        s_lbl = self.hud_sub.render(sub_txt, True, (70, 220, 120) if is_my_turn else (160, 170, 190))
        self.screen.blit(s_lbl, (bx + 38, by + 28))

    def handle_exit_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.show_exit_modal:
                if self.exit_btn_rect.collidepoint(event.pos):
                    self.show_exit_modal = True
                    return "MODAL_OPENED"
            else:
                if self.confirm_exit_btn.collidepoint(event.pos):
                    self.show_exit_modal = False
                    return "DO_EXIT"
                elif self.cancel_exit_btn.collidepoint(event.pos):
                    self.show_exit_modal = False
                    return "CANCEL_EXIT"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_exit_modal = not self.show_exit_modal
        return None

    def draw_3d_btn(self, rect: pygame.Rect, title: str, color: tuple, is_hovered: bool):
        x, y, w, h = rect
        shadow_col = tuple(max(0, int(c * 0.5)) for c in color)
        pygame.draw.rect(self.screen, shadow_col, (x, y + 3, w, h), border_radius=8)
        btn_col = tuple(min(255, int(c * (1.15 if is_hovered else 1.0))) for c in color)
        pygame.draw.rect(self.screen, btn_col, rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255, 60), rect, 1, border_radius=8)
        lbl = self.btn_font.render(title, True, WHITE)
        self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    def draw_exit_confirmation_modal(self):
        dim = pygame.Surface((800, 800), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 180))
        self.screen.blit(dim, (0, 0))

        x, y, w, h = self.modal_rect
        pygame.draw.rect(self.screen, (10, 12, 18), (x, y + 6, w, h), border_radius=16)
        pygame.draw.rect(self.screen, (26, 32, 48), self.modal_rect, border_radius=16)
        pygame.draw.rect(self.screen, (220, 53, 69), self.modal_rect, 2, border_radius=16)

        title = pygame.font.SysFont("Helvetica", 20, bold=True).render("LEAVE MATCH?", True, WHITE)
        self.screen.blit(title, (x + w // 2 - title.get_width() // 2, y + 32))
        sub = self.hud_sub.render("Match progress will be lost.", True, (160, 175, 200))
        self.screen.blit(sub, (x + w // 2 - sub.get_width() // 2, y + 78))

        mpos = pygame.mouse.get_pos()
        self.draw_3d_btn(self.confirm_exit_btn, "YES, EXIT", (220, 53, 69), self.confirm_exit_btn.collidepoint(mpos))
        self.draw_3d_btn(self.cancel_exit_btn, "CONTINUE", (80, 85, 100), self.cancel_exit_btn.collidepoint(mpos))

    def render(self, game_state: dict, current_player: str, last_roll: int | None, animator=None, is_my_turn=True):
        self.draw_3d_board_slab()
        self.draw_3d_base_corner(0, 0, "RED")
        self.draw_3d_base_corner(9, 0, "GREEN")
        self.draw_3d_base_corner(9, 9, "YELLOW")
        self.draw_3d_base_corner(0, 9, "BLUE")
        self.draw_3d_tracks()
        self.draw_3d_center_pyramid()
        self.draw_pawns(game_state, current_player, last_roll, animator)

        # Header HUD & Exit Button
        self.draw_player_hud_cards(current_player, is_my_turn)
        mpos = pygame.mouse.get_pos()
        self.draw_3d_btn(self.exit_btn_rect, "🚪 EXIT", (210, 45, 60), self.exit_btn_rect.collidepoint(mpos))

        if self.show_exit_modal:
            self.draw_exit_confirmation_modal()