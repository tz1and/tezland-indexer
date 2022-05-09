from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandPlaces.parameter.mint import MintParameter
from landex.types.tezlandPlaces.storage import TezlandPlacesStorage
from landex.utils import fromhex


async def on_place_mint(
    ctx: HandlerContext,
    mint: Transaction[MintParameter, TezlandPlacesStorage],
) -> None:
    mint_counter = len(mint.parameter.__root__)
    for mint_batch_item in mint.parameter.__root__:
        # subtract decresing mint counter from last_token_id to get token_id
        token_id = int(mint.storage.last_token_id) - mint_counter
        holder, _ = await models.Holder.get_or_create(address=mint_batch_item.to_)
        
        minter = holder

        metadata = ''
        if mint_batch_item.metadata['']:
            metadata = fromhex(mint_batch_item.metadata[''])

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

        mint_counter -= 1
