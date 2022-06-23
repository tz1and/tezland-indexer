from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.place_items import PlaceItemsParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_place_items(
    ctx: HandlerContext,
    bid: Transaction[PlaceItemsParameter, TezlandWorldStorage],
) -> None:
    pass