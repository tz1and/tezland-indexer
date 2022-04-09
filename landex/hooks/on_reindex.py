
from dipdup.context import HookContext

import landex.backups as backups

async def on_reindex(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_reindex')

    # pretty sure we want to delete the backups on reindex.
    backups.delete_old_backups(0)
