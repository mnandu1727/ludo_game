import pygame
from config import SCREEN_WIDTH, WHITE
from database.db import get_all_users, get_all_matches, delete_user_by_id

ADMIN_CREDENTIALS = {"admin": "admin123", "root": "ludo2026"}


class AdminScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("Helvetica", 30, bold=True)
        self.font = pygame.font.SysFont("Helvetica", 16)
        self.input_font = pygame.font.SysFont("Helvetica", 20)
        self.state = "LOGIN"
        self.admin_user = ""
        self.admin_pass = ""
        self.active_field = "user"
        self.message = ""
        self.users_data = []
        self.matches_data = []
        self.login_rect = pygame.Rect(SCREEN_WIDTH // 2 - 165, 430, 330, 46)
        self.back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 165, 490, 330, 42)
        self.user_rect = pygame.Rect(SCREEN_WIDTH // 2 - 165, 250, 330, 44)
        self.pass_rect = pygame.Rect(SCREEN_WIDTH // 2 - 165, 330, 330, 44)

    def reset(self):
        self.state = "LOGIN"
        self.admin_user = ""
        self.admin_pass = ""
        self.active_field = "user"
        self.message = ""

    def refresh_data(self):
        self.users_data = get_all_users()
        self.matches_data = get_all_matches()

    def handle_event(self, event) -> str | None:
        if self.state == "LOGIN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.user_rect.collidepoint(event.pos):
                    self.active_field = "user"
                elif self.pass_rect.collidepoint(event.pos):
                    self.active_field = "pass"
                elif self.login_rect.collidepoint(event.pos):
                    if ADMIN_CREDENTIALS.get(self.admin_user) == self.admin_pass:
                        self.state = "DASHBOARD"
                        self.refresh_data()
                    else:
                        self.message = "Invalid admin credentials"
                elif self.back_rect.collidepoint(event.pos):
                    return "EXIT_TO_LOGIN"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.active_field = "pass" if self.active_field == "user" else "user"
                elif event.key == pygame.K_RETURN:
                    if ADMIN_CREDENTIALS.get(self.admin_user) == self.admin_pass:
                        self.state = "DASHBOARD"
                        self.refresh_data()
                    else:
                        self.message = "Invalid admin credentials"
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_field == "user":
                        self.admin_user = self.admin_user[:-1]
                    else:
                        self.admin_pass = self.admin_pass[:-1]
                elif event.unicode.isprintable():
                    if self.active_field == "user" and len(self.admin_user) < 20:
                        self.admin_user += event.unicode
                    elif self.active_field == "pass" and len(self.admin_pass) < 20:
                        self.admin_pass += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect(680, 110, 80, 42).collidepoint(event.pos):
                return "EXIT_TO_LOGIN"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "EXIT_TO_LOGIN"
        return None

    def button(self, rect, label, color):
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        text = self.font.render(label, True, WHITE)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def render(self):
        self.screen.fill((16, 20, 30))
        if self.state == "LOGIN":
            title = self.title_font.render("ADMIN PORTAL", True, WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 180)))
            for rect, value, label in ((self.user_rect, self.admin_user, "USERNAME"), (self.pass_rect, "*" * len(self.admin_pass), "PASSWORD")):
                self.screen.blit(self.font.render(label, True, (180, 190, 205)), (rect.x, rect.y - 24))
                pygame.draw.rect(self.screen, (30, 36, 50), rect, border_radius=6)
                self.screen.blit(self.input_font.render(value, True, WHITE), (rect.x + 10, rect.y + 9))
            self.button(self.login_rect, "ACCESS DATABASE", (200, 45, 60))
            self.button(self.back_rect, "BACK TO LOGIN", (75, 85, 105))
            if self.message:
                self.screen.blit(self.font.render(self.message, True, (255, 90, 95)), (SCREEN_WIDTH // 2 - 110, 550))
        else:
            self.screen.blit(self.title_font.render("ADMIN DASHBOARD", True, WHITE), (50, 40))
            self.screen.blit(self.font.render(f"Users: {len(self.users_data)}  Matches: {len(self.matches_data)}", True, (180, 190, 205)), (50, 90))
            self.button(pygame.Rect(680, 110, 80, 42), "EXIT", (200, 45, 60))
            y = 180
            for user in self.users_data[:12]:
                text = f"{user['id']}  {user['username']}  played: {user['games_played']}  won: {user['games_won']}"
                self.screen.blit(self.font.render(text, True, WHITE), (60, y))
                y += 32
