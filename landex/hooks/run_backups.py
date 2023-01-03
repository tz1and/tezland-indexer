import logging

from dipdup.context import HookContext

import landex.backups as backups

_logger = logging.getLogger(__name__)

async def run_backups(
    ctx: HookContext,
) -> None:
    try:
        await backups.backup(ctx)

        # Probably shouldn't delete old backups if backups failed.
        await backups.delete_old_backups(ctx)
    except Exception as e:
        _logger.warning(f'Database backup failed: {e}')
