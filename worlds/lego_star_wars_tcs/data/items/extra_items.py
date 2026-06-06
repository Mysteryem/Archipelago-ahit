from dataclasses import dataclass
from typing import ClassVar

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