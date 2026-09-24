from . import LegoStarWarsWorldTestBase
from ..options import get_option_name, EnabledChaptersCount, LogicDifficulty, StartingChapter

_BASE_OPTIONS = {
    get_option_name(StartingChapter): StartingChapter.option_random_chapter,
    get_option_name(EnabledChaptersCount): EnabledChaptersCount.range_end,
}


class TestBaseLogicAllChapters(LegoStarWarsWorldTestBase):
    options = _BASE_OPTIONS | {
        get_option_name(LogicDifficulty): LogicDifficulty.option_none,
    }

class TestNormalLogicAllChapters(LegoStarWarsWorldTestBase):
    options = _BASE_OPTIONS | {
        get_option_name(LogicDifficulty): LogicDifficulty.option_normal,
    }

class TestModerateLogicAllChapters(LegoStarWarsWorldTestBase):
    options = _BASE_OPTIONS | {
        get_option_name(LogicDifficulty): LogicDifficulty.option_moderate,
    }

class TestHardLogicAllChapters(LegoStarWarsWorldTestBase):
    options = _BASE_OPTIONS | {
        get_option_name(LogicDifficulty): LogicDifficulty.option_hard,
    }