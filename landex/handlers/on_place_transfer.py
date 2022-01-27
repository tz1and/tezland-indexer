from typing import Optional
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandPlaces.parameter.transfer import TransferParameter
from landex.types.tezlandPlaces.storage import TezlandPlacesStorage


async def on_place_transfer(
    ctx: HandlerContext,
    transfer: Transaction[TransferParameter, TezlandPlacesStorage],
) -> None:
    for t in transfer.parameter.__root__:
        sender, _ = await models.Holder.get_or_create(address=t.from_)
        for tx in t.txs:
            receiver, _ = await models.Holder.get_or_create(address=tx.to_)
            token = await models.PlaceToken.filter(id=int(tx.token_id)).get()

            # TODO: rather use balances like in item_transfer?

            # delete sender holding
            sender_holding, _ = await models.PlaceTokenHolder.get_or_create(token=token, holder=sender)
            await sender_holding.delete()

            # update reciever holding
            receiver_holding, _ = await models.PlaceTokenHolder.get_or_create(token=token, holder=receiver)
            await receiver_holding.save()
