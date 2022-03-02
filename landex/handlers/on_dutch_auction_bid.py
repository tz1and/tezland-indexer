from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctions.parameter.bid import BidParameter
from landex.types.tezlandDutchAuctions.storage import TezlandDutchAuctionsStorage


async def on_dutch_auction_bid(
    ctx: HandlerContext,
    bid: Transaction[BidParameter, TezlandDutchAuctionsStorage],
) -> None:
    # nothing to do but to delete the auction.
    # TODO: should we keep finished auctions in the index?
    auction_id = bid.parameter.auction_id

    auction = await models.DutchAuction.filter(id=int(auction_id)).get()
    await auction.delete()
