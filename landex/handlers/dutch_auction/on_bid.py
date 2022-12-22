from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models
import landex.utils as utils

from landex.types.tezlandDutchAuctions.parameter.bid import BidParameter
from landex.types.tezlandDutchAuctions.storage import TezlandDutchAuctionsStorage


async def on_bid(
    ctx: HandlerContext,
    bid: Transaction[BidParameter, TezlandDutchAuctionsStorage],
) -> None:
    # If this bid call is after the upgrade, it's to update the metadata. skip it.
    # TODO: maybe do it by level.
    if bid.parameter.extension is not None and bid.parameter.extension["metadata_uri"] is not None:
        print("Op updated metadata, skipping.")
        return

    # nothing to do but to delete the auction.
    # TODO: should we keep finished auctions in the index?
    auction_id = bid.parameter.auction_id

    auction = await models.DutchAuction.get(transient_id=int(auction_id)).prefetch_related("owner")

    auction.bid_op_hash = bid.data.hash
    auction.finishing_bid = utils.getAuctionPrice(auction, int(bid.storage.granularity), bid.data.timestamp)
    auction.finished = True
    await auction.save()

    # handle wl removal
    # It seems wl is always removed, even if currently disabled.
    #if bid.storage.whitelist_enabled:
    is_primary = (auction.owner.address == bid.storage.administrator)

    if is_primary:
        wl = await models.DutchAuctionWhitelistV1.get_or_none(address=bid.data.sender_address)
        if wl and wl.current_status == True:
            wl.used_count += 1
            wl.current_status = False
            await wl.save()
