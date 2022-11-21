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
    place_contract = await models.PlaceContract.get(address=place_items.storage.places_contract)
    place = await models.PlaceToken.get(token_id=int(place_items.parameter.lot_id), contract=place_contract)

    item_contract = await models.ItemContract.get(address=place_items.storage.items_contract)

    place_next_id = int(place_items.storage.places.get(place_items.parameter.lot_id).next_id)

    place_items_counter = len(place_items.parameter.item_list)
    for i in place_items.parameter.item_list:
        # subtract decresing counter from next_id to get item_id
        item_id = place_next_id - place_items_counter

        item_token = await models.ItemToken.get(token_id=int(i.item.token_id), contract=item_contract)

        await models.WorldItemPlacement.create(
            place=place,
            issuer=issuer,
            item_id=item_id,
            chunk=0,
            item_token=item_token,
            amount=i.item.token_amount,
            rate=i.item.mutez_per_token,
            data=i.item.item_data,
            level=place_items.data.level,
            timestamp=place_items.data.timestamp)

        place_items_counter -= 1
