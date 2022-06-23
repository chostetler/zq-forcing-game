from pathlib import Path
import pygame

BASE_PATH: Path = Path(__file__).parent.parent

ASSETS_PATH: Path = BASE_PATH / 'assets'
GRAPHS_PATH: Path = BASE_PATH / 'graphs'
SRC_PATH: Path = BASE_PATH / 'src'

IMAGES_PATH: Path = ASSETS_PATH / 'images'
SOUNDS_PATH: Path = ASSETS_PATH / 'sounds'

FILLED_COLOR: pygame.Color = pygame.Color('cyan')
EMPTY_COLOR: pygame.Color = pygame.Color('white')

GRAPH_CENTER_X = 200
GRAPH_CENTER_Y = 200

DEFAULT_VERTEX_RADIUS = 20