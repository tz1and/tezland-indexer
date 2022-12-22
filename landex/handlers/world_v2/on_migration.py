from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorldV2.parameter.migration import MigrationParameter
from landex.types.tezlandWorldV2.storage import TezlandWorldV2Storage


async def on_migration(
    ctx: HandlerContext,
    migration: Transaction[MigrationParameter, TezlandWorldV2Storage],
) -> None:
    place_contract = await models.Contract.get(address=migration.parameter.place_key.fa2)
    place = await models.PlaceToken.get(token_id=int(migration.parameter.place_key.id), contract=place_contract)

    chunk_item_limit = int(migration.storage.place_tokens[migration.parameter.place_key.fa2].chunk_item_limit)

    # delete all item placements in old place
    old_place_contract = await models.Contract.get(address=ctx.config.contracts["tezlandPlaces"].address)
    old_place = await models.PlaceToken.get(token_id=int(migration.parameter.place_key.id), contract=old_place_contract)
    await models.WorldItemPlacement.filter(place=old_place).delete()

    item_id = 0
    chunk = 0
    for (issuer_key, issuer_map) in migration.parameter.item_map.items():
        # TODO: get_or_create?
        issuer = await models.Holder.get(address=issuer_key)

        for (fa2, item_list) in issuer_map.items():
            item_contract = await models.Contract.get(address=fa2)
            for i in item_list:
                item_token = await models.ItemToken.get(token_id=int(i.item.token_id), contract=item_contract)

                await models.WorldItemPlacement.create(
                    place=place,
                    issuer=issuer,
                    item_id=item_id,
                    chunk=chunk,
                    item_token=item_token,
                    amount=i.item.amount,
                    rate=i.item.rate,
                    data=i.item.data,
                    level=migration.data.level,
                    timestamp=migration.data.timestamp)

                item_id += 1

                # Move to next chunk if item id counter >= max chunk size.
                if item_id >= chunk_item_limit:
                    item_id = 0
                    chunk += 1
