from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.remove_items import RemoveItemsParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_remove_items(
    ctx: HandlerContext,
    bid: Transaction[RemoveItemsParameter, TezlandWorldStorage],
) -> None:
    pass