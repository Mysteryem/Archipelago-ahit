from rule_builder.rules import And, Or, HasAny, False_, True_

from ...macros import can_destroy_close_silver_bricks, can_self_destruct
from ...option_filters import logic_options
from ...rules import HasAbility, HasAllAbilities, HasAnyAbilities
from ...types import minikit_data, ExitData, Chapter, LocationData

from .....character_ability import *

INVASION_OF_NABOO = Chapter(
    name="Invasion of Naboo",
    episode_number=1,
    chapter_number=2,
    start_region="Forest Spawn",
    start_level="gungan_a",
    regions={
        "Forest Spawn": (
            # Expert logic could get past the tree without a jedi.
            ExitData("After First Fallen Tree", HasAbility(JEDI)),
        ),
        "After First Fallen Tree": (
            ExitData(
                "After Crashed MTT",
                logic_options(
                    base=HasAbility(JEDI),
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP)
                ),
                new_level="gungan_b",
            ),
        ),
        "After Crashed MTT": (
            ExitData("Cliff Face Ruins Entrance", new_level="gungan_b"),
        ),
        "Cliff Face Ruins Entrance": (
            # Hover across the gap or force down the mosaic.
            ExitData("Cliff Face Ruins Collapsing Debris Section", HasAnyAbilities(JEDI | HOVER)),
        ),
        "Cliff Face Ruins Collapsing Debris Section": (
            ExitData(
                "Cliff Face Ruins Past Collapsing Debris",
                logic_options(
                    base=HasAllAbilities(JEDI | HIGH_JUMP),
                    # Jedi triple jump gets more height than a high jump.
                    # There is, however a collapsing debris that sits in a dip, so requires a high triple jump to get on
                    # top without.
                    moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                    # From the first collapsing platform, a high double jump is just enough to collapse the second
                    # platform without needing a jedi.
                    # A jetpack can also get across here by jumping from each collapsing platform and then hovering to
                    # the next, but needs a High Jump/Jedi to get up at the start.
                    # Restarting the level is required to re-attempt, so this is in Hard logic.
                    hard=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM) & HasAny("Jar Jar Binks", "Captain Tarpals"),
                ),
            ),
            ExitData(
                "Cliff Face Ruins Raised Square",
                logic_options(
                    # Not expected, use the exit from "Cliff Face Ruins Past Collapsing Debris" instead.
                    base=False_(),
                    # Triple or high jump up to the first collapsing platform, then jumping from each collapsing
                    # platform and then hovering to the next, it is possible to get to the top of the raised square.
                    # Restarting the level is required to re-attempt, so this is in Hard logic.
                    hard=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM) & HasAbility(JETPACK),
                ),
            ),
        ),
        # This is the lower area around the Raised Square platform.
        "Cliff Face Ruins Past Collapsing Debris": (
            ExitData(
                "Cliff Face Ruins End Platform",
                logic_options(
                    # Force down the blocks from on top of the square to make a platform, then jump up.
                    base=HasAbility(JEDI),
                    # Triple jump up, ignoring the force blocks.
                    moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                ),
            ),
            ExitData(
                "Cliff Face Ruins Raised Square",
                logic_options(
                    # Force down the blocks on the top of the square and then high jump up.
                    base=HasAllAbilities(JEDI | HIGH_JUMP),
                    # Triple jump up (don't even need to force down the blocks).
                    moderate=HasAbility(JEDI),
                ),
            ),
        ),
        "Cliff Face Ruins Raised Square": (
            ExitData(
                "Cliff Face Ruins End Platform",
                logic_options(
                    # Not expected, use the exit from "Cliff Face Ruins Past Collapsing Debris" instead.
                    base=False_(),
                    # Jump and jetpack hover across.
                    normal=HasAbility(JETPACK),
                    # There is a cliff face alcove that gives extra starting height, so astromech hover is enough to
                    # cross.
                    # Triple jump can just jump straight over.
                    moderate=HasAnyAbilities(HOVER | JEDI | CAN_HIGH_JUMP_SLAM),
                    # A regular high jump can also just barely cross the gap from the cliff face alcove.
                    hard=HasAnyAbilities(HOVER | JEDI | CAN_HIGH_JUMP_SLAM | HIGH_JUMP),
                ),
            ),
            # This exit might not be needed, but including it won't really hurt.
            ExitData(
                # Just drop down.
                "Cliff Face Ruins Past Collapsing Debris",
            ),
        ),
        "Cliff Face Ruins End Platform": (
            ExitData(
                "Cliff Face Ruins Raised Square",
                logic_options(
                    # Not intended.
                    base=False_(),
                    normal=HasAbility(HOVER),
                    moderate=HasAnyAbilities(HOVER | JEDI | CAN_HIGH_JUMP_SLAM),
                ),
            ),
            ExitData(
                "Swamp Ruins Entrance",
                new_level="gungan_c"
            ),
        ),
        "Swamp Ruins Entrance": (
            ExitData(
                "Swamp Ruins",
                logic_options(
                    # Move the blocks out of the way to collapse the log.
                    base=HasAbility(JEDI),
                    # A triple jump can bypass the log entirely, but the jump is quite tight.
                    hard=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
                ),
            ),
        ),
        "Swamp Ruins": (
            # ExitData(
            #     "Swamp Behind MTT",
            #     logic_options(
            #         base=HasAbility(BOUNTY_HUNTER),
            #         normal=can_destroy_close_silver_bricks,
            #         # The collision for the MTT is enormous, though there's probably ways to get out-of-bounds to get
            #         # behind it.
            #     ),
            # ),
            ExitData(
                "Swamp Before Water",
                logic_options(
                    # High jump up to get on top of the collapsing debris.
                    base=HasAbility(HIGH_JUMP),
                    # Alternatively, jump + jetpack hover across from the higher swamp area.
                    normal=HasAnyAbilities(HIGH_JUMP | JETPACK),
                    # Triple jump up with a jedi instead.
                    moderate=HasAnyAbilities(JEDI | HIGH_JUMP | JETPACK),
                    # The collision on the boards is busted, and can be used to clip inside the wall, or jump on top of
                    # the wall.
                    hard=HasAnyAbilities(JEDI | HIGH_JUMP | JETPACK | CAN_JUMP_NORMAL_HEIGHT),
                ),
                new_level="gungan_e",
            ),
        ),
        # There is nothing of logical relevance here yet, so this region is disabled for now.
        # "Swamp Behind MTT": (),
        "Swamp Before Water": (
            ExitData(
                # Just walk.
                "Chapter Completion",
                new_level="gungan_status",
            ),
        ),
    },
    minikits={
        "Shoot Target Minikit": minikit_data(
            "Forest Spawn",
            logic_options(
                # Shoot the target, then force the boulders and jump up to the minikit.
                base=HasAllAbilities(JEDI | BLASTER),
                # Stacking the boulders allows an ewok to hit the target.
                # High jump can be expected instead of a jedi, but requires a blaster character.
                normal=Or(
                    HasAbility(JEDI) & HasAnyAbilities(BLASTER | WEAPON_EWOK),
                    HasAllAbilities(HIGH_JUMP | BLASTER)
                ),
                moderate=Or(
                    And(
                        HasAnyAbilities(JEDI | HIGH_JUMP),
                        Or(
                            HasAbility(BLASTER),
                            # The explosion allows Ewok to hit the target without needing a Jedi to move the boulders
                            # for extra height.
                            WEAPON_EWOK & (HasAny("Super Ewok Catapult", "Exploding Blaster Bolts")),
                            # Self-destruct can also hit the target.
                            can_self_destruct,
                        )
                    ),
                    # With only an ewok, a Jedi is still required to move the boulders so the ewok can hit the target.
                    HasAllAbilities(JEDI | WEAPON_EWOK),
                )
            ),
            pickup_name="m_pup2",
        ),
        "Destroy Fallen Tree Minikit": minikit_data(
            "After First Fallen Tree",
            HasAbility(JEDI),
            pickup_name="m_pup1",
        ),
        "Minikit Above Crashed MTT": minikit_data(
            "After First Fallen Tree",
            logic_options(
                # Destroy the MTT using the force.
                base=HasAbility(JEDI),
                # A high jump from the MTT's side-cannon is just enough to get on top of the MTT's hitbox.
                moderate=HasAnyAbilities(JEDI | HIGH_JUMP),
            ),
            pickup_name="m_pOOP1",
        ),
        "Minikit Under Crashed MTT": minikit_data(
            "After First Fallen Tree",
            HasAbility(JEDI),
            pickup_name="m_pOOP3",
        ),
        "High Minikit Above Steps": minikit_data(
            "After Crashed MTT",
            logic_options(
                base=HasAllAbilities(JEDI | HIGH_JUMP),
                moderate=HasAnyAbilities(JEDI | CAN_HIGH_JUMP_SLAM),
            ),
            pickup_name="m_pOOP2",
        ),
        "Minikit On Top Of Raised Square": minikit_data(
            "Cliff Face Ruins Raised Square",
            pickup_name="m_pup1",
        ),
        "Minikit In Ruins Alcove": minikit_data(
            "Swamp Ruins Entrance",
            HasAbility(JEDI),
            pickup_name="mk_2",
        ),
        "Minikit After Access Hatch": minikit_data(
            "Swamp Ruins",
            HasAbility(SHORTIE),
            pickup_name="mk_1",
        ),
        "Minikit In Boarded Up Room": minikit_data(
            "Swamp Ruins",
            logic_options(
                # Force the boards out of the way.
                base=HasAbility(JEDI),
                # The collision on the boards is broken, you can walk through them if you know what you're doing.
                moderate=True_(),
            ),
            pickup_name="mk_01",
        ),
        "Statue Puzzle Minikit": minikit_data(
            "Swamp Before Water",
            HasAbility(JEDI),
            pickup_name="m_pup1",
        ),
    },
    power_brick=LocationData("Cliff Face Ruins Past Collapsing Debris", HasAbility(BOUNTY_HUNTER))
)
