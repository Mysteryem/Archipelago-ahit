from ..types import make_legacy_chapter, LegacyMinikitData

THE_GREAT_PIT_OF_CARKOON = make_legacy_chapter(
    short_name="6-2",
    minikits={
        "Walk The Plank Minikit": LegacyMinikitData.new("sarlaccpit_a", "mk_0"),
        "Barge Left Side Minikit": LegacyMinikitData.new("sarlaccpit_a", "mk_2"),
        "Build Four Skiff Cannons Minikit": LegacyMinikitData.new("sarlaccpit_a", "m_pup2"),
        "Barge Front Two Levers Minikit": LegacyMinikitData.new("sarlaccpit_a", "m_pup1"),
        "Barge Rear Three Levers Minikit": LegacyMinikitData.new("sarlaccpit_a", "m_pup3"),

        "Barge Interior Access Hatch Minikit": LegacyMinikitData.new("sarlaccpit_b", "m_pup1"),
        "Barge Interior Window Shutters Minikit": LegacyMinikitData.new("sarlaccpit_b", "m_pup2"),

        "Barge Deck Minikit Beneath Sail": LegacyMinikitData.new("sarlaccpit_c", "mk_0"),
        "Minikit Between Barge Deck Targets": LegacyMinikitData.new("sarlaccpit_c", "mk_1"),
        "Barge Deck Access Hatch Minikit": LegacyMinikitData.new("sarlaccpit_c", "mk_2"),
    },
)
