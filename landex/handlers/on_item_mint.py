from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandItems.parameter.mint import MintParameter
from landex.types.tezlandItems.storage import TezlandItemsStorage
from landex.types.tezlandMinter.parameter.mint_item import MintItemParameter
from landex.types.tezlandMinter.storage import TezlandMinterStorage
from landex.utils import fromhex
from landex.metadata import get_item_metadata


async def on_item_mint(
    ctx: HandlerContext,
    mint_Item: Transaction[MintItemParameter, TezlandMinterStorage],
    mint: Transaction[MintParameter, TezlandItemsStorage],
) -> None:
    assert len(mint.parameter.__root__) == 1
    for mint_batch_item in mint.parameter.__root__:
        # NOTE: this will fail if minter can mint multiple tokens
        token_id = int(mint.storage.last_token_id) - 1
        holder, _ = await models.Holder.get_or_create(address=mint_batch_item.to_)
        
        minter = holder
        if mint_batch_item.to_ != mint_Item.data.sender_address:
            minter, _ = await models.Holder.get_or_create(address=mint_Item.data.sender_address)

        metadata = ''
        if mint_Item.parameter.metadata:
            metadata = fromhex(mint_Item.parameter.metadata)

        token = models.ItemToken(
            id=token_id,
            royalties=mint_Item.parameter.royalties,
            minter=minter,
            metadata=metadata,
            supply=int(mint_batch_item.amount),
            level=mint.data.level,
            timestamp=mint.data.timestamp
        )
        await token.save()

        holding, _ = await models.ItemTokenHolder.get_or_create(token=token, holder=holder, quantity=int(mint_batch_item.amount))
        await holding.save()

        # runs in retry_metadata deamon job now
        #await get_item_metadata(ctx.get_ipfs_datasource("local_ipfs"), token)
