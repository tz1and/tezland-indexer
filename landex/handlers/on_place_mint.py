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
    assert len(mint.parameter.__root__) == 1
    for mint_batch_item in mint.parameter.__root__:
        # NOTE: this will fail if minter can mint multiple tokens
        token_id = int(mint.storage.last_token_id) - 1
        holder, _ = await models.Holder.get_or_create(address=mint_batch_item.to_)
        
        minter = holder
        if mint_batch_item.to_ != mint_Place.data.sender_address:
            minter, _ = await models.Holder.get_or_create(address=mint_Place.data.sender_address)

        metadata = ''
        if mint_Place.parameter.metadata:
            metadata = fromhex(mint_Place.parameter.metadata)

        token = models.PlaceToken(
            id=token_id,
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
