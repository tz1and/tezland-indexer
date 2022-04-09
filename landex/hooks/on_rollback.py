import logging
from typing import Union

from dipdup.datasources.datasource import Datasource
from dipdup.context import HookContext
from dipdup.enums import ReindexingReason
from dipdup.config import PostgresDatabaseConfig, SqliteDatabaseConfig

import landex.backups as backups

_logger = logging.getLogger(__name__)

async def on_rollback(
    ctx: HookContext,
    datasource: Datasource,
    from_level: int,
    to_level: int,
) -> None:
    await ctx.execute_sql('on_rollback')

    database_config: Union[SqliteDatabaseConfig, PostgresDatabaseConfig] = ctx.config.database

    # if not a postgres db, reindex.
    if database_config.kind != "postgres":
        _logger.info('Not postgres database, skipping restore')
        await ctx.reindex(ReindexingReason.ROLLBACK)
        return

    available_levels = backups.get_available_backups()

    # if no backups available, reindex
    if not available_levels:
        _logger.info('Not backups available, skipping restore')
        await ctx.reindex(ReindexingReason.ROLLBACK)
        return

    # find the right level. ie the on that's closest to to_level
    chosen_level = 0
    for level in available_levels:
        if level <= to_level and level > chosen_level:
            chosen_level = level

    # try to restore or reindex
    try:
        backups.restore(chosen_level, database_config)
        _logger.info('Restarting dipdup...')
        await ctx.restart()
    except:
        await ctx.reindex(ReindexingReason.ROLLBACK)
