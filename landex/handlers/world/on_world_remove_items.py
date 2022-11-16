from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.remove_items import RemoveItemsParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_world_remove_items(
    ctx: HandlerContext,
    remove_items: Transaction[RemoveItemsParameter, TezlandWorldStorage],
) -> None:
    place = await models.PlaceToken.get(token_id=int(remove_items.parameter.lot_id), contract=remove_items.storage.places_contract)

    for (issuer_address, item_list) in remove_items.parameter.remove_map.items():
        issuer = await models.Holder.get(address=issuer_address)

        for item_id in item_list:
            item_placement = await models.WorldItemPlacement.get(
                place=place,
                issuer=issuer,
                item_id=int(item_id))

            await item_placement.delete()
