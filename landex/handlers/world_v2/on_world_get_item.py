from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorldV2.parameter.get_item import GetItemParameter
from landex.types.tezlandWorldV2.storage import TezlandWorldV2Storage


async def on_world_get_item(
    ctx: HandlerContext,
    get_item: Transaction[GetItemParameter, TezlandWorldV2Storage],
) -> None:
    place_contract = await models.PlaceContract.get(address=get_item.parameter.chunk_key.place_key.fa2)
    place = await models.PlaceToken.get(token_id=int(get_item.parameter.chunk_key.place_key.id), contract=place_contract)
    issuer = (None if get_item.parameter.issuer is None else await models.Holder.get(address=get_item.parameter.issuer))

    item_placement = await models.WorldItemPlacement.get(
        place=place,
        issuer=issuer,
        item_id=int(get_item.parameter.item_id)).prefetch_related('item_token')

    collector, _ = await models.Holder.get_or_create(address=get_item.data.sender_address)

    await models.ItemCollectionHistory.create(
        place=place,
        item_token=item_placement.item_token,
        issuer=issuer,
        collector=collector,
        rate=item_placement.rate,
        op_hash=get_item.data.hash,
        level=get_item.data.level,
        timestamp=get_item.data.timestamp)

    # reduce amount or delete
    if item_placement.amount > 1:
        item_placement.amount -= 1
        await item_placement.save()
    else:
        await item_placement.delete()