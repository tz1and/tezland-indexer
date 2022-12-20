from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctionsV2.parameter.cancel import CancelParameter
from landex.types.tezlandDutchAuctionsV2.storage import TezlandDutchAuctionsV2Storage


async def on_cancel(
    ctx: HandlerContext,
    cancel: Transaction[CancelParameter, TezlandDutchAuctionsV2Storage],
) -> None:
    auction_key = cancel.parameter.auction_key
    owner = await models.Holder.get(address=auction_key.owner)

    auction = await models.DutchAuction.get(
        token_id=auction_key.token_id,
        fa2=auction_key.fa2,
        owner=owner)
    await auction.delete()
