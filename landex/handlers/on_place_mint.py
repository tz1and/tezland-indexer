from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandPlaces.parameter.mint import MintParameter
from landex.types.tezlandPlaces.storage import TezlandPlacesStorage
from landex.types.tezlandMinter.parameter.mint_place import MintPlaceParameter
from landex.types.tezlandMinter.storage import TezlandMinterStorage
from landex.utils import fromhex
from landex.metadata import get_place_metadata


async def on_place_mint(
    ctx: HandlerContext,
    mint_Place: Transaction[MintPlaceParameter, TezlandMinterStorage],
    mint: Transaction[MintParameter, TezlandPlacesStorage],
) -> None:
    holder, _ = await models.Holder.get_or_create(address=mint.parameter.address)
    
    minter = holder
    if mint.parameter.address != mint_Place.data.sender_address:
        minter, _ = await models.Holder.get_or_create(address=mint_Place.data.sender_address)

    metadata = ''
    if mint_Place.parameter.metadata:
        metadata = fromhex(mint_Place.parameter.metadata)

    token = models.PlaceToken(
        id=mint.parameter.token_id,
        minter=minter,
        metadata=metadata,
        level=mint.data.level,
        timestamp=mint.data.timestamp
    )
    await token.save()

    holding, _ = await models.PlaceTokenHolder.get_or_create(token=token, holder=holder)
    await holding.save()

    # runs in retry_metadata deamon job now
    #await get_place_metadata(ctx.get_ipfs_datasource("local_ipfs"), token)
