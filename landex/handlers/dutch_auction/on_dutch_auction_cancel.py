from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctions.parameter.cancel import CancelParameter
from landex.types.tezlandDutchAuctions.storage import TezlandDutchAuctionsStorage


async def on_dutch_auction_cancel(
    ctx: HandlerContext,
    cancel: Transaction[CancelParameter, TezlandDutchAuctionsStorage],
) -> None:
    auction_id = cancel.parameter.auction_id

    await models.DutchAuction.filter(transient_id=int(auction_id)).delete()
