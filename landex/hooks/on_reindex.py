
from dipdup.context import HookContext

import landex.backups as backups
import landex.models as models

async def on_reindex(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_reindex')

    # pretty sure we want to delete the backups on reindex.
    backups.delete_old_backups(0)

    await models.PlaceContract.create(address=ctx.config.contracts.get("tezlandPlaces").address, level=0, timestamp=0)
    await models.PlaceContract.create(address=ctx.config.contracts.get("tezlandPlacesV2").address, level=0, timestamp=0)
    await models.PlaceContract.create(address=ctx.config.contracts.get("tezlandInteriors").address, level=0, timestamp=0)

    await models.ItemContract.create(address=ctx.config.contracts.get("tezlandItems").address, level=0, timestamp=0)
