from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorld.parameter.set_item_data import SetItemDataParameter
from landex.types.tezlandWorld.storage import TezlandWorldStorage


async def on_set_item_data(
    ctx: HandlerContext,
    set_item_data: Transaction[SetItemDataParameter, TezlandWorldStorage],
) -> None:
    place_contract = await models.Contract.get(address=set_item_data.storage.places_contract)
    place = await models.PlaceToken.get(token_id=int(set_item_data.parameter.lot_id), contract=place_contract)

    for (issuer_address, update_list) in set_item_data.parameter.update_map.items():
        issuer = await models.Holder.get(address=issuer_address)

        for update_item in update_list:
            item_placement = await models.WorldItemPlacement.get(
                place=place,
                issuer=issuer,
                item_id=int(update_item.item_id)
            )

            item_placement.data = update_item.item_data
            await item_placement.save()
