from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.get_item import GetItemParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_get_item(
    ctx: HandlerContext,
    bid: Transaction[GetItemParameter, TezlandWorldStorage],
) -> None:
    pass