# Some utility
import sys
import datetime
import logging

from dipdup.context import DipDupContext
from dipdup.datasources.tzkt.datasource import TzktDatasource

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


async def addContract(ctx: DipDupContext, address: str, owner: str | None = None, level: int = sys.maxsize, timestamp: datetime = 0):
    tzkt: TzktDatasource = ctx.get_tzkt_datasource("tzkt_mainnet")

    big_maps = await tzkt.get_contract_big_maps(address)
    metadata_ptr: int = -1
    for big_map in big_maps:
        if (big_map["path"] == "metadata"):
            metadata_ptr = int(big_map["ptr"])
            #print(f"found metadata map at: {metadata_ptr}")
            break

    metadata_uri = "error_no_metadata"
    if metadata_ptr >= 0:
        # TODO: don't specify level, offset, limit! waiting for dipdup fix.
        metadata_map = await tzkt.get_big_map(metadata_ptr, active=True, level=level, offset=0, limit=10)
        
        for item in metadata_map:
            if item["key"] == "":
                metadata_uri = bytes.fromhex(item["value"]).decode()
                #print(f"found metadata_uri: {metadata_uri}")
                break

    owner_model = None
    if owner is not None:
        owner_model, _ = await models.Holder.get_or_create(address=owner)

    await models.Contract.create(address=address, owner=owner_model, metadata_uri=metadata_uri, level=level, timestamp=timestamp)
