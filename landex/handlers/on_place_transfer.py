from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandFA2NFT.parameter.transfer import TransferParameter
from landex.types.tezlandFA2NFT.storage import TezlandFA2NFTStorage


async def on_place_transfer(
    ctx: HandlerContext,
    transfer: Transaction[TransferParameter, TezlandFA2NFTStorage],
) -> None:
    contract = await models.Contract.get(address=transfer.data.target_address)

    for t in transfer.parameter.__root__:
        sender, _ = await models.Holder.get_or_create(address=t.from_)
        for tx in t.txs:
            receiver, _ = await models.Holder.get_or_create(address=tx.to_)
            token = await models.PlaceToken.get(token_id=int(tx.token_id), contract=contract)

            # TODO: rather use balances like in item_transfer?

            # delete sender holding
            sender_holding, _ = await models.PlaceTokenHolder.get_or_create(token=token, holder=sender)
            await sender_holding.delete()

            # update reciever holding
            receiver_holding, _ = await models.PlaceTokenHolder.get_or_create(token=token, holder=receiver)
            await receiver_holding.save()
