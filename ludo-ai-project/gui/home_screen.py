import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from database.db import get_user_stats

class HomeScreen:
    def __init__(self, screen, user_data):
        self.screen = screen
        self.user = user_data
        self.title_font = pygame.font.SysFont("Helvetica", 36, bold=True)
        self.font = pygame.font.SysFont("Helvetica", 16)
        self.btn_font = pygame.font.SysFont("Helvetica", 16, bold=True)
        self.stats_font = pygame.font.SysFont("Helvetica", 18, bold=True)
        self.btn_pressed = None

        self.modes = [
            ("1v1_AI", "Duo vs AI", "1 Player vs Expectimax AI", (0, 130, 250), pygame.Rect(90, 290, 290, 60)),
            ("4P_AI", "Squad vs 3 AIs", "1 Player vs 3 Bots", (255, 152, 0), pygame.Rect(420, 290, 290, 60)),
            ("1v1_LOCAL", "Duo Local", "Pass & Play (Same PC)", (40, 167, 69), pygame.Rect(90, 365, 290, 60)),
            ("4P_LOCAL", "Squad Local", "4 Players (Same PC)", (156, 39, 176), pygame.Rect(420, 365, 290, 60)),
            ("LAN_MODE", "🎮 Play with Friends", "Create or Join 6-Digit Room", (0, 180, 216), pygame.Rect(90, 440, 620, 62)),
        ]
        self.logout_btn_rect = pygame.Rect(300, 525, 200, 44)
        self.refresh_stats()

    def refresh_stats(self):
        updated = get_user_stats(self.user["id"])
        if updated:
            self.user = updated

    def draw_3d_card(self, rect: pygame.Rect, bg_color=(28, 33, 48), border_color=(55, 65, 90)):
        x, y, w, h = rect
        pygame.draw.rect(self.screen, (12, 14, 20), (x, y + 6, w, h), border_radius=14)
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=14)
        pygame.draw.rect(self.screen, border_color, rect, width=1, border_radius=14)

    def draw_3d_btn(self, rect: pygame.Rect, title: str, subtitle: str, color, is_hovered: bool, is_pressed: bool):
        x, y, w, h = rect
        press_offset = 3 if is_pressed else 0
        depth = 5 - press_offset
        shadow_col = tuple(max(0, int(c * 0.5)) for c in color)
        pygame.draw.rect(self.screen, shadow_col, (x, y + depth, w, h), border_radius=10)
        btn_col = tuple(min(255, int(c * (1.15 if is_hovered else 1.0))) for c in color)
        top_rect = pygame.Rect(x, y + press_offset, w, h)
        pygame.draw.rect(self.screen, btn_col, top_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255, 60), top_rect, width=1, border_radius=10)
        t_surf = self.btn_font.render(title, True, (255, 255, 255))
        s_surf = pygame.font.SysFont("Helvetica", 12).render(subtitle, True, (230, 230, 230))
        self.screen.blit(t_surf, (top_rect.centerx - t_surf.get_width() // 2, top_rect.y + (12 if subtitle else 14)))
        if subtitle:
            self.screen.blit(s_surf, (top_rect.centerx - s_surf.get_width() // 2, top_rect.y + 34))

    def handle_event(self, event) -> tuple[str, str | None] | None:
        mpos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for key, _, _, _, rect in self.modes:
                if rect.collidepoint(mpos):
                    self.btn_pressed = key
            if self.logout_btn_rect.collidepoint(mpos):
                self.btn_pressed = "LOGOUT"
        elif event.type == pygame.MOUSEBUTTONUP:
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
        self.screen.fill((18, 22, 32))
        title = self.title_font.render("LUDO DASHBOARD", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 35))
        stats_rect = pygame.Rect(120, 95, 560, 165)
        self.draw_3d_card(stats_rect, bg_color=(28, 34, 50))
        u_name = self.title_font.render(f"Player: {self.user['username']}", True, (255, 255, 255))
        self.screen.blit(u_name, (150, 115))
        played = self.user.get("games_played", 0)
        won = self.user.get("games_won", 0)
        win_rate = self.user.get("win_rate", round((won / played * 100), 1) if played > 0 else 0.0)
        self.screen.blit(self.font.render(f"Matches: {played}   |   Wins: {won}", True, (170, 185, 205)), (150, 168))
        rate_col = (70, 220, 120) if win_rate >= 50.0 else (255, 90, 95)
        self.screen.blit(self.stats_font.render(f"Career Win Rate: {win_rate}%", True, rate_col), (150, 205))
        mpos = pygame.mouse.get_pos()
        for key, m_title, m_sub, col, rect in self.modes:
            self.draw_3d_btn(rect, m_title, m_sub, col, rect.collidepoint(mpos), self.btn_pressed == key)
        self.draw_3d_btn(self.logout_btn_rect, "LOG OUT", "", (80, 85, 100), self.logout_btn_rect.collidepoint(mpos), self.btn_pressed == "LOGOUT")
