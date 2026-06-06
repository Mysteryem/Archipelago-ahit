from dataclasses import dataclass
from typing import ClassVar

from ..areas import Area
from ..extras import Extra

from . import EXTRA_ITEMS_BASE, GenericItemData, ItemType


@dataclass(frozen=True)
class ExtraData(GenericItemData):
    extra: Extra
    item_type: ClassVar[ItemType] = "Extra"

    @classmethod
    def ap_item(
            cls,
            extra: Extra
    ):
        return cls(
            code=extra + EXTRA_ITEMS_BASE,
            name=extra.readable_name,
            extra=extra,
        )

EXTRA_DATA: list[ExtraData] = [
    ExtraData.ap_item(extra) for extra in Extra
]
POWER_BRICK_EXTRAS: frozenset[Extra] = frozenset({
    area.extra for area in Area if area.extra is not None
})
NON_POWER_BRICK_EXTRAS: frozenset[Extra] = frozenset({
    extra for extra in Extra if extra not in POWER_BRICK_EXTRAS
})
PURCHASABLE_NON_POWER_BRICK_EXTRAS: frozenset[Extra] = frozenset({
    extra for extra in NON_POWER_BRICK_EXTRAS if extra.purchase_cost is not None
})