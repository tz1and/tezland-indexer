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
    holder, _ = await models.Holder.get_or_create(address=mint.parameter.address)
    
    minter = holder
    if mint.parameter.address != mint_Item.data.sender_address:
        minter, _ = await models.Holder.get_or_create(address=mint_Item.data.sender_address)

    metadata = ''
    if mint_Item.parameter.metadata:
        metadata = fromhex(mint_Item.parameter.metadata)

    token = models.ItemToken(
        id=mint.parameter.token_id,
        royalties=mint_Item.parameter.royalties,
        minter=minter,
        metadata=metadata,
        supply=int(mint.parameter.amount),
        level=mint.data.level,
        timestamp=mint.data.timestamp
    )
    await token.save()

    holding, _ = await models.ItemTokenHolder.get_or_create(token=token, holder=holder, quantity=int(mint.parameter.amount))
    await holding.save()

    # runs in retry_metadata deamon job now
    #await get_item_metadata(ctx.get_ipfs_datasource("local_ipfs"), token)
