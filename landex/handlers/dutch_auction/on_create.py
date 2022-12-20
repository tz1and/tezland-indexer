from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctions.parameter.create import CreateParameter
from landex.types.tezlandDutchAuctions.storage import TezlandDutchAuctionsStorage


async def on_create(
    ctx: HandlerContext,
    create: Transaction[CreateParameter, TezlandDutchAuctionsStorage],
) -> None:
    auction_id = int(create.storage.auction_id) - 1
    owner, _ = await models.Holder.get_or_create(address=create.data.sender_address)
    
    auction = models.DutchAuction(
        transient_id=auction_id,
        owner=owner,
        token_id=create.parameter.token_id,
        start_price=create.parameter.start_price,
        end_price=create.parameter.end_price,
        start_time=create.parameter.start_time,
        end_time=create.parameter.end_time,
        fa2=create.parameter.fa2,
        level=create.data.level,
        timestamp=create.data.timestamp,
        is_primary=(owner.address == create.storage.administrator)
    )
    await auction.save()
