from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandItems.parameter.burn import BurnParameter
from landex.types.tezlandItems.storage import TezlandItemsStorage


async def on_item_burn(
    ctx: HandlerContext,
    burn: Transaction[BurnParameter, TezlandItemsStorage],
) -> None:
    holder, _ = await models.Holder.get_or_create(address=burn.parameter.address)
    token = await models.ItemToken.filter(id=int(burn.parameter.token_id)).get()

    # update sender holding
    holding, _ = await models.ItemTokenHolder.get_or_create(token=token, holder=holder)
    holding.quantity -= int(burn.parameter.amount)
    await holding.save()
    
    # update token supply
    token.supply -= int(burn.parameter.amount)
    await token.save()
