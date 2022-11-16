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


async def on_world_place_items(
    ctx: HandlerContext,
    place_items: Transaction[PlaceItemsParameter, TezlandWorldV2Storage],
) -> None:
    issuer = await models.Holder.get(address=place_items.data.sender_address)
    place = await models.PlaceToken.get(token_id=int(place_items.parameter.chunk_key.place_key.id), contract=place_items.parameter.chunk_key.place_key.fa2)

    chunk = find_chunk(place_items.storage.chunks, place_items.parameter.chunk_key)
    chunk_next_id = int(chunk.value.next_id)

    chunk_items_counter = sum(len(x) for x in place_items.parameter.place_item_map.values())
    for (fa2, item_list) in place_items.parameter.place_item_map.items():
        for i in item_list:
            # subtract decresing counter from next_id to get item_id
            item_id = chunk_next_id - chunk_items_counter

            item_token = await models.ItemToken.get(token_id=int(i.item.token_id), contract=fa2)

            await models.WorldItemPlacement.create(
                place=place,
                issuer=(None if place_items.parameter.send_to_place else issuer),
                item_id=item_id,
                chunk=place_items.parameter.chunk_key.chunk_id,
                item_token=item_token,
                token_amount=i.item.token_amount,
                mutez_per_token=i.item.mutez_per_token,
                item_data=i.item.item_data,
                level=place_items.data.level,
                timestamp=place_items.data.timestamp)

            chunk_items_counter -= 1
