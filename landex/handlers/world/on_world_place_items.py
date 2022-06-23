from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.place_items import PlaceItemsParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_place_items(
    ctx: HandlerContext,
    place_items: Transaction[PlaceItemsParameter, TezlandWorldStorage],
) -> None:
    issuer = await models.Holder.get(address=place_items.data.sender_address)
    place = await models.PlaceToken.get(id=int(place_items.parameter.lot_id))

    place_next_id = int(place_items.storage.places.get(place_items.parameter.lot_id).next_id)

    place_items_counter = len(place_items.parameter.item_list)
    for i in place_items.parameter.item_list:
        # subtract decresing counter from next_id to get item_id
        item_id = place_next_id - place_items_counter

        item_token = await models.ItemToken.get(id=int(i.item.token_id))

        await models.WorldItemPlacement.create(
            place=place,
            issuer=issuer,
            item_id=item_id,
            item_token=item_token,
            token_amount=i.item.token_amount,
            mutez_per_token=i.item.mutez_per_token,
            item_data=i.item.item_data,
            level=place_items.data.level,
            timestamp=place_items.data.timestamp)

        place_items_counter -= 1
