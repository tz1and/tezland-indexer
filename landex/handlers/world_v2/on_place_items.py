from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorldV2.parameter.place_items import PlaceItemsParameter
from landex.types.tezlandWorldV2.storage import TezlandWorldV2Storage, Chunk, Key

from typing import List


def find_chunk(chunk_list: List[Chunk], chunk_key: Key) -> Chunk:
    for x in chunk_list:
        if x.key == chunk_key:
            return x
    assert False

def count_items_to_place(place_item_param: PlaceItemsParameter) -> int:
    place_items_counter: int = 0
    for fa2_map in place_item_param.place_item_map.values():
        for item_list in fa2_map.values():
            place_items_counter += len(item_list)
    return place_items_counter

async def on_place_items(
    ctx: HandlerContext,
    place_items: Transaction[PlaceItemsParameter, TezlandWorldV2Storage],
) -> None:
    issuer = await models.Holder.get(address=place_items.data.sender_address)
    place_contract = await models.PlaceContract.get(address=place_items.parameter.place_key.fa2)
    place = await models.PlaceToken.get(token_id=int(place_items.parameter.place_key.id), contract=place_contract)

    for (chunk_id, issuer_map) in place_items.parameter.place_item_map.items():
        chunk_key = Key(place_key=place_items.parameter.place_key, chunk_id=chunk_id)
        chunk = find_chunk(place_items.storage.chunks, chunk_key)
        chunk_next_id = int(chunk.value.next_id)

        place_items_counter = count_items_to_place(place_items.parameter)

        for (send_to_place, fa2_map) in issuer_map.items():
            send_to_place_bool = False if send_to_place.lower() == "false" else True

            for (fa2, item_list) in fa2_map.items():
                item_contract = await models.ItemContract.get(address=fa2)
                for i in item_list:
                    # subtract decresing counter from next_id to get item_id
                    item_id = chunk_next_id - place_items_counter

                    item_token = await models.ItemToken.get(token_id=int(i.item.token_id), contract=item_contract)

                    await models.WorldItemPlacement.create(
                        place=place,
                        issuer=(None if send_to_place_bool else issuer),
                        item_id=item_id,
                        chunk=int(chunk_id),
                        item_token=item_token,
                        amount=int(i.item.amount),
                        rate=int(i.item.rate),
                        data=i.item.data,
                        level=place_items.data.level,
                        timestamp=place_items.data.timestamp)

                    place_items_counter -= 1
