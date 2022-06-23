from enum import Enum, auto

class GameState(Enum):
    MENU = auto()
    INSTRUCTIONS = auto()
    CHOOSE_FILE = auto()
    GAME = auto()
    GAME_OVER = auto()

class ActionState(Enum):
    RULE_1 = auto()
    RULE_3_BLUE = auto()
    RULE_3_WHITE = auto()
    RULE_3_FORCE = auto()