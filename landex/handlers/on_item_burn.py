from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandFA2Fungible.parameter.burn import BurnParameter
from landex.types.tezlandFA2Fungible.storage import TezlandFA2FungibleStorage


async def on_item_burn(
    ctx: HandlerContext,
    burn: Transaction[BurnParameter, TezlandFA2FungibleStorage],
) -> None:
    for burn_batch_item in burn.parameter.__root__:
        holder, _ = await models.Holder.get_or_create(address=burn_batch_item.from_)
        contract = await models.ItemContract.get(address=burn.data.target_address)
        token = await models.ItemToken.get(token_id=int(burn_batch_item.token_id), contract=contract)

        # update sender holding
        holding, _ = await models.ItemTokenHolder.get_or_create(token=token, holder=holder)
        holding.quantity -= int(burn_batch_item.amount)
        if holding.quantity <= 0:
            await holding.delete()
        else:
            await holding.save()

        # update token supply
        token.supply -= int(burn_batch_item.amount)
        if token.supply <= 0:
            await token.delete()

            # do not delete metadata!
            # await token.metadata.delete()
            #await models.ItemTokenMetadata.filter(token_id=token.token_id, contract=contract).delete()
            # delete tags
            # NOTE: Tag map should cascade.
            #await models.ItemTagMap.filter(item_metadata=metadataId).delete()
            # NOTE: orphaned tags need to be deleted as well, eventually.

            # NOTE: delete remaining holders? shouldn't have to,
            #holders = await models.ItemTokenHolder.filter(token=token) ...
        else:
            await token.save()
