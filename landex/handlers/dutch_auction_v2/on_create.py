from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctionsV2.parameter.create import CreateParameter
from landex.types.tezlandDutchAuctionsV2.storage import TezlandDutchAuctionsV2Storage


async def on_create(
    ctx: HandlerContext,
    create: Transaction[CreateParameter, TezlandDutchAuctionsV2Storage],
) -> None:
    auction_key = create.parameter.auction_key
    (owner, _) = await models.Holder.get_or_create(address=create.data.sender_address)
    
    auction = models.DutchAuction(
        owner=owner,
        token_id=auction_key.token_id,
        start_price=create.parameter.auction.start_price,
        end_price=create.parameter.auction.end_price,
        start_time=create.parameter.auction.start_time,
        end_time=create.parameter.auction.end_time,
        fa2=auction_key.fa2,
        level=create.data.level,
        timestamp=create.data.timestamp,
        is_primary=(owner.address == create.storage.administrator)
    )
    await auction.save()
