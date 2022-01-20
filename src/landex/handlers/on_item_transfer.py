from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandItems.parameter.transfer import TransferParameter
from landex.types.tezlandItems.storage import TezlandItemsStorage


async def on_item_transfer(
    ctx: HandlerContext,
    transfer: Transaction[TransferParameter, TezlandItemsStorage],
) -> None:
    for t in transfer.parameter.__root__:
        sender, _ = await models.Holder.get_or_create(address=t.from_)
        for tx in t.txs:
            receiver, _ = await models.Holder.get_or_create(address=tx.to_)
            token = await models.ItemToken.filter(id=int(tx.token_id)).get()

            # update sender holding
            sender_holding, _ = await models.ItemTokenHolder.get_or_create(token=token, holder=sender)
            sender_holding.quantity -= int(tx.amount)
            await sender_holding.save()

            # update reciever holding
            receiver_holding, _ = await models.ItemTokenHolder.get_or_create(token=token, holder=receiver)
            receiver_holding.quantity += int(tx.amount)
            await receiver_holding.save()
