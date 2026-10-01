import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from database.db import get_user_stats

class HomeScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.user = user_data
        self.title_font = pygame.font.SysFont("Helvetica", 42, bold=True)
        self.btn_font = pygame.font.SysFont("Helvetica", 17, bold=True)
        self.sub_font = pygame.font.SysFont("Helvetica", 12)
        self.stats_font = pygame.font.SysFont("Helvetica", 16, bold=True)
        self.num_font = pygame.font.SysFont("Helvetica", 24, bold=True)
        self.btn_pressed = None

        # Mode Cartridges
        self.modes = [
            ("1v1_AI", "⚡ 1v1 DUEL VS AI", "Instant match vs Expectimax Bot", (0, 130, 255), pygame.Rect(80, 275, 305, 68)),
            ("4P_AI", "👑 4-PLAYER SQUAD AI", "Play with 3 Intelligent Bots", (255, 140, 0), pygame.Rect(415, 275, 305, 68)),
            ("1v1_LOCAL", "👥 1v1 PASS & PLAY", "Local Match on Same PC", (38, 194, 129), pygame.Rect(80, 360, 305, 68)),
            ("4P_LOCAL", "🎉 4-PLAYER PARTY", "Local 4 Players on Same PC", (156, 39, 176), pygame.Rect(415, 360, 305, 68)),
            ("LAN_MODE", "🌐 PLAY WITH FRIENDS (ONLINE / WI-FI)", "Join or Host Cross-Network Multiplayer Room", (0, 180, 216), pygame.Rect(80, 445, 640, 72)),
        ]
        self.logout_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 545, 200, 44)
        self.refresh_stats()

    def refresh_stats(self):
        updated = get_user_stats(self.user["id"])
        if updated:
            self.user = updated

    def draw_floating_background_dice(self):
        ticks = pygame.time.get_ticks()
        mx, my = pygame.mouse.get_pos()
        dx = (mx - SCREEN_WIDTH // 2) * 0.02
        dy = (my - SCREEN_HEIGHT // 2) * 0.02

        dice = [
            (80 + dx, 120 + dy, 42, 0.0012, (235, 47, 60)),
            (720 - dx, 140 - dy, 48, 0.0016, (255, 180, 0)),
            (730 - dx, 680 - dy, 52, 0.0010, (30, 144, 255)),
            (70 + dx, 700 + dy, 44, 0.0014, (38, 194, 129)),
        ]
        for bx, by, sz, spd, col in dice:
            cy = by + math.sin(ticks * spd + bx) * 12
            cx = bx
            top = [(cx, cy - sz * 0.5), (cx + sz * 0.86, cy), (cx, cy + sz * 0.5), (cx - sz * 0.86, cy)]
            left = [(cx - sz * 0.86, cy), (cx, cy + sz * 0.5), (cx, cy + sz * 1.5), (cx - sz * 0.86, cy + sz)]
            right = [(cx + sz * 0.86, cy), (cx, cy + sz * 0.5), (cx, cy + sz * 1.5), (cx + sz * 0.86, cy + sz)]
            pygame.draw.polygon(self.screen, tuple(int(v * 0.6) for v in col), left)
            pygame.draw.polygon(self.screen, tuple(int(v * 0.8) for v in col), right)
            pygame.draw.polygon(self.screen, tuple(min(255, int(v * 1.15)) for v in col), top)
            pygame.draw.polygon(self.screen, (255, 255, 255, 40), top, 1)

    def draw_3d_btn(self, rect: pygame.Rect, title: str, subtitle: str, color, is_hovered: bool, is_pressed: bool):
        x, y, w, h = rect
        press = 3 if is_pressed else 0
        depth = 6 - press

        shadow_col = tuple(max(0, int(c * 0.45)) for c in color)
        pygame.draw.rect(self.screen, shadow_col, (x, y + depth, w, h), border_radius=14)

        btn_col = tuple(min(255, int(c * (1.18 if is_hovered else 1.0))) for c in color)
        top_rect = pygame.Rect(x, y + press, w, h)
        pygame.draw.rect(self.screen, btn_col, top_rect, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255, 70), top_rect, width=1, border_radius=14)

        t_surf = self.btn_font.render(title, True, (255, 255, 255))
        self.screen.blit(t_surf, (top_rect.centerx - t_surf.get_width() // 2, top_rect.y + (12 if subtitle else 13)))
        if subtitle:
            s_surf = self.sub_font.render(subtitle, True, (230, 240, 255))
            self.screen.blit(s_surf, (top_rect.centerx - s_surf.get_width() // 2, top_rect.y + 38))

    def handle_event(self, event) -> tuple[str, str | None] | None:
        mpos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, _, _, _, rect in self.modes:
                if rect.collidepoint(mpos):
                    self.btn_pressed = key
            if self.logout_btn_rect.collidepoint(mpos):
                self.btn_pressed = "LOGOUT"

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for key, _, _, _, rect in self.modes:
                if self.btn_pressed == key and rect.collidepoint(event.pos):
                    self.btn_pressed = None
                    return ("START_GAME", key)
            if self.btn_pressed == "LOGOUT" and self.logout_btn_rect.collidepoint(event.pos):
                self.btn_pressed = None
                return ("LOGOUT", None)
            self.btn_pressed = None
        return None

    def render(self):
        self.screen.fill((15, 18, 28))
        self.draw_floating_background_dice()

        title = self.title_font.render("LUDO ARCADE", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 22))

        # Modern Player Glass Card
        card = pygame.Rect(80, 80, 640, 165)
        for s in range(8, 0, -2):
            pygame.draw.rect(self.screen, (8, 10, 16), (card.x - s, card.y - s + 6, card.w + s * 2, card.h + s * 2), border_radius=18)
        pygame.draw.rect(self.screen, (24, 30, 46), card, border_radius=16)
        pygame.draw.rect(self.screen, (55, 68, 96), card, 1, border_radius=16)

        # Avatar Ring
        center = (145, 162)
        pygame.draw.circle(self.screen, (0, 150, 255), center, 44)
        pygame.draw.circle(self.screen, (20, 24, 36), center, 40)
        u_init = self.title_font.render(self.user["username"][:1].upper(), True, (255, 215, 0))
        self.screen.blit(u_init, u_init.get_rect(center=center))

        # Username & Badges
        u_name = self.stats_font.render(f"PLAYER: {self.user["username"].upper()}", True, (255, 255, 255))
        self.screen.blit(u_name, (210, 110))

        played = self.user.get("games_played", 0)
        won = self.user.get("games_won", 0)
        win_rate = self.user.get("win_rate", round((won / played * 100), 1) if played > 0 else 0.0)

        # Stat Pods
        stats = [
            ("MATCHES", str(played), (140, 155, 180), 210),
            ("WINS", str(won), (70, 220, 120), 360),
            ("WIN RATE", f"{win_rate}%", (255, 193, 7), 500)
        ]
        for lbl, val, col, px in stats:
            self.screen.blit(self.sub_font.render(lbl, True, (130, 145, 170)), (px, 152))
            self.screen.blit(self.num_font.render(val, True, col), (px, 172))

        # Mode Selection Cartridges
        mpos = pygame.mouse.get_pos()
        for key, m_title, m_sub, col, rect in self.modes:
            self.draw_3d_btn(rect, m_title, m_sub, col, rect.collidepoint(mpos), self.btn_pressed == key)

        self.draw_3d_btn(self.logout_btn_rect, "LOG OUT", "", (80, 85, 100), self.logout_btn_rect.collidepoint(mpos), self.btn_pressed == "LOGOUT")
