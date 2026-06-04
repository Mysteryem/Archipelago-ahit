from ..types import make_legacy_chapter, LegacyMinikitData

CLOUD_CITY_TRAP = make_legacy_chapter(
    short_name="5-5",
    minikits={
        "Minikit Around Corner After Bridge": LegacyMinikitData.new("cloudcitytrap_a", "m_pup1"),
        "Bounty Hunter Panel Room Minikit": LegacyMinikitData.new("cloudcitytrap_a", "pup1"),
        "Carbonite Chamber Minikit": LegacyMinikitData.new("cloudcitytrap_a", "pup2"),

        "Vader Chase High Minikit 1": LegacyMinikitData.new("cloudcitytrap_c", "pup3"),
        "Vader Chase High Minikit 2": LegacyMinikitData.new("cloudcitytrap_c", "pup1"),

        "Access Hatch Caged Minikit": LegacyMinikitData.new("cloudcitytrap_c", "pup2"),

        "Final Vader Chase Spawn Minikit": LegacyMinikitData.new("cloudcitytrap_b", "m_pup2"),
        "Final Vader Chase Platform Behind Camera Minikit": LegacyMinikitData.new("cloudcitytrap_b", "mk_0"),
        "Final Vader Chase Imperial Room Minikit": LegacyMinikitData.new("cloudcitytrap_b", "mk_1"),
        "Below Floor Minikit Across From Round Window": LegacyMinikitData.new("cloudcitytrap_b", "m_pup1"),
    },
)
