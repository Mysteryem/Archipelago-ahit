from .episode1 import CHAPTERS as EP1_CHAPTERS
from .episode2 import CHAPTERS as EP2_CHAPTERS
from .episode3 import CHAPTERS as EP3_CHAPTERS
from .episode4 import CHAPTERS as EP4_CHAPTERS
from .episode5 import CHAPTERS as EP5_CHAPTERS
from .episode6 import CHAPTERS as EP6_CHAPTERS
from .extra_toggle import PRE_RULE_OPTIMIZER as EXTRA_TOGGLE_PRE_RULE_OPTIMIZER
from .types import Chapter, RULE_OPTIMIZER

__all__ = [
    "EPISODES",
    "CHAPTERS_BY_SHORT_NAME",
    "CHAPTERS_BY_NUMBERS",
]

EPISODES = (
    EP1_CHAPTERS,
    EP2_CHAPTERS,
    EP3_CHAPTERS,
    EP4_CHAPTERS,
    EP5_CHAPTERS,
    EP6_CHAPTERS,
)

CHAPTERS_BY_SHORT_NAME: dict[str, Chapter] = {
    chapter.short_name: chapter for episode in EPISODES for chapter in episode
}
CHAPTERS_BY_NUMBERS: dict[int, dict[int, Chapter]] = {
    i: {j: chapter for j, chapter in enumerate(episode, start=1)}
    for i, episode in enumerate(EPISODES, start=1)
}

# Free up memory used by the rule optimizers.
RULE_OPTIMIZER.purge_memodict()
EXTRA_TOGGLE_PRE_RULE_OPTIMIZER.purge_memodict()
