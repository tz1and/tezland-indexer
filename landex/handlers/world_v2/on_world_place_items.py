from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorldV2.parameter.place_items import PlaceItemsParameter, ChunkKey
from landex.types.tezlandWorldV2.storage import TezlandWorldV2Storage, Chunk

from typing import List


def find_chunk(chunk_list: List[Chunk], chunk_key: ChunkKey) -> Chunk:
    for x in chunk_list:
        if x.key == chunk_key:
            return x
    assert False

#def count_items_to_place()

async def on_world_place_items(
    ctx: HandlerContext,
    place_items: Transaction[PlaceItemsParameter, TezlandWorldV2Storage],
) -> None:
    issuer = await models.Holder.get(address=place_items.data.sender_address)
    place_contract = await models.PlaceContract.get(address=place_items.parameter.chunk_key.place_key.fa2)
    place = await models.PlaceToken.get(token_id=int(place_items.parameter.chunk_key.place_key.id), contract=place_contract)

    chunk = find_chunk(place_items.storage.chunks, place_items.parameter.chunk_key)
    chunk_next_id = int(chunk.value.next_id)

    chunk_items_counter = sum(len(x) for x in place_items.parameter.place_item_map.values())
    for (send_to_place, fa2_map) in place_items.parameter.place_item_map.items():
        send_to_place_bool = False if send_to_place.lower() == "false" else True

        for (fa2, item_list) in fa2_map.items():
            item_contract = await models.ItemContract.get(address=fa2)
            for i in item_list:
                # subtract decresing counter from next_id to get item_id
                item_id = chunk_next_id - chunk_items_counter

                item_token = await models.ItemToken.get(token_id=int(i.item.token_id), contract=item_contract)

                await models.WorldItemPlacement.create(
                    place=place,
                    issuer=(None if send_to_place_bool else issuer),
                    item_id=item_id,
                    chunk=place_items.parameter.chunk_key.chunk_id,
                    item_token=item_token,
                    amount=i.item.amount,
                    rate=i.item.rate,
                    data=i.item.data,
                    level=place_items.data.level,
                    timestamp=place_items.data.timestamp)

                chunk_items_counter -= 1
