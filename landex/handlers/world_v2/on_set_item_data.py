from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorldV2.parameter.set_item_data import SetItemDataParameter
from landex.types.tezlandWorldV2.storage import TezlandWorldV2Storage


async def on_set_item_data(
    ctx: HandlerContext,
    set_item_data: Transaction[SetItemDataParameter, TezlandWorldV2Storage],
) -> None:
    place_contract = await models.PlaceContract.get(address=set_item_data.parameter.chunk_key.place_key.fa2)
    place = await models.PlaceToken.get(token_id=int(set_item_data.parameter.chunk_key.place_key.id), contract=place_contract)

    for update_map_item in set_item_data.parameter.update_map:
        issuer = (None if update_map_item.key is None else await models.Holder.get(address=update_map_item.key))

        for update_list in update_map_item.value.values():
            for update_item in update_list:
                item_placement = await models.WorldItemPlacement.get(
                    place=place,
                    issuer=issuer,
                    chunk=set_item_data.parameter.chunk_key.chunk_id,
                    item_id=int(update_item.item_id)
                )

                item_placement.data = update_item.data
                await item_placement.save()
