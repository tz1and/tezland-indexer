import logging
from os import remove, path

from dipdup.context import HookContext, ReindexingReason

from landex import backups

_logger = logging.getLogger(__name__)


async def on_restart(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_restart')

    reindex_file = f'{backups.BACKUPS_DIR}/reindex'

    # If the file exists, a reindex is desired.
    if path.exists(reindex_file) and path.isfile(reindex_file):
        _logger.info(f'Manual reindex flagged. Reindexing.....')
        remove(reindex_file)
        await backups.delete_old_backups(ctx, 0)

        await ctx.reindex(ReindexingReason.config_modified)