from ..types import make_legacy_chapter, LegacyMinikitData

INTO_THE_DEATH_STAR = make_legacy_chapter(
    short_name="6-6",
    minikits={
        "Star Destroyer Minikit 1": LegacyMinikitData.new("deathstar2battle_a", "m_pup1"),
        "Star Destroyer Minikit 2": LegacyMinikitData.new("deathstar2battle_a", "m_pup2"),

        "Torpedo Pipes Minikit": LegacyMinikitData.new("deathstar2battle_b", "m_pup3"),
        "First TIE Gate Minikit": LegacyMinikitData.new("deathstar2battle_b", "m_pup4"),

        "Hidden Corner Path Minikit": LegacyMinikitData.new("deathstar2battle_c", "m_pup5"),
        "Second TIE Gate Minikit": LegacyMinikitData.new("deathstar2battle_c", "m_pup6"),

        "Reactor Core Minikit": LegacyMinikitData.new("deathstar2battle_d", "m_pup7"),

        "Escape Minikit 1": LegacyMinikitData.new("deathstar2battle_e", "m_pup8"),

        "Escape Minikit 2": LegacyMinikitData.new("deathstar2battle_f", "m_pup9"),

        "Escape Minikit 3": LegacyMinikitData.new("deathstar2battle_g", "m_pup10"),
    },
)
