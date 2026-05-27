from .episode1 import CHAPTERS as EP1_CHAPTERS
from .episode2 import CHAPTERS as EP2_CHAPTERS
from .episode3 import CHAPTERS as EP3_CHAPTERS
from .types import Chapter

__all__ = [
    "EPISODES"
]

EPISODES = (
    EP1_CHAPTERS,
    EP2_CHAPTERS,
    EP3_CHAPTERS,
)

CHAPTERS_BY_SHORT_NAME: dict[str, Chapter] = {
    chapter.short_name: chapter for episode in EPISODES for chapter in episode
}
