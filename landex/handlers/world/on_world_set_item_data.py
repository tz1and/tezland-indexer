from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.set_item_data import SetItemDataParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_set_item_data(
    ctx: HandlerContext,
    bid: Transaction[SetItemDataParameter, TezlandWorldStorage],
) -> None:
    pass