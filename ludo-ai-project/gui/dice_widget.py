import pygame
import random
from config import WHITE, BLACK, RED

class DiceWidget:
    def __init__(self, x=705, y=365, size=65):
        self.rect = pygame.Rect(x, y, size, size)
        self.value = 1
        self.is_rolling = False
        self.roll_frames_left = 0
        self.final_value = 1
        self.font = pygame.font.SysFont("Helvetica", 14, bold=True)

    def trigger_roll(self, final_value: int, duration_frames=18):
        self.is_rolling = True
        self.roll_frames_left = duration_frames
        self.final_value = final_value

    def update(self) -> bool:
        if not self.is_rolling:
            return False
        if self.roll_frames_left > 0:
            self.value = random.randint(1, 6)
            self.roll_frames_left -= 1
            return False
        else:
            self.is_rolling = False
            self.value = self.final_value
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

    def render(self, screen, is_player_turn: bool, can_roll: bool):
        x, y, w, h = self.rect
        pygame.draw.rect(screen, (180, 180, 180), (x + 3, y + 3, w, h), border_radius=10)
        border_color = (0, 120, 255) if (is_player_turn and can_roll and not self.is_rolling) else (60, 60, 60)
        border_width = 3 if (is_player_turn and can_roll and not self.is_rolling) else 2
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=10)
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=10)
        self.draw_pips(screen, x, y, w, self.value, RED if self.value in (1, 6) else BLACK)
        if self.is_rolling:
            label = self.font.render("Rolling...", True, (100, 100, 100))
        elif is_player_turn and can_roll:
            label = self.font.render("CLICK!", True, (0, 120, 255))
        else:
            label = self.font.render(f"Rolled: {self.value}", True, (50, 50, 50))
        screen.blit(label, label.get_rect(center=(x + w // 2, y + h + 14)))
