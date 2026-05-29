from ...rules import HasAbility, HasAbilityExceptCharacters, True_
from ...types import minikit_data, ExitData, Chapter, LocationData
from ...option_filters import logic_options
from .....character_ability import IS_A_VEHICLE, VEHICLE_BLASTER

BATTLE_OVER_CORUSCANT = Chapter(
    name="Battle Over Coruscant",
    episode_number=3,
    chapter_number=1,
    story_characters=(
        "Jedi Starfighter (Yellow)",
        "Jedi Starfighter (Red)",
    ),
    purchase_characters={
        "Droid Trifighter": 28000,
        "Vulture Droid": 30000,
        "Clone Arcfighter": 33000,
    },
    extra_toggle_characters=(
        # Completely useless in this level because it cannot shoot, and at least one unlocked vehicle is needed to
        # enter the chapter in the first place.
        # Interestingly, it can use the Self Destruct extra, but I could not find a use for this.
        "Buzz Droid",
    ),
    start_region="Space Battle Spawn",
    start_level="dogfight_a",
    extra_chapter_entrance_rules=logic_options(
        # In base logic, expect a blaster vehicle to fight back at the start.
        base=HasAbility(VEHICLE_BLASTER),
        # The first 2 minikits can be collected by ramming into them.
        normal=HasAbility(IS_A_VEHICLE),
    ),
    regions={
        "Space Battle Spawn": (
            ExitData("After First Destroyable Ship", HasAbility(VEHICLE_BLASTER)),
        ),
        "After First Destroyable Ship": (
            ExitData(
                "After Second Destroyable Ship",
                logic_options(
                    # Slave 1 just barely fits through the ship later in the level. To reduce confusion with newer
                    # players, and to potentially help with achieving True Jedi, any vehicle other than Slave 1 is
                    # expected for the base logic.
                    base=HasAbilityExceptCharacters(IS_A_VEHICLE, "Slave 1"),
                    normal=True_(),
                ),
            ),
        ),
        "After Second Destroyable Ship": (
            ExitData("Chapter Completion", new_level="dogfight_status"),
        ),
    },
    minikits={
        "Minikit 1": minikit_data(
            "Space Battle Spawn",
            pickup_name="m_pup1"
        ),
        "Minikit 2": minikit_data(
            "Space Battle Spawn",
            pickup_name="m_pup2"
        ),
        "Minikit 3": minikit_data(
            "After First Destroyable Ship",
            pickup_name="m_pup3"
        ),
        "Minikit 4": minikit_data(
            "After First Destroyable Ship",
            pickup_name="m_pup4"
        ),
        "Minikit 5": minikit_data(
            "After First Destroyable Ship",
            pickup_name="m_pup5"
        ),
        "Minikit 6": minikit_data(
            "After First Destroyable Ship",
            pickup_name="m_pup6"
        ),
        "Minikit 7": minikit_data(
            "After First Destroyable Ship",
            pickup_name="m_pup7"
        ),
        "Minikit 8": minikit_data(
            "After Second Destroyable Ship",
            pickup_name="m_pup8"
        ),
        "Minikit 9": minikit_data(
            "After Second Destroyable Ship",
            pickup_name="m_pup9"
        ),
        "Minikit 10": minikit_data(
            "After Second Destroyable Ship",
            pickup_name="m_pup10"
        ),
    },
    power_brick=LocationData("After Second Destroyable Ship")
)
