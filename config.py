import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
DB_PATH = os.path.join(BASE_DIR, "database","ludo.db")  
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BOARD_SIZE = 600
FPS = 60

# Palette
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
LIGHT_BG = (245, 245, 245)
RED = (220, 53, 69)
GREEN = (40, 167, 69)
YELLOW = (255, 193, 7)
BLUE = (0, 123, 255)