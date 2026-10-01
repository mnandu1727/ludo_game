# gui/admin_screen.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE, GRAY
from database.db import get_all_users, get_all_matches, delete_user_by_id

ADMIN_CREDENTIALS = {"admin": "admin123", "root": "ludo2026"}

class AdminScreen:
    def __init__(self, screen):
        self.screen = screen
        self.state = "LOGIN"  # "LOGIN" or "DASHBOARD"
        
        # Fonts
        self.title_font = pygame.font.SysFont("Helvetica", 32, bold=True)
        self.header_font = pygame.font.SysFont("Helvetica", 18, bold=True)
        self.font = pygame.font.SysFont("Helvetica", 14)
        self.btn_font = pygame.font.SysFont("Helvetica", 15, bold=True)
        self.input_font = pygame.font.SysFont("Helvetica", 18)

        # Login State
        self.admin_user = ""
        self.admin_pass = ""
        self.active_field = "user"
        self.error_msg = ""
        self.btn_pressed = None

        # Dashboard State
        self.current_tab = "USERS"  # "USERS" or "MATCHES"
        self.scroll_offset = 0
        self.users_data = []
        self.matches_data = []

        # Login Rects
        self.card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 180, 400, 430)
        self.u_input_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 110, 330, 44)
        self.p_input_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 190, 330, 44)
        self.login_btn_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 265, 330, 46)
        self.back_btn_rect = pygame.Rect(self.card_rect.x + 35, self.card_rect.y + 325, 330, 42)

        # Dashboard Rects
        self.tab_users_rect = pygame.Rect(60, 110, 180, 42)
        self.tab_matches_rect = pygame.Rect(250, 110, 180, 42)
        self.refresh_btn_rect = pygame.Rect(560, 110, 100, 42)
        self.exit_admin_btn = pygame.Rect(670, 110, 80, 42)

    def refresh_data(self):
        self.users_data = get_all_users()
        self.matches_data = get_all_matches()

    def draw_3d_btn(self, rect: pygame.Rect, text: str, color: tuple, is_pressed: bool):
        x, y, w, h = rect
        press = 3 if is_pressed else 0
        shadow = tuple(max(0, int(c * 0.55)) for c in color)
        pygame.draw.rect(self.screen, shadow, (x, y + 4 - press, w, h), border_radius=8)
        pygame.draw.rect(self.screen, color, (x, y + press, w, h), border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255, 60), (x, y + press, w, h), 1, border_radius=8)
        lbl = self.btn_font.render(text, True, WHITE)
        self.screen.blit(lbl, lbl.get_rect(center=(x + w // 2, y + press + h // 2)))

    def handle_event(self, event) -> str | None:
        mouse_pos = pygame.mouse.get_pos()

        # ---------- ADMIN LOGIN EVENTS ----------
        if self.state == "LOGIN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.u_input_rect.collidepoint(mouse_pos):
                    self.active_field = "user"
                elif self.p_input_rect.collidepoint(mouse_pos):
                    self.active_field = "pass"
                elif self.login_btn_rect.collidepoint(mouse_pos):
                    self.btn_pressed = "ADMIN_AUTH"
                elif self.back_btn_rect.collidepoint(mouse_pos):
                    self.btn_pressed = "BACK_MAIN"

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.btn_pressed == "ADMIN_AUTH" and self.login_btn_rect.collidepoint(event.pos):
                    if ADMIN_CREDENTIALS.get(self.admin_user) == self.admin_pass:
                        self.state = "DASHBOARD"
                        self.refresh_data()
                        self.error_msg = ""
                    else:
                        self.error_msg = "Invalid Master Admin Credentials!"
                elif self.btn_pressed == "BACK_MAIN" and self.back_btn_rect.collidepoint(event.pos):
                    self.btn_pressed = None
                    return "EXIT_TO_LOGIN"
                self.btn_pressed = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.active_field = "pass" if self.active_field == "user" else "user"
                elif event.key == pygame.K_RETURN:
                    if ADMIN_CREDENTIALS.get(self.admin_user) == self.admin_pass:
                        self.state = "DASHBOARD"
                        self.refresh_data()
                    else:
                        self.error_msg = "Invalid Master Admin Credentials!"
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_field == "user": self.admin_user = self.admin_user[:-1]
                    else: self.admin_pass = self.admin_pass[:-1]
                else:
                    if event.unicode.isprintable():
                        if self.active_field == "user" and len(self.admin_user) < 20:
                            self.admin_user += event.unicode
                        elif self.active_field == "pass" and len(self.admin_pass) < 20:
                            self.admin_pass += event.unicode

        # ---------- ADMIN DASHBOARD EVENTS ----------
        elif self.state == "DASHBOARD":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.tab_users_rect.collidepoint(mouse_pos):
                    self.current_tab = "USERS"
                    self.scroll_offset = 0
                elif self.tab_matches_rect.collidepoint(mouse_pos):
                    self.current_tab = "MATCHES"
                    self.scroll_offset = 0
                elif self.refresh_btn_rect.collidepoint(mouse_pos):
                    self.refresh_data()
                elif self.exit_admin_btn.collidepoint(mouse_pos):
                    self.state = "LOGIN"
                    self.admin_user = ""
                    self.admin_pass = ""
                    return "EXIT_TO_LOGIN"

                # Check Delete User clicks
                if self.current_tab == "USERS":
                    start_y = 230 - self.scroll_offset
                    for u in self.users_data:
                        del_btn_rect = pygame.Rect(680, start_y + 4, 60, 24)
                        if del_btn_rect.collidepoint(mouse_pos):
                            delete_user_by_id(u["id"])
                            self.refresh_data()
                            break
                        start_y += 38

            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_offset = max(0, self.scroll_offset - event.y * 20)

        return None

    def render(self):
        self.screen.fill((16, 20, 30))

        if self.state == "LOGIN":
            # 3D Login Panel
            x, y, w, h = self.card_rect
            pygame.draw.rect(self.screen, (10, 12, 18), (x, y + 6, w, h), border_radius=14)
            pygame.draw.rect(self.screen, (26, 32, 48), self.card_rect, border_radius=14)
            pygame.draw.rect(self.screen, (220, 53, 69), self.card_rect, 2, border_radius=14)

            title = self.title_font.render("🔒 ADMIN PORTAL", True, WHITE)
            self.screen.blit(title, (self.card_rect.centerx - title.get_width() // 2, y + 30))

            # Username Input
            u_lbl = self.font.render("ADMIN USERNAME", True, (160, 175, 200))
            self.screen.blit(u_lbl, (self.u_input_rect.x, self.u_input_rect.y - 20))
            pygame.draw.rect(self.screen, (18, 22, 34), self.u_input_rect, border_radius=6)
            b_col1 = (0, 168, 255) if self.active_field == "user" else (60, 70, 90)
            pygame.draw.rect(self.screen, b_col1, self.u_input_rect, 2 if self.active_field == "user" else 1, border_radius=6)
            u_txt = self.input_font.render(self.admin_user, True, WHITE)
            self.screen.blit(u_txt, (self.u_input_rect.x + 10, self.u_input_rect.y + 10))

            # Password Input
            p_lbl = self.font.render("MASTER PASSWORD", True, (160, 175, 200))
            self.screen.blit(p_lbl, (self.p_input_rect.x, self.p_input_rect.y - 20))
            pygame.draw.rect(self.screen, (18, 22, 34), self.p_input_rect, border_radius=6)
            b_col2 = (0, 168, 255) if self.active_field == "pass" else (60, 70, 90)
            pygame.draw.rect(self.screen, b_col2, self.p_input_rect, 2 if self.active_field == "pass" else 1, border_radius=6)
            p_txt = self.input_font.render("●" * len(self.admin_pass), True, WHITE)
            self.screen.blit(p_txt, (self.p_input_rect.x + 10, self.p_input_rect.y + 10))

            self.draw_3d_btn(self.login_btn_rect, "ACCESS DATABASE", (220, 53, 69), self.btn_pressed == "ADMIN_AUTH")
            self.draw_3d_btn(self.back_btn_rect, "BACK TO GAME", (80, 85, 100), self.btn_pressed == "BACK_MAIN")

            if self.error_msg:
                err = self.font.render(self.error_msg, True, (255, 90, 95))
                self.screen.blit(err, (self.card_rect.centerx - err.get_width() // 2, y + 380))

        elif self.state == "DASHBOARD":
            # Header
            title = self.title_font.render("🛡️ SYSTEM DATABASE MANAGEMENT", True, WHITE)
            self.screen.blit(title, (60, 35))

            stats_summary = f"Total Registered Users: {len(self.users_data)}  |  Total Match Logs: {len(self.matches_data)}"
            self.screen.blit(self.font.render(stats_summary, True, (160, 180, 210)), (60, 78))

            # Tabs
            u_tab_col = (0, 130, 250) if self.current_tab == "USERS" else (40, 48, 68)
            m_tab_col = (0, 130, 250) if self.current_tab == "MATCHES" else (40, 48, 68)
            self.draw_3d_btn(self.tab_users_rect, f"USERS ({len(self.users_data)})", u_tab_col, False)
            self.draw_3d_btn(self.tab_matches_rect, f"MATCH LOGS ({len(self.matches_data)})", m_tab_col, False)
            self.draw_3d_btn(self.refresh_btn_rect, "REFRESH", (40, 167, 69), False)
            self.draw_3d_btn(self.exit_admin_btn, "EXIT", (220, 53, 69), False)

            # Table Container
            table_rect = pygame.Rect(50, 170, 700, 580)
            pygame.draw.rect(self.screen, (22, 28, 42), table_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 60, 85), table_rect, 1, border_radius=10)

            # Header Row
            pygame.draw.rect(self.screen, (32, 40, 60), (50, 170, 700, 42), border_top_left_radius=10, border_top_right_radius=10)
            
            if self.current_tab == "USERS":
                cols = [("ID", 70), ("USERNAME", 130), ("PLAYED", 280), ("WON", 370), ("WIN RATE", 460), ("CREATED AT", 560), ("ACTION", 680)]
                for name, pos_x in cols:
                    self.screen.blit(self.header_font.render(name, True, (200, 215, 240)), (pos_x, 182))

                # User Rows with Clipping
                clip_rect = pygame.Rect(50, 215, 700, 530)
                self.screen.set_clip(clip_rect)
                
                row_y = 225 - self.scroll_offset
                for i, u in enumerate(self.users_data):
                    bg_row = (26, 32, 48) if i % 2 == 0 else (22, 28, 42)
                    pygame.draw.rect(self.screen, bg_row, (55, row_y - 4, 690, 34), border_radius=4)

                    self.screen.blit(self.font.render(str(u["id"]), True, (150, 160, 180)), (70, row_y + 4))
                    self.screen.blit(self.header_font.render(u["username"], True, WHITE), (130, row_y + 3))
                    self.screen.blit(self.font.render(str(u["games_played"]), True, WHITE), (290, row_y + 4))
                    self.screen.blit(self.font.render(str(u["games_won"]), True, (70, 220, 120)), (380, row_y + 4))
                    self.screen.blit(self.font.render(f"{u['win_rate']}%", True, (255, 193, 7)), (470, row_y + 4))
                    
                    created_short = str(u.get("created_at", "N/A"))[:10]
                    self.screen.blit(self.font.render(created_short, True, (140, 150, 170)), (560, row_y + 4))

                    # Delete Action Button
                    del_rect = pygame.Rect(680, row_y + 2, 55, 24)
                    pygame.draw.rect(self.screen, (220, 53, 69), del_rect, border_radius=4)
                    del_lbl = self.font.render("DEL", True, WHITE)
                    self.screen.blit(del_lbl, del_lbl.get_rect(center=del_rect.center))

                    row_y += 38

                self.screen.set_clip(None)

            elif self.current_tab == "MATCHES":
                cols = [("MATCH ID", 70), ("PLAYER", 170), ("WINNER", 310), ("PLAYER COL", 440), ("AI / OPPONENT", 560), ("TIMESTAMP", 660)]
                for name, pos_x in cols:
                    self.screen.blit(self.header_font.render(name, True, (200, 215, 240)), (pos_x, 182))

                clip_rect = pygame.Rect(50, 215, 700, 530)
                self.screen.set_clip(clip_rect)

                row_y = 225 - self.scroll_offset
                for i, m in enumerate(self.matches_data):
                    bg_row = (26, 32, 48) if i % 2 == 0 else (22, 28, 42)
                    pygame.draw.rect(self.screen, bg_row, (55, row_y - 4, 690, 34), border_radius=4)

                    self.screen.blit(self.font.render(str(m["id"]), True, (150, 160, 180)), (80, row_y + 4))
                    self.screen.blit(self.font.render(m["username"], True, WHITE), (170, row_y + 4))
                    
                    is_win = (m["winner"] in [m["player_color"], "RED", "TEAM A (RED & YELLOW)"])
                    win_col = (70, 220, 120) if is_win else (255, 90, 95)
                    self.screen.blit(self.header_font.render(m["winner"], True, win_col), (310, row_y + 3))

                    self.screen.blit(self.font.render(m["player_color"], True, (180, 190, 210)), (450, row_y + 4))
                    self.screen.blit(self.font.render(m["ai_color"], True, (180, 190, 210)), (570, row_y + 4))
                    
                    time_short = str(m.get("played_at", "N/A"))[:10]
                    self.screen.blit(self.font.render(time_short, True, (140, 150, 170)), (660, row_y + 4))

                    row_y += 38

                self.screen.set_clip(None)