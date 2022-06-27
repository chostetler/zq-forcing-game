from pathlib import Path
import pygame

# File Paths

BASE_PATH: Path = Path(__file__).parent.parent
ASSETS_PATH: Path = BASE_PATH / 'assets'
GRAPHS_PATH: Path = BASE_PATH / 'graphs'
USER_GRAPHS_PATH: Path = GRAPHS_PATH / 'usergraphs'
SRC_PATH: Path = BASE_PATH / 'src'
IMAGES_PATH: Path = ASSETS_PATH / 'images'
SOUNDS_PATH: Path = ASSETS_PATH / 'sounds'

# Colors
FILLED_COLOR: pygame.Color = pygame.Color('#5751FF')
EMPTY_COLOR: pygame.Color = pygame.Color('white')
RULE_1_HOVER_COLOR: pygame.Color = pygame.Color('cyan')
RULE_3_HOVER_COLOR: pygame.Color = pygame.Color('#FF8F00')
RULE_3_SELECTED_COLOR: pygame.Color = pygame.Color('#FFD65C')

# Coordinates/Dimensions
WIN_WIDTH = 800
WIN_HEIGHT = 600
GRAPH_CENTER_X = 200
GRAPH_CENTER_Y = 200
DEFAULT_VERTEX_RADIUS = 20

# Timing
TIME_BETWEEN_AUTOFORCE = 250

# Forcing
AUTOFORCE_ENABLED = False

# Visual settings
RENDER_VERTEX_LABELS = True
RENDER_VERTEX_TOKENS = True
SHOW_RULE_3_INSTRUCTIONS = True

# Various
Q = 1