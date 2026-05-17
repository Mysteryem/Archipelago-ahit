from rule_builder.rules import Rule, TWorld
from rule_builder.options import OptionFilter

from ...options import LogicDifficulty

normal_logic = (OptionFilter(LogicDifficulty, LogicDifficulty.option_normal, "ge"),)
moderate_logic = (OptionFilter(LogicDifficulty, LogicDifficulty.option_moderate, "ge"),)
hard_logic = (OptionFilter(LogicDifficulty, LogicDifficulty.option_hard, "ge"),)

base_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_none),)
normal_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_normal),)
moderate_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_moderate),)
hard_logic_only = (OptionFilter(LogicDifficulty, LogicDifficulty.option_hard),)

base_and_normal_logic_only = (
    OptionFilter(LogicDifficulty, LogicDifficulty.option_normal, "le"),
)

logic_expects_fighting_all_enemies = base_logic_only
extras_in_logic = normal_logic

# Entrance Rando does not exist currently, but this can be used to mark rules as only being relevant to entrance rando,
# and then filtering them out (replacing them with False_()).
entrance_rando = (OptionFilter(LogicDifficulty, float("nan"), "eq"),)


def logic_options(
        base: Rule[TWorld],
        normal: Rule[TWorld] | None = None,
        moderate: Rule[TWorld] | None = None,
        hard: Rule[TWorld] | None = None,
) -> Rule[TWorld]:
    if normal is None:
        normal = base
    if moderate is None:
        moderate = normal
    if hard is None:
        hard = moderate

    if hard == base:
        # This is not really a problem, but it could indicate an issue elsewhere.
        raise Exception("Hard and Base rules are the same.")

    return (
            (base & base_logic_only)
            | (normal & normal_logic_only)
            | (moderate & moderate_logic_only)
            | (hard & hard_logic_only)
    )
