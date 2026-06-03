from ..types import make_legacy_chapter, LegacyMinikitData

THE_BATTLE_OF_ENDOR = make_legacy_chapter(
    short_name="6-4",
    start_level="endorbattle_a",
    minikits={
        "Minikit Left Of Spawn": LegacyMinikitData.new("endorbattle_a", "mk_0"),
        "Minikit Behind Wooden Gate": LegacyMinikitData.new("endorbattle_a", "mk_1"),
        "High Minikit Above Second Bridge": LegacyMinikitData.new("endorbattle_a", "mk_2"),

        "Boarded Up Minikit": LegacyMinikitData.new("endorbattle_b", "mk_1"),
        "Top Of River Minikit": LegacyMinikitData.new("endorbattle_b", "mk_0"),
        "Platform After Split Paths Minikit": LegacyMinikitData.new("endorbattle_b", "mk_2"),

        "Left Minikit Outside Bunker": LegacyMinikitData.new("endorbattle_c", "mk_1"),
        "Right Minikit Outside Bunker": LegacyMinikitData.new("endorbattle_c", "mk_0"),

        "Bunker Minikit After Hatch And Gap": LegacyMinikitData.new("endorbattle_c", "m_pup1"),
        "Bunker Buildable Minikit": LegacyMinikitData.new("endorbattle_c", "MINI06"),
    },
    extra_toggle_characters=(
        "Womp Rat",
        "Imperial Engineer",
        "Scout Trooper",
    ),
)
