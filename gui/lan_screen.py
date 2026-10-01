# gui/lan_screen.py
import pygame
from config import SCREEN_WIDTH, WHITE, RED, GREEN, YELLOW, BLUE
from network.network_manager import get_local_ip

COLOR_RGB = {
    "RED": RED,
    "GREEN": GREEN,
    "YELLOW": YELLOW,
    "BLUE": BLUE
}

class LANLobbyScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("Helvetica", 36, bold=True)
        self.font = pygame.font.SysFont("Helvetica", 16)
        self.input_font = pygame.font.SysFont("Helvetica", 20)
        self.btn_font = pygame.font.SysFont("Helvetica", 16, bold=True)
        
        self.local_ip = get_local_ip()
        self.host_ip_input = "127.0.0.1"
        self.active_input = False
        self.status_msg = ""
        self.btn_pressed = None

        self.connected_players = []
        self.is_host = False

        self.card_rect = pygame.Rect(140, 100, 520, 560)
        self.host_btn_rect = pygame.Rect(180, 160, 440, 46)
        self.ip_box_rect = pygame.Rect(180, 260, 440, 44)
        self.join_btn_rect = pygame.Rect(180, 315, 440, 46)
        self.start_game_btn_rect = pygame.Rect(180, 490, 440, 46)
        self.back_btn_rect = pygame.Rect(180, 550, 440, 40)

    def draw_3d_btn(self, rect: pygame.Rect, text: str, color: tuple, is_pressed: bool, enabled: bool = True):
        x, y, w, h = rect
        draw_color = color if enabled else (70, 75, 88)
        press = (3 if is_pressed else 0) if enabled else 0
        shadow = tuple(max(0, int(c * 0.55)) for c in draw_color)
        
        pygame.draw.rect(self.screen, shadow, (x, y + 5 - press, w, h), border_radius=8)
        pygame.draw.rect(self.screen, draw_color, (x, y + press, w, h), border_radius=8)
        if enabled:
            pygame.draw.rect(self.screen, (255, 255, 255, 60), (x, y + press, w, h), 1, border_radius=8)
        
        lbl = self.btn_font.render(text, True, WHITE if enabled else (140, 140, 140))
        self.screen.blit(lbl, lbl.get_rect(center=(x + w // 2, y + press + h // 2)))

    def handle_event(self, event) -> tuple[str, str | None] | None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ip_box_rect.collidepoint(event.pos):
                self.active_input = True
            else:
                self.active_input = False

            if self.host_btn_rect.collidepoint(event.pos) and not self.is_host:
                self.btn_pressed = "HOST"
            elif self.join_btn_rect.collidepoint(event.pos):
                self.btn_pressed = "JOIN"
            elif self.start_game_btn_rect.collidepoint(event.pos) and self.is_host and len(self.connected_players) >= 2:
                self.btn_pressed = "START_MATCH"
            elif self.back_btn_rect.collidepoint(event.pos):
                self.btn_pressed = "BACK"

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.btn_pressed == "HOST" and self.host_btn_rect.collidepoint(event.pos):
                self.btn_pressed = None
                return ("START_HOST", self.local_ip)
            elif self.btn_pressed == "JOIN" and self.join_btn_rect.collidepoint(event.pos):
                self.btn_pressed = None
                return ("START_JOIN", self.host_ip_input.strip())
            elif self.btn_pressed == "START_MATCH" and self.start_game_btn_rect.collidepoint(event.pos):
                self.btn_pressed = None
                return ("TRIGGER_START", None)
            elif self.btn_pressed == "BACK" and self.back_btn_rect.collidepoint(event.pos):
                self.btn_pressed = None
                return ("BACK", None)
            self.btn_pressed = None

        elif event.type == pygame.KEYDOWN and self.active_input:
            if event.key == pygame.K_BACKSPACE:
                self.host_ip_input = self.host_ip_input[:-1]
            elif event.unicode.isprintable() and len(self.host_ip_input) < 18:
                self.host_ip_input += event.unicode
        return None

    def render(self):
        self.screen.fill((18, 22, 32))
        title = self.title_font.render("4-PLAYER LAN LOBBY", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        # Main Panel
        x, y, w, h = self.card_rect
        pygame.draw.rect(self.screen, (10, 12, 18), (x, y + 6, w, h), border_radius=14)
        pygame.draw.rect(self.screen, (28, 34, 50), self.card_rect, border_radius=14)
        pygame.draw.rect(self.screen, (55, 65, 90), self.card_rect, 1, border_radius=14)

        # Host Action
        host_title = f"HOST 4P MATCH (Your IP: {self.local_ip})" if not self.is_host else "SERVER ACTIVE (WAITING FOR PLAYERS)"
        self.draw_3d_btn(self.host_btn_rect, host_title, (0, 130, 250), self.btn_pressed == "HOST", enabled=not self.is_host)

        # Divider
        pygame.draw.line(self.screen, (50, 60, 80), (180, 225), (620, 225), 1)
        or_lbl = self.font.render("- OR JOIN AS CLIENT -", True, (130, 145, 170))
        self.screen.blit(or_lbl, (SCREEN_WIDTH // 2 - or_lbl.get_width() // 2, 235))

        # Join Input
        pygame.draw.rect(self.screen, (20, 24, 34), self.ip_box_rect, border_radius=6)
        border_col = (0, 168, 255) if self.active_input else (50, 58, 76)
        pygame.draw.rect(self.screen, border_col, self.ip_box_rect, 2 if self.active_input else 1, border_radius=6)
        
        ip_txt = self.input_font.render(self.host_ip_input, True, (240, 245, 255))
        self.screen.blit(ip_txt, (self.ip_box_rect.x + 12, self.ip_box_rect.y + 10))

        self.draw_3d_btn(self.join_btn_rect, "CONNECT TO HOST", (36, 175, 80), self.btn_pressed == "JOIN", enabled=not self.is_host)

        # Connected Players Status Tray
        tray_rect = pygame.Rect(180, 380, 440, 95)
        pygame.draw.rect(self.screen, (20, 24, 35), tray_rect, border_radius=8)
        pygame.draw.rect(self.screen, (45, 52, 70), tray_rect, 1, border_radius=8)

        status_header = f"Lobby Slots: ({len(self.connected_players)}/4 Players Connected)"
        self.screen.blit(self.btn_font.render(status_header, True, (200, 210, 230)), (195, 390))

        # Draw player color badges
        if self.connected_players:
            badge_x = 195
            for p_col in self.connected_players:
                pygame.draw.circle(self.screen, COLOR_RGB.get(p_col, WHITE), (badge_x + 8, 435), 8)
                p_lbl = self.font.render(p_col, True, WHITE)
                self.screen.blit(p_lbl, (badge_x + 22, 426))
                badge_x += 105
        else:
            self.screen.blit(self.font.render("No active connections yet.", True, (120, 130, 150)), (195, 426))

        # Host Start Game Button
        can_start = self.is_host and len(self.connected_players) >= 2
        start_txt = f"START MATCH WITH {len(self.connected_players)} PLAYERS" if can_start else "WAITING FOR PLAYERS (MIN 2)..."
        self.draw_3d_btn(self.start_game_btn_rect, start_txt, (255, 152, 0), self.btn_pressed == "START_MATCH", enabled=can_start)

        self.draw_3d_btn(self.back_btn_rect, "BACK TO MAIN MENU", (100, 105, 120), self.btn_pressed == "BACK")

        if self.status_msg:
            s_surf = self.font.render(self.status_msg, True, (255, 193, 7))
            self.screen.blit(s_surf, (SCREEN_WIDTH // 2 - s_surf.get_width() // 2, 625))