# Some utility
import datetime
import logging

import landex.models as models

_logger = logging.getLogger(__name__)


def clean_null_bytes(string: str) -> str:
    return string.replace('\x00','')


def fromhex(hexbytes: str) -> str:
    try:
        return clean_null_bytes(bytes.fromhex(hexbytes).decode('utf-8'))
    except Exception as err:
        _logger.error(f'Failed to decode {hexbytes} as utf-8 string: {err}')
    return ''


def getAuctionPrice(the_auction: models.DutchAuction, granularity: int, op_now: datetime):
    """Returns current price in mutez.
    More or less pasted from dutch auction contract."""

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