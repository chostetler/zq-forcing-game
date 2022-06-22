from pathlib import Path

BASE_PATH: Path = Path(__file__).parent.parent

ASSETS_PATH: Path = BASE_PATH / 'assets'
GRAPHS_PATH: Path = BASE_PATH / 'graphs'
SRC_PATH: Path = BASE_PATH / 'src'

IMAGES_PATH: Path = ASSETS_PATH / 'images'
SOUNDS_PATH: Path = ASSETS_PATH / 'sounds'