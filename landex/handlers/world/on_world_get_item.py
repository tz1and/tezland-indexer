from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.get_item import GetItemParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_get_item(
    ctx: HandlerContext,
    get_item: Transaction[GetItemParameter, TezlandWorldStorage],
) -> None:
    # If this bid call is after the upgrade, it's to update the metadata. skip it.
    # TODO: maybe do it by level.
    if get_item.parameter.extension is not None and get_item.parameter.extension["metadata_uri"] is not None:
        print("Op updated metadata, skipping.")
        return

    place_contract = await models.PlaceContract.get(address=get_item.storage.places_contract)
    place = await models.PlaceToken.get(token_id=int(get_item.parameter.lot_id), contract=place_contract)
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