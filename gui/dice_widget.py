import pygame
import random
import math
from config import WHITE, BLACK, RED

class DiceWidget:
    def __init__(self, x=700, y=360, size=70):
        self.rect = pygame.Rect(x, y, size, size)
        self.value = 1
        self.is_rolling = False
        self.roll_frames_left = 0
        self.final_value = 1
        self.font = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.rot_offset = 0

    def trigger_roll(self, final_value: int, duration_frames=18):
        self.is_rolling = True
        self.roll_frames_left = duration_frames
        self.final_value = final_value

    def update(self) -> bool:
        if not self.is_rolling:
            return False
        if self.roll_frames_left > 0:
            self.value = random.randint(1, 6)
            self.rot_offset = random.randint(-4, 4)
            self.roll_frames_left -= 1
            return False
        else:
            self.is_rolling = False
            self.value = self.final_value
            self.rot_offset = 0
            return True

    def is_clicked(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def draw_pips(self, screen, x, y, size, val, color):
        rad = max(3, size // 10)
        cx, cy = x + size // 2, y + size // 2
        offset = size // 4
        pip_map = {
            1: [(cx, cy)],
            2: [(cx - offset, cy - offset), (cx + offset, cy + offset)],
            3: [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)],
            4: [(cx - offset, cy - offset), (cx + offset, cy - offset), (cx - offset, cy + offset), (cx + offset, cy + offset)],
            5: [(cx - offset, cy - offset), (cx + offset, cy - offset), (cx, cy), (cx - offset, cy + offset), (cx + offset, cy + offset)],
            6: [(cx - offset, cy - offset), (cx + offset, cy - offset), (cx - offset, cy), (cx + offset, cy), (cx - offset, cy + offset), (cx + offset, cy + offset)]
        }
        for px, py in pip_map.get(val, []):
            pygame.draw.circle(screen, color, (px, py), rad)
            # Pip reflection specular
            pygame.draw.circle(screen, (255, 255, 255, 120), (px - 1, py - 1), max(1, rad // 2))

    def render(self, screen, is_player_turn: bool, can_roll: bool):
        x, y, w, h = self.rect
        mpos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mpos) and can_roll and is_player_turn

        elevation = 6 if (is_hovered and not self.is_rolling) else 3
        draw_y = y - elevation + self.rot_offset

        # 3D Drop shadow
        pygame.draw.rect(screen, (20, 24, 35, 100), (x - 2, y + 4, w + 4, h + 2), border_radius=12)
        # Extruded lower side
        pygame.draw.rect(screen, (190, 195, 208), (x, draw_y + 4, w, h), border_radius=12)
        # Elevated top surface
        pygame.draw.rect(screen, (255, 255, 255), (x, draw_y, w, h), border_radius=12)

        # Border outline
        border_col = (0, 140, 255) if (is_player_turn and can_roll) else (80, 90, 110)
        pygame.draw.rect(screen, border_col, (x, draw_y, w, h), 2, border_radius=12)
        pygame.draw.line(screen, (255, 255, 255, 180), (x + 3, draw_y + 2), (x + w - 3, draw_y + 2), 2)

        self.draw_pips(screen, x, draw_y, w, self.value, RED if self.value in (1, 6) else BLACK)

        # Status HUD label
        if self.is_rolling:
            label = self.font.render("Rolling...", True, (130, 140, 160))
        elif is_player_turn and can_roll:
            label = self.font.render("CLICK!", True, (0, 140, 255))
        else:
            label = self.font.render(f"Rolled: {self.value}", True, (50, 60, 80))
        screen.blit(label, label.get_rect(center=(x + w // 2, y + h + 16)))