from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models
import landex.utils as utils

from landex.types.tezlandDutchAuctionsV2.parameter.bid import BidParameter
from landex.types.tezlandDutchAuctionsV2.storage import TezlandDutchAuctionsV2Storage


async def on_bid(
    ctx: HandlerContext,
    bid: Transaction[BidParameter, TezlandDutchAuctionsV2Storage],
) -> None:
    auction_key = bid.parameter.auction_key
    owner = await models.Holder.get(address=auction_key.owner)

    auction = await models.DutchAuction.get(
        token_id=auction_key.token_id,
        fa2=auction_key.fa2,
        owner=owner,
        finished=False)

    auction.bid_op_hash = bid.data.hash
    auction.finishing_bid = utils.getAuctionPrice(auction, int(bid.storage.settings.granularity), bid.data.timestamp)
    auction.finished = True
    await auction.save()

    # handle wl removal
    # It seems wl is always removed, even if's currently disabled.
    if auction.is_primary:
        wl = await models.DutchAuctionWhitelist.get_or_none(fa2=bid.parameter.auction_key.fa2, address=bid.data.sender_address)
        if wl and wl.current_status == True:
            wl.used_count += 1
            wl.current_status = False
            await wl.save()
