
from dipdup.context import HookContext

import landex.backups as backups
import landex.utils as utils

async def on_reindex(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_reindex')

    # pretty sure we want to delete the backups on reindex.
    backups.delete_old_backups(0)

    await utils.addContract(ctx, ctx.config.contracts.get("tezlandPlaces").address)
    await utils.addContract(ctx, ctx.config.contracts.get("tezlandPlacesV2").address)
    await utils.addContract(ctx, ctx.config.contracts.get("tezlandInteriors").address)

    await utils.addContract(ctx, ctx.config.contracts.get("tezlandItems").address)
    await utils.addContract(ctx, ctx.config.contracts.get("tezlandItemsV2").address)
