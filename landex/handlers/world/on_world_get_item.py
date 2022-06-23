from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.get_item import GetItemParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_get_item(
    ctx: HandlerContext,
    get_item: Transaction[GetItemParameter, TezlandWorldStorage],
) -> None:
    place = await models.PlaceToken.get(id=int(get_item.parameter.lot_id))
    issuer = await models.Holder.get(address=get_item.parameter.issuer)

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
        mutez_per_token=item_placement.mutez_per_token,
        level=get_item.data.level,
        timestamp=get_item.data.timestamp)

    # reduce amount or delete
    if item_placement.token_amount > 1:
        item_placement.token_amount -= 1
        await item_placement.save()
    else:
        await item_placement.delete()