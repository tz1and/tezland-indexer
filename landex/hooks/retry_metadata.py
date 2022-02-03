
from dipdup.context import HookContext

import landex.models as models
from landex.metadata import get_place_metadata, get_item_metadata


# NOTE: isn't used at the moment.
async def retry_metadata(
    ctx: HookContext,
) -> None:
    async for token in models.PlaceToken.filter(metadata_fetched=False):
        await get_place_metadata(token)

    async for token in models.ItemToken.filter(metadata_fetched=False):
        await get_item_metadata(token)
    
    await ctx.execute_sql('retry_metadata')