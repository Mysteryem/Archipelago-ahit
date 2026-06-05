from enum import StrEnum

class NonDataItemName(StrEnum):
    """
    Names of items that are not determined by explicitly defined data.
    """
    # AP Items.
    PROGRESSIVE_SCORE_MULTIPLIER = "Progression Score Multiplier"

    EPISODE_COMPLETION_TOKEN = "Episode Completion Token"

    EPISODE_1_UNLOCK = "Episode 1 Unlock"
    EPISODE_2_UNLOCK = "Episode 2 Unlock"
    EPISODE_3_UNLOCK = "Episode 3 Unlock"
    EPISODE_4_UNLOCK = "Episode 4 Unlock"
    EPISODE_5_UNLOCK = "Episode 5 Unlock"
    EPISODE_6_UNLOCK = "Episode 6 Unlock"

    MINIKIT = "Minikit"
    TWO_MINIKITS = "Two Minikits"
    FIVE_MINIKITS = "Five Minikits"
    TEN_MINIKITS = "Ten Minikits"

    KYBER_BRICK = "Kyber Brick"

    POWER_UP = "Power Up"

    SILVER_STUD = "Silver Stud"
    GOLD_STUD = "Gold Stud"
    BLUE_STUD = "Blue Stud"
    PURPLE_STUD = "Purple Stud"


    # Events.
    SUPER_GONK_DROID = "Super Gonk Droid"

SHORT_NAME_TO_CHAPTER_UNLOCK_ITEM = {
    f"{episode}-{chapter}" for chapter in range(1, 7) for episode in range(1, 7)
}