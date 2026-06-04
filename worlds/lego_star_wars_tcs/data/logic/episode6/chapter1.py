from ..types import make_legacy_chapter, LegacyMinikitData

JABBAS_PALACE = make_legacy_chapter(
    short_name="6-1",
    minikits={
        "Minikit Behind Astromech Door": LegacyMinikitData.new("jabbaspalace_a", "mk_0"),
        "Minikit Outside Above Silver Bricks": LegacyMinikitData.new("jabbaspalace_a", "mk_1"),
        "Spawn Far Left Minikit": LegacyMinikitData.new("jabbaspalace_a", "mk_2"),
        "Minikit Behind Gate With B'Omarr Monk": LegacyMinikitData.new("jabbaspalace_a", "mk_3"),

        "Prison Protocol Room Porthole Minikit": LegacyMinikitData.new("jabbaspalace_b", "mk_0"),
        "Explode Prison Wall Minikit": LegacyMinikitData.new("jabbaspalace_b", "mk_1"),
        "Droid Room Porthole Minikit": LegacyMinikitData.new("jabbaspalace_b", "mk_2"),

        "Sith Force Grate Minikit": LegacyMinikitData.new("jabbaspalace_d", "mk_0"),
        "Imperial Gate Minikit": LegacyMinikitData.new("jabbaspalace_d", "mk_1"),

        "Rancor Pit Minikit": LegacyMinikitData.new("jabbaspalace_e", "m_pup1"),
    },
)
