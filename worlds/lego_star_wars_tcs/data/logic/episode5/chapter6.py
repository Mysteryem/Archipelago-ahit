from ..types import make_legacy_chapter, LegacyMinikitData, minikit_data

FOUNTAINS_MINIKIT_NAME = "Build Three Fountain Sculptures Minikit"

BETRAYAL_OVER_BESPIN = make_legacy_chapter(
    short_name="5-6",
    start_level="cloudcityescape_a",
    minikits={
        "Spawn Protocol Panel Room Minikit": LegacyMinikitData.new("cloudcityescape_a", "pup4"),
        # This is also in cloudcityescape_c as "pup1". Note that "pup5" is used for a different minikit in
        # cloudcityescape_c.
        FOUNTAINS_MINIKIT_NAME: LegacyMinikitData("cloudcityescape_a", ("pup1", "pup5")),
        "Astromech Door Platforming Minikit": LegacyMinikitData.new("cloudcityescape_a", "pup2"),
        "Boba Fight Room": LegacyMinikitData.new("cloudcityescape_a", "pup3"),
        "Force Chairs Minikit": LegacyMinikitData.new("cloudcityescape_a", "pup6"),
        "Bounty Hunter Area Force Plant Pots Minikit": LegacyMinikitData.new("cloudcityescape_a", "pup7"),

        "High Minikit Above Push Blocks": LegacyMinikitData.new("cloudcityescape_c", "pup2"),
        "Sith Force Double Score Zone Minikit": LegacyMinikitData.new("cloudcityescape_c", "pup3"),
        "Millennium Falcon Minikit": LegacyMinikitData.new("cloudcityescape_c", "pup4"),
        "Minikit Behind Camera After Imperial Elevator": LegacyMinikitData.new("cloudcityescape_c", "pup5"),
    },
    extra_toggle_characters=(
        "Han Solo (frozen in carbonite)",
    )
)

# This is one of the only Minikits in the entire game that is split across multiple levels.
BETRAYAL_OVER_BESPIN.level_minikits["cloudcityescape_c"][FOUNTAINS_MINIKIT_NAME] \
    = minikit_data("cloudcityescape_c", pickup_name="pup1")