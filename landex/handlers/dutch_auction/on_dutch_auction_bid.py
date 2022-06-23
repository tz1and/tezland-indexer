from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctions.parameter.bid import BidParameter
from landex.types.tezlandDutchAuctions.storage import TezlandDutchAuctionsStorage

# 

def getAuctionPrice(the_auction: models.DutchAuction, bid: Transaction[BidParameter, TezlandDutchAuctionsStorage]):
    """Returns current price in mutez.
    More or less pasted from dutch auction contract."""

    granularity = int(bid.storage.granularity)
    op_now = bid.data.timestamp

    # return start price if it hasn't started
    if (op_now <= the_auction.start_time):
        return the_auction.start_price
    else:
        # return end price if it's over
        if (op_now >= the_auction.end_time):
            return the_auction.end_price
        else:
            # alright, this works well enough. make 100% sure the math checks out (overflow, abs, etc)
            # probably by validating the input in create. to make sure intervals can't be negative.
            duration = abs(the_auction.end_time - the_auction.start_time) // granularity
            time_since_start = abs(op_now - the_auction.start_time) // granularity
            # NOTE: this can lead to a division by 0. auction duration must be > granularity.
            mutez_per_interval = (the_auction.start_price - the_auction.end_price) // duration.seconds
            time_deduction = mutez_per_interval * time_since_start.seconds

            current_price = the_auction.start_price - time_deduction

            return current_price


async def on_dutch_auction_bid(
    ctx: HandlerContext,
    bid: Transaction[BidParameter, TezlandDutchAuctionsStorage],
) -> None:
    # nothing to do but to delete the auction.
    # TODO: should we keep finished auctions in the index?
    auction_id = bid.parameter.auction_id

    auction = await models.DutchAuction.filter(id=int(auction_id)).get()

    auction.bid_op_hash = bid.data.hash
    auction.finishing_bid = getAuctionPrice(auction, bid)
    auction.finished = True
    await auction.save()

    # handle wl removal
    if bid.storage.whitelist_enabled:
        await auction.fetch_related("owner")
        is_primary = (auction.owner.address == bid.storage.administrator)

        if is_primary:
            wl = await models.DutchAuctionWhitelist.get(address=bid.data.sender_address)
            wl.used_count += 1
            wl.current_status = False
            await wl.save()
