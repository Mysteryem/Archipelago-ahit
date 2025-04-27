from enum import Enum


class StartRoomDifficulty(Enum):
    Normal = -1
    Safe = 0
    Dangerous = 1


class CombatLogicDifficulty(Enum):
    NO_LOGIC = -1
    NORMAL = 0
    MINIMAL = 1