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
    for burn_batch_item in burn.parameter.__root__:
        holder, _ = await models.Holder.get_or_create(address=burn_batch_item.from_)
        token = await models.ItemToken.filter(id=int(burn_batch_item.token_id)).get()

        # update sender holding
        holding, _ = await models.ItemTokenHolder.get_or_create(token=token, holder=holder)
        holding.quantity -= int(burn_batch_item.amount)
        await holding.save()

        # update token supply
        token.supply -= int(burn_batch_item.amount)
        await token.save()
