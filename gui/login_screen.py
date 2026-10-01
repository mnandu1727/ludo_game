import pygame
import math
from database.auth.auth import login, signup
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("Helvetica", 36, bold=True)
        self.sub_font = pygame.font.SysFont("Helvetica", 13)
        self.label_font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.input_font = pygame.font.SysFont("Helvetica", 18)
        self.btn_font = pygame.font.SysFont("Helvetica", 16, bold=True)
        self.admin_btn_font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.msg_font = pygame.font.SysFont("Helvetica", 13, bold=True)
        
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.msg_color = (255, 90, 95)
        self.user_data = None

        # Main Card Box
        self.card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 210, 75, 420, 590)
        self.u_field_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 110, 350, 44)
        self.p_field_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 190, 350, 44)
        self.login_btn_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 260, 350, 46)
        self.signup_btn_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 320, 350, 46)
        
        # Unmistakable Big Red Admin Button
        self.admin_btn_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 490, 350, 50)
        # Top-Right Header Badge
        self.top_admin_badge = pygame.Rect(SCREEN_WIDTH - 180, 20, 160, 38)
        
        self.btn_pressed = None

    def draw_3d_btn(self, rect: pygame.Rect, text: str, color: tuple, is_hovered: bool):
        x, y, w, h = rect
        shadow_col = tuple(max(0, int(c * 0.5)) for c in color)
        pygame.draw.rect(self.screen, shadow_col, (x, y + 4, w, h), border_radius=10)
        
        btn_col = tuple(min(255, int(c * (1.15 if is_hovered else 1.0))) for c in color)
        pygame.draw.rect(self.screen, btn_col, rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255, 70), rect, 1, border_radius=10)
        
        lbl = self.admin_btn_font.render(text, True, (255, 255, 255))
        self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    def draw_input_field(self, rect: pygame.Rect, text: str, label_title: str, is_active: bool, is_password=False):
        x, y, w, h = rect
        lbl = self.label_font.render(label_title, True, (180, 190, 205))
        self.screen.blit(lbl, (x, y - 20))
        pygame.draw.rect(self.screen, (22, 26, 36), rect, border_radius=8)
        border_col = (0, 168, 255) if is_active else (60, 70, 90)
        pygame.draw.rect(self.screen, border_col, rect, 2 if is_active else 1, border_radius=8)
        display_str = ("●" * len(text)) if is_password else text
        txt_surf = self.input_font.render(display_str, True, (240, 245, 255))
        self.screen.blit(txt_surf, (x + 14, y + 12))

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mpos = event.pos
            # DIRECT ADMIN CHECK ON CLICK
            if self.admin_btn_rect.collidepoint(mpos) or self.top_admin_badge.collidepoint(mpos):
                return "GOTO_ADMIN"
            
            if self.u_field_rect.collidepoint(mpos):
                self.active_field = "username"
            elif self.p_field_rect.collidepoint(mpos):
                self.active_field = "password"
            elif self.login_btn_rect.collidepoint(mpos):
                success, res = login(self.username, self.password)
                if success:
                    self.user_data = res
                    return "HOME"
                self.message = str(res)
                self.msg_color = (255, 80, 80)
            elif self.signup_btn_rect.collidepoint(mpos):
                success, res = signup(self.username, self.password)
                self.message = res
                self.msg_color = (70, 220, 120) if success else (255, 80, 80)

        elif event.type == pygame.KEYDOWN:
            # SHORTCUT KEYS FOR ADMIN
            if event.key == pygame.K_F1:
                return "GOTO_ADMIN"
            elif event.key == pygame.K_TAB:
                self.active_field = "password" if self.active_field == "username" else "username"
            elif event.key == pygame.K_RETURN:
                success, res = login(self.username, self.password)
                if success:
                    self.user_data = res
                    return "HOME"
                self.message = str(res)
                self.msg_color = (255, 80, 80)
            elif event.key == pygame.K_BACKSPACE:
                if self.active_field == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
            else:
                if event.unicode.isprintable():
                    if self.active_field == "username" and len(self.username) < 18:
                        self.username += event.unicode
                    elif self.active_field == "password" and len(self.password) < 24:
                        self.password += event.unicode
        return None

    def render(self):
        self.screen.fill((16, 20, 30))
        mpos = pygame.mouse.get_pos()

        # Top Right Admin Badge
        self.draw_3d_btn(self.top_admin_badge, "🛡️ Admin Portal", (190, 45, 60), self.top_admin_badge.collidepoint(mpos))

        # Panel
        x, y, w, h = self.card_rect
        pygame.draw.rect(self.screen, (10, 12, 18), (x, y + 6, w, h), border_radius=16)
        pygame.draw.rect(self.screen, (28, 34, 48), self.card_rect, border_radius=16)
        pygame.draw.rect(self.screen, (60, 72, 98), self.card_rect, 1, border_radius=16)
        
        title_surf = self.title_font.render("LUDO MASTER", True, (255, 255, 255))
        sub_surf = self.sub_font.render("LOGIN OR SIGN UP TO PLAY", True, (130, 145, 170))
        self.screen.blit(title_surf, (self.card_rect.centerx - title_surf.get_width() // 2, self.card_rect.y + 25))
        self.screen.blit(sub_surf, (self.card_rect.centerx - sub_surf.get_width() // 2, self.card_rect.y + 68))
        
        self.draw_input_field(self.u_field_rect, self.username, "USERNAME", self.active_field == "username")
        self.draw_input_field(self.p_field_rect, self.password, "PASSWORD", self.active_field == "password", is_password=True)
        
        self.draw_3d_btn(self.login_btn_rect, "LOG IN", (0, 130, 250), self.login_btn_rect.collidepoint(mpos))
        self.draw_3d_btn(self.signup_btn_rect, "CREATE ACCOUNT", (36, 175, 80), self.signup_btn_rect.collidepoint(mpos))
        
        if self.message:
            msg_surf = self.msg_font.render(self.message, True, self.msg_color)
            self.screen.blit(msg_surf, (self.card_rect.centerx - msg_surf.get_width() // 2, self.card_rect.y + 380))

        # Admin Section Divider
        pygame.draw.line(self.screen, (50, 60, 80), (self.card_rect.x + 35, self.card_rect.y + 430), (self.card_rect.x + self.card_rect.w - 35, self.card_rect.y + 430), 1)
        or_lbl = self.sub_font.render("- SYSTEM ADMINISTRATION -", True, (140, 155, 180))
        self.screen.blit(or_lbl, (self.card_rect.centerx - or_lbl.get_width() // 2, self.card_rect.y + 450))

        # Big Bottom Admin Button
        self.draw_3d_btn(self.admin_btn_rect, "🔒 ACCESS ADMIN DATABASE", (200, 40, 55), self.admin_btn_rect.collidepoint(mpos))
