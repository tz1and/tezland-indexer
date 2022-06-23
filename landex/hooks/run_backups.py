import logging
from typing import Union
from contextlib import AsyncExitStack

from dipdup.context import HookContext
from dipdup.enums import MessageType
from dipdup.config import PostgresDatabaseConfig, SqliteDatabaseConfig

import landex.backups as backups

_logger = logging.getLogger(__name__)

async def run_backups(
    ctx: HookContext,
) -> None:
    database_config: Union[SqliteDatabaseConfig, PostgresDatabaseConfig] = ctx.config.database

    if database_config.kind != "postgres":
        _logger.info(f'Not postgres database, skipping backup')
        return

    level = ctx.get_tzkt_datasource("tzkt_mainnet").get_channel_level(MessageType.head)

    backups.backup(level, database_config)

    backups.delete_old_backups()
