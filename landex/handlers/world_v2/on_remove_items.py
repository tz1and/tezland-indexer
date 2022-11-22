from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorldV2.parameter.remove_items import RemoveItemsParameter
from landex.types.tezlandWorldV2.storage import TezlandWorldV2Storage


async def on_remove_items(
    ctx: HandlerContext,
    remove_items: Transaction[RemoveItemsParameter, TezlandWorldV2Storage],
) -> None:
    place_contract = await models.PlaceContract.get(address=remove_items.parameter.place_key.fa2)
    place = await models.PlaceToken.get(token_id=int(remove_items.parameter.place_key.id), contract=place_contract)

    for (chunk_id, issuer_map) in remove_items.parameter.remove_map.items():
        for remove_map_item in issuer_map:
            issuer = (None if remove_map_item.key is None else await models.Holder.get(address=remove_map_item.key))

            for item_list in remove_map_item.value.values():
                for item_id in item_list:
                    item_placement = await models.WorldItemPlacement.get(
                        place=place,
                        issuer=issuer,
                        chunk=int(chunk_id),
                        item_id=int(item_id))

                    await item_placement.delete()
