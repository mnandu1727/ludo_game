import pygame
import math
from auth.auth import login, signup
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("Helvetica", 40, bold=True)
        self.sub_font = pygame.font.SysFont("Helvetica", 13)
        self.label_font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.input_font = pygame.font.SysFont("Helvetica", 18)
        self.btn_font = pygame.font.SysFont("Helvetica", 16, bold=True)
        self.admin_btn_font = pygame.font.SysFont("Helvetica", 13, bold=True)
        self.msg_font = pygame.font.SysFont("Helvetica", 13, bold=True)
        
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.msg_color = (255, 90, 95)
        self.user_data = None

        # Dimensions & Rects
        self.card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 210, 110, 420, 560)
        self.u_field_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 125, 350, 44)
        self.p_field_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 205, 350, 44)
        self.login_btn_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 280, 350, 46)
        self.signup_btn_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 345, 350, 46)
        
        # Dedicated Admin Portal Access Button
        self.admin_btn_rect = pygame.Rect(self.card_rect.x + 75, self.card_rect.y + 490, 270, 38)
        self.btn_pressed = None

    def draw_radial_gradient_background(self):
        for r in range(SCREEN_WIDTH, 0, -40):
            alpha_ratio = r / SCREEN_WIDTH
            c = int(18 + (1.0 - alpha_ratio) * 14)
            c2 = int(24 + (1.0 - alpha_ratio) * 22)
            c3 = int(38 + (1.0 - alpha_ratio) * 35)
            pygame.draw.circle(self.screen, (c, c2, c3), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), r)

    def draw_floating_3d_cubes(self):
        ticks = pygame.time.get_ticks()
        cubes = [
            (90, 200, 50, 0.0015, (220, 53, 69)),
            (700, 240, 58, 0.0018, (255, 193, 7)),
            (110, 620, 62, 0.0012, (0, 123, 255)),
            (680, 650, 52, 0.0020, (40, 167, 69)),
        ]
        for bx, by, sz, spd, col in cubes:
            offset_y = math.sin(ticks * spd + bx) * 12
            cx, cy = bx, by + offset_y
            top = [(cx, cy - sz * 0.5), (cx + sz * 0.86, cy), (cx, cy + sz * 0.5), (cx - sz * 0.86, cy)]
            left = [(cx - sz * 0.86, cy), (cx, cy + sz * 0.5), (cx, cy + sz * 1.5), (cx - sz * 0.86, cy + sz)]
            right = [(cx + sz * 0.86, cy), (cx, cy + sz * 0.5), (cx, cy + sz * 1.5), (cx + sz * 0.86, cy + sz)]
            pygame.draw.polygon(self.screen, tuple(int(v * 0.65) for v in col), left)
            pygame.draw.polygon(self.screen, tuple(int(v * 0.85) for v in col), right)
            pygame.draw.polygon(self.screen, tuple(min(255, int(v * 1.15)) for v in col), top)
            pygame.draw.polygon(self.screen, (255, 255, 255, 30), top, 1)

    def draw_3d_panel(self, rect: pygame.Rect, bg_color, border_color, bevel_height=8):
        x, y, w, h = rect
        for s in range(bevel_height, 0, -2):
            pygame.draw.rect(self.screen, (10, 12, 18), (x - s, y - s + 6, w + s * 2, h + s * 2), border_radius=18)
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=16)
        bevel_surf = pygame.Surface((w - 4, 3), pygame.SRCALPHA)
        bevel_surf.fill((255, 255, 255, 45))
        self.screen.blit(bevel_surf, (x + 2, y + 2))
        pygame.draw.rect(self.screen, border_color, rect, width=1, border_radius=16)

    def draw_3d_button(self, rect: pygame.Rect, text: str, primary_color, is_hovered: bool, is_pressed: bool, is_admin=False):
        x, y, w, h = rect
        press_offset = 3 if is_pressed else 0
        depth = 5 - press_offset
        shadow_col = tuple(max(0, int(c * 0.55)) for c in primary_color)
        pygame.draw.rect(self.screen, shadow_col, (x, y + depth, w, h), border_radius=10)
        btn_col = tuple(min(255, int(c * (1.15 if is_hovered else 1.0))) for c in primary_color)
        top_rect = pygame.Rect(x, y + press_offset, w, h)
        pygame.draw.rect(self.screen, btn_col, top_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255, 50), top_rect, width=1, border_radius=10)
        
        f = self.admin_btn_font if is_admin else self.btn_font
        label = f.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=top_rect.center))

    def draw_input_field(self, rect: pygame.Rect, text: str, label_title: str, is_active: bool, is_password=False):
        x, y, w, h = rect
        lbl = self.label_font.render(label_title, True, (180, 190, 205))
        self.screen.blit(lbl, (x, y - 20))
        pygame.draw.rect(self.screen, (22, 26, 36), rect, border_radius=8)
        pygame.draw.line(self.screen, (10, 12, 18), (x + 4, y + 1), (x + w - 4, y + 1), 2)
        border_col = (0, 168, 255) if is_active else (50, 58, 76)
        pygame.draw.rect(self.screen, border_col, rect, width=2 if is_active else 1, border_radius=8)
        display_str = ("●" * len(text)) if is_password else text
        txt_surf = self.input_font.render(display_str, True, (240, 245, 255))
        self.screen.blit(txt_surf, (x + 14, y + 12))
        if is_active and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = x + 14 + txt_surf.get_width() + 2
            pygame.draw.line(self.screen, (0, 180, 255), (cursor_x, y + 10), (cursor_x, y + h - 10), 2)

    def handle_event(self, event) -> str | None:
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.u_field_rect.collidepoint(event.pos):
                self.active_field = "username"
            elif self.p_field_rect.collidepoint(event.pos):
                self.active_field = "password"
            elif self.login_btn_rect.collidepoint(event.pos):
                self.btn_pressed = "login"
            elif self.signup_btn_rect.collidepoint(event.pos):
                self.btn_pressed = "signup"
            elif self.admin_btn_rect.collidepoint(event.pos):
                self.btn_pressed = "admin"

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.btn_pressed == "login" and self.login_btn_rect.collidepoint(event.pos):
                success, res = login(self.username, self.password)
                if success:
                    self.user_data = res
                    return "HOME"
                self.message = str(res)
                self.msg_color = (255, 80, 80)
            elif self.btn_pressed == "signup" and self.signup_btn_rect.collidepoint(event.pos):
                success, res = signup(self.username, self.password)
                self.message = res
                self.msg_color = (70, 220, 120) if success else (255, 80, 80)
            elif self.btn_pressed == "admin" and self.admin_btn_rect.collidepoint(event.pos):
                self.btn_pressed = None
                return "GOTO_ADMIN"
            self.btn_pressed = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
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
        self.draw_radial_gradient_background()
        self.draw_floating_3d_cubes()
        self.draw_3d_panel(self.card_rect, bg_color=(30, 36, 50), border_color=(60, 72, 98), bevel_height=10)
        
        # Titles
        title_surf = self.title_font.render("LUDO MASTER", True, (255, 255, 255))
        sub_surf = self.sub_font.render("LOGIN OR SIGN UP TO PLAY", True, (130, 145, 170))
        self.screen.blit(title_surf, (self.card_rect.centerx - title_surf.get_width() // 2, self.card_rect.y + 30))
        self.screen.blit(sub_surf, (self.card_rect.centerx - sub_surf.get_width() // 2, self.card_rect.y + 75))
        
        # Text Inputs
        self.draw_input_field(self.u_field_rect, self.username, "USERNAME", self.active_field == "username")
        self.draw_input_field(self.p_field_rect, self.password, "PASSWORD", self.active_field == "password", is_password=True)
        
        # User Action Buttons
        mpos = pygame.mouse.get_pos()
        self.draw_3d_button(self.login_btn_rect, "LOG IN", (0, 130, 250), self.login_btn_rect.collidepoint(mpos), self.btn_pressed == "login")
        self.draw_3d_button(self.signup_btn_rect, "CREATE ACCOUNT", (36, 175, 80), self.signup_btn_rect.collidepoint(mpos), self.btn_pressed == "signup")
        
        # Status Message
        if self.message:
            msg_surf = self.msg_font.render(self.message, True, self.msg_color)
            self.screen.blit(msg_surf, (self.card_rect.centerx - msg_surf.get_width() // 2, self.card_rect.y + 408))

        # Divider for Admin Section
        pygame.draw.line(self.screen, (50, 60, 80), (self.card_rect.x + 35, self.card_rect.y + 440), (self.card_rect.x + self.card_rect.w - 35, self.card_rect.y + 440), 1)
        or_lbl = self.sub_font.render("- SYSTEM ADMINISTRATION -", True, (120, 135, 160))
        self.screen.blit(or_lbl, (self.card_rect.centerx - or_lbl.get_width() // 2, self.card_rect.y + 455))

        # Red Admin Portal Button
        self.draw_3d_button(self.admin_btn_rect, "🔒 ACCESS ADMIN DATABASE", (180, 40, 55), self.admin_btn_rect.collidepoint(mpos), self.btn_pressed == "admin", is_admin=True)
