import gzip, logging
from io import StringIO
from pathlib import Path
from typing import Union
from sh import pg_dump, ErrorReturnCode

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

    level = ctx.get_tzkt_datasource("tzkt_mainnet")._level.get(MessageType.head)

    if level is None:
        _logger.info(f'No level, skipping backup')
        return

    backups.backup(level, database_config)

    backups.delete_old_backups()
