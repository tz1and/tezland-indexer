
import logging
from typing import Union
from dipdup.context import HookContext

from dipdup.enums import MessageType
from dipdup.config import PostgresDatabaseConfig, SqliteDatabaseConfig
import landex.backups as backups

_logger = logging.getLogger(__name__)

async def on_synchronized(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_synchronized')

    # TODO: level will almost always be None in on_synchronized.
    return
    level = ctx.get_tzkt_datasource("tzkt_mainnet")._level.get(MessageType.head)

    # If level is None, realtime state hasn't been reached and
    # we wait for the next on_synchronized.
    if not level:
        _logger.info('datasource level is None')
        return

    # do a backup if the last one is too old.
    # let's say 50 blocks.

    database_config: Union[SqliteDatabaseConfig, PostgresDatabaseConfig] = ctx.config.database

    # if not a postgres db, reindex.
    if database_config.kind != "postgres":
        _logger.info('Not postgres database, skipping backup')
        return

    available_levels = backups.get_available_backups()

    # find highest level
    highest_level = 0
    for level in available_levels:
        if level > highest_level:
            highest_level = level

    # if highest level is old, run a backup.
    if level - highest_level > 50:
        backups.backup(level, database_config)
