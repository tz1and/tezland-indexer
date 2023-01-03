
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

    # Let's say back if it's older than 100 blocks.
    try:
        await backups.backup_if_older_than(ctx, 100)
    except Exception as e:
        _logger.warning(f'Database backup failed: {e}')
