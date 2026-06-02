from ..types import make_legacy_chapter, LegacyMinikitData

FALCON_FLIGHT = make_legacy_chapter(
    short_name="5-3",
    start_level="asteroidchase_d",
    minikits={
        "Behind Star Destroyer Minikit": LegacyMinikitData.new("asteroidchase_d", "m_pup1"),

        "Crater Minikit 1": LegacyMinikitData.new("asteroidchase_a", "m_pup2"),
        "Crater Minikit 2": LegacyMinikitData.new("asteroidchase_a", "m_pup3"),

        "Minikit Before Blocked Tunnel": LegacyMinikitData.new("asteroidchase_a", "m_pup4"),

        "Minikit After Blocked Tunnel": LegacyMinikitData.new("asteroidchase_b", "m_pup5"),

        "Shoot Torpedo Behind TIE Gate Minikit": LegacyMinikitData.new("asteroidchase_b", "m_pup6"),
        "Shoot Torpedo Before TIE Gate Minikit 1": LegacyMinikitData.new("asteroidchase_b", "m_pup7"),
        "Shoot Torpedo Before TIE Gate Minikit 2": LegacyMinikitData.new("asteroidchase_b", "m_pup8"),
        "Minikit Inside Space Slug Mouth": LegacyMinikitData.new("asteroidchase_b", "m_pup9"),

        "Minikit In Asteroid Before Torpedo Asteroid": LegacyMinikitData.new("asteroidchase_c", "m_pup10"),
    },
)
