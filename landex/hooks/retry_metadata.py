
from dipdup.context import HookContext

import landex.models as models
from landex.metadata import get_place_metadata, get_item_metadata


# NOTE: isn't used at the moment.
async def retry_metadata(
    ctx: HookContext,
) -> None:
    places = await models.PlaceToken.filter(metadata_fetched=False).all()
    for token in places:
        await get_place_metadata(token)

    items = await models.ItemToken.filter(metadata_fetched=False).all()
    for token in items:
        await get_item_metadata(token)
    
    await ctx.execute_sql('retry_metadata')