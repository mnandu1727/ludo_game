import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN, YELLOW, BLUE
from network.room_code import encode_online_room, decode_online_room
from network.network_manager import get_local_ip
from network.share_utils import copy_to_clipboard, get_from_clipboard, share_to_whatsapp

COLOR_RGB = {"RED": RED, "GREEN": GREEN, "YELLOW": YELLOW, "BLUE": BLUE}

class RoomLobbyScreen:
    def __init__(self, screen, current_username="Player"):
        self.screen = screen
        self.username = current_username
        self.title_font = pygame.font.SysFont("Helvetica", 30, bold=True)
        self.room_font = pygame.font.SysFont("Helvetica", 20, bold=True)
        self.card_font = pygame.font.SysFont("Helvetica", 15, bold=True)
        self.sub_font = pygame.font.SysFont("Helvetica", 13)
        self.btn_font = pygame.font.SysFont("Helvetica", 15, bold=True)
        self.input_font = pygame.font.SysFont("Helvetica", 18, bold=True)

        self.sub_state = "MENU" # "MENU", "JOIN_INPUT", "INSIDE_ROOM"
        self.is_host = False
        self.room_code = ""
        self.join_input_code = ""
        self.input_active = False
        self.status_msg = ""
        self.btn_pressed = None
        self.toast_msg = ""
        self.toast_timer = 0
        self.slots = []

        # Menu Buttons
        self.create_online_btn = pygame.Rect(SCREEN_WIDTH // 2 - 200, 240, 400, 52)
        self.create_local_btn = pygame.Rect(SCREEN_WIDTH // 2 - 200, 305, 400, 52)
        self.join_room_btn = pygame.Rect(SCREEN_WIDTH // 2 - 200, 370, 400, 52)
        self.back_menu_btn = pygame.Rect(SCREEN_WIDTH // 2 - 200, 440, 400, 44)

        # Join Input Rects
        self.input_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, 270, 260, 50)
        self.paste_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 + 90, 270, 90, 50)
        self.confirm_join_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, 340, 360, 50)
        self.cancel_join_btn = pygame.Rect(SCREEN_WIDTH // 2 - 180, 410, 360, 44)

        # Inside Room Header Sharing Rects
        self.copy_btn_rect = pygame.Rect(495, 42, 120, 34)
        self.share_wa_btn_rect = pygame.Rect(495, 82, 120, 34)
        self.start_game_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, 570, 320, 52)
        self.leave_room_btn = pygame.Rect(SCREEN_WIDTH // 2 - 160, 635, 320, 42)

    def show_toast(self, msg: str, duration_ms=2500):
        self.toast_msg = msg
        self.toast_timer = pygame.time.get_ticks() + duration_ms

    def draw_3d_btn(self, rect: pygame.Rect, title: str, color: tuple, is_pressed: bool, enabled: bool = True):
        x, y, w, h = rect
        draw_col = color if enabled else (60, 66, 80)
        press = (3 if is_pressed else 0) if enabled else 0
        shadow = tuple(max(0, int(c * 0.55)) for c in draw_col)
        pygame.draw.rect(self.screen, shadow, (x, y + 5 - press, w, h), border_radius=10)
        pygame.draw.rect(self.screen, draw_col, (x, y + press, w, h), border_radius=10)
        if enabled:
            pygame.draw.rect(self.screen, (255, 255, 255, 50), (x, y + press, w, h), 1, border_radius=10)
        lbl = self.btn_font.render(title, True, WHITE if enabled else (140, 140, 140))
        self.screen.blit(lbl, lbl.get_rect(center=(x + w // 2, y + press + h // 2)))

    def draw_avatar_pod(self, rect: pygame.Rect, slot_data: dict | None, default_color_name: str):
        x, y, w, h = rect
        c_rgb = COLOR_RGB[default_color_name]
        pygame.draw.rect(self.screen, (10, 12, 18), (x, y + 4, w, h), border_radius=12)
        pygame.draw.rect(self.screen, (26, 32, 48), rect, border_radius=12)
        pygame.draw.rect(self.screen, c_rgb, rect, 2, border_radius=12)
        center = (x + w // 2, y + 55)
        pygame.draw.circle(self.screen, (18, 22, 34), center, 34)
        pygame.draw.circle(self.screen, c_rgb, center, 30)

        if slot_data:
            init_surf = self.title_font.render(slot_data["name"][:1].upper(), True, WHITE)
            self.screen.blit(init_surf, init_surf.get_rect(center=center))
            name_surf = self.card_font.render(slot_data["name"][:10], True, WHITE)
            self.screen.blit(name_surf, name_surf.get_rect(center=(x + w // 2, y + 105)))
            badge = self.sub_font.render("👑 HOST" if slot_data.get("is_host") else "READY", True, (255, 215, 0) if slot_data.get("is_host") else (70, 220, 120))
            self.screen.blit(badge, badge.get_rect(center=(x + w // 2, y + 128)))
        else:
            dot_surf = self.sub_font.render("...", True, (130, 140, 160))
            self.screen.blit(dot_surf, dot_surf.get_rect(center=center))
            wait_surf = self.sub_font.render("WAITING...", True, (120, 130, 150))
            self.screen.blit(wait_surf, wait_surf.get_rect(center=(x + w // 2, y + 110)))
        pygame.draw.rect(self.screen, c_rgb, (x + 15, y + h - 12, w - 30, 4), border_radius=2)

    def draw_toast_notification(self):
        if pygame.time.get_ticks() < self.toast_timer and self.toast_msg:
            t_rect = pygame.Rect((SCREEN_WIDTH - 360) // 2, 135, 360, 42)
            pygame.draw.rect(self.screen, (15, 18, 25), (t_rect.x, t_rect.y + 3, t_rect.w, t_rect.h), border_radius=20)
            pygame.draw.rect(self.screen, (40, 167, 69), t_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255, 70), t_rect, 1, border_radius=20)
            t_surf = self.btn_font.render(self.toast_msg, True, WHITE)
            self.screen.blit(t_surf, t_surf.get_rect(center=t_rect.center))

    def handle_event(self, event) -> tuple[str, any] | None:
        mpos = pygame.mouse.get_pos()
        if self.sub_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.create_online_btn.collidepoint(mpos): self.btn_pressed = "ONLINE_ROOM"
                elif self.create_local_btn.collidepoint(mpos): self.btn_pressed = "LOCAL_ROOM"
                elif self.join_room_btn.collidepoint(mpos): self.btn_pressed = "JOIN_VIEW"
                elif self.back_menu_btn.collidepoint(mpos): self.btn_pressed = "BACK_MAIN"
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.btn_pressed == "ONLINE_ROOM" and self.create_online_btn.collidepoint(event.pos):
                    self.btn_pressed = None
                    self.is_host = True
                    self.sub_state = "INSIDE_ROOM"
                    self.show_toast("✓ Online Room Created! Tunnel active.")
                    return ("START_HOST_ONLINE", True)
                elif self.btn_pressed == "LOCAL_ROOM" and self.create_local_btn.collidepoint(event.pos):
                    self.btn_pressed = None
                    self.is_host = True
                    self.sub_state = "INSIDE_ROOM"
                    self.show_toast("✓ Local Wi-Fi Room Created!")
                    return ("START_HOST_LOCAL", False)
                elif self.btn_pressed == "JOIN_VIEW" and self.join_room_btn.collidepoint(event.pos):
                    self.sub_state = "JOIN_INPUT"
                elif self.btn_pressed == "BACK_MAIN" and self.back_menu_btn.collidepoint(event.pos):
                    return ("BACK_TO_HOME", None)
                self.btn_pressed = None

        elif self.sub_state == "JOIN_INPUT":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.input_active = self.input_box_rect.collidepoint(mpos)
                if self.paste_btn_rect.collidepoint(mpos): self.btn_pressed = "PASTE"
                elif self.confirm_join_btn.collidepoint(mpos): self.btn_pressed = "DO_JOIN"
                elif self.cancel_join_btn.collidepoint(mpos): self.btn_pressed = "CANCEL_JOIN"
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.btn_pressed == "PASTE" and self.paste_btn_rect.collidepoint(event.pos):
                    clip = get_from_clipboard()
                    if clip:
                        self.join_input_code = clip.strip()
                        self.show_toast("✓ Code Pasted from Clipboard!")
                elif self.btn_pressed == "DO_JOIN" and self.confirm_join_btn.collidepoint(event.pos):
                    self.btn_pressed = None
                    self.room_code = self.join_input_code.strip()
                    target_host, target_port = decode_online_room(self.join_input_code)
                    self.is_host = False
                    return ("START_JOIN", (target_host, target_port))
                elif self.btn_pressed == "CANCEL_JOIN" and self.cancel_join_btn.collidepoint(event.pos):
                    self.sub_state = "MENU"
                    self.status_msg = ""
                self.btn_pressed = None
            elif event.type == pygame.KEYDOWN and self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.join_input_code = self.join_input_code[:-1]
                elif event.unicode.isprintable() and len(self.join_input_code) < 35:
                    self.join_input_code += event.unicode

        elif self.sub_state == "INSIDE_ROOM":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.copy_btn_rect.collidepoint(mpos): self.btn_pressed = "COPY"
                elif self.share_wa_btn_rect.collidepoint(mpos): self.btn_pressed = "WHATSAPP"
                elif self.start_game_btn.collidepoint(mpos) and self.is_host and len(self.slots) >= 2: self.btn_pressed = "LAUNCH"
                elif self.leave_room_btn.collidepoint(mpos): self.btn_pressed = "LEAVE"
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.btn_pressed == "COPY" and self.copy_btn_rect.collidepoint(event.pos):
                    copy_to_clipboard(self.room_code)
                    self.show_toast("✓ Room Code Copied to Clipboard!")
                elif self.btn_pressed == "WHATSAPP" and self.share_wa_btn_rect.collidepoint(event.pos):
                    share_to_whatsapp(self.room_code, self.username)
                    self.show_toast("✓ Opening WhatsApp Share...")
                elif self.btn_pressed == "LAUNCH" and self.start_game_btn.collidepoint(event.pos):
                    self.btn_pressed = None
                    return ("TRIGGER_START", None)
                elif self.btn_pressed == "LEAVE" and self.leave_room_btn.collidepoint(event.pos):
                    self.sub_state = "MENU"
                    self.slots = []
                    self.is_host = False
                    return ("LEAVE_ROOM", None)
                self.btn_pressed = None
        return None

    def render(self):
        self.screen.fill((16, 20, 30))
        if self.sub_state == "MENU":
            title = self.title_font.render("MULTIPLAYER LOBBY", True, WHITE)
            sub = self.sub_font.render("PLAY ONLINE (DIFFERENT NETWORKS) OR LOCAL WI-FI", True, (140, 150, 175))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 115))
            self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 165))

            self.draw_3d_btn(self.create_online_btn, "🌍 CREATE ONLINE ROOM (ANY NETWORK)", (0, 150, 255), self.btn_pressed == "ONLINE_ROOM")
            self.draw_3d_btn(self.create_local_btn, "📶 CREATE LOCAL WI-FI ROOM (SAME NETWORK)", (36, 175, 80), self.btn_pressed == "LOCAL_ROOM")
            self.draw_3d_btn(self.join_room_btn, "🔑 JOIN VIA ROOM CODE", (255, 152, 0), self.btn_pressed == "JOIN_VIEW")
            self.draw_3d_btn(self.back_menu_btn, "MAIN MENU", (80, 85, 100), self.btn_pressed == "BACK_MAIN")

        elif self.sub_state == "JOIN_INPUT":
            title = self.title_font.render("ENTER ROOM CODE", True, WHITE)
            sub = self.sub_font.render("Paste your friend's online or local room code", True, (140, 150, 175))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 140))
            self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 190))

            pygame.draw.rect(self.screen, (22, 26, 38), self.input_box_rect, border_radius=8)
            border_col = (0, 168, 255) if self.input_active else (60, 70, 90)
            pygame.draw.rect(self.screen, border_col, self.input_box_rect, 2 if self.input_active else 1, border_radius=8)
            disp_code = self.join_input_code if self.join_input_code else "E.G. X1Y2Z3"
            code_surf = self.input_font.render(disp_code[:22], True, WHITE if self.join_input_code else (100, 110, 130))
            self.screen.blit(code_surf, code_surf.get_rect(center=self.input_box_rect.center))

            self.draw_3d_btn(self.paste_btn_rect, "📋 PASTE", (0, 150, 214), self.btn_pressed == "PASTE")
            self.draw_3d_btn(self.confirm_join_btn, "CONNECT TO ROOM", (40, 167, 69), self.btn_pressed == "DO_JOIN", enabled=len(self.join_input_code) >= 3)
            self.draw_3d_btn(self.cancel_join_btn, "CANCEL", (100, 105, 120), self.btn_pressed == "CANCEL_JOIN")
            if self.status_msg:
                msg = self.sub_font.render(self.status_msg, True, (255, 90, 95))
                self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 475))

        elif self.sub_state == "INSIDE_ROOM":
            header_rect = pygame.Rect(140, 25, 520, 100)
            pygame.draw.rect(self.screen, (24, 30, 45), header_rect, border_radius=12)
            pygame.draw.rect(self.screen, (55, 65, 90), header_rect, 1, border_radius=12)
            self.screen.blit(self.sub_font.render("SHARE CODE WITH PLAYERS ANYWHERE", True, (150, 165, 190)), (165, 38))
            self.screen.blit(self.room_font.render(f"🔑 {self.room_code[:18]}", True, (255, 215, 0)), (165, 68))
            self.draw_3d_btn(self.copy_btn_rect, "📋 COPY", (0, 123, 255), self.btn_pressed == "COPY")
            self.draw_3d_btn(self.share_wa_btn_rect, "💬 SHARE", (37, 211, 102), self.btn_pressed == "WHATSAPP")

            pod_rects = [pygame.Rect(90, 180, 145, 160), pygame.Rect(250, 180, 145, 160), pygame.Rect(410, 180, 145, 160), pygame.Rect(570, 180, 145, 160)]
            for i, c_name in enumerate(["RED", "GREEN", "YELLOW", "BLUE"]):
                self.draw_avatar_pod(pod_rects[i], self.slots[i] if i < len(self.slots) else None, c_name)

            can_launch = self.is_host and len(self.slots) >= 2
            btn_title = f"START MATCH ({len(self.slots)} PLAYERS)" if can_launch else ("WAITING FOR HOST..." if not self.is_host else "WAITING FOR PLAYERS (MIN 2)...")
            self.draw_3d_btn(self.start_game_btn, btn_title, (255, 152, 0), self.btn_pressed == "LAUNCH", enabled=can_launch)
            self.draw_3d_btn(self.leave_room_btn, "LEAVE ROOM", (220, 53, 69), self.btn_pressed == "LEAVE")

        self.draw_toast_notification()