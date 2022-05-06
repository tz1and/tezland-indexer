import logging
from typing import Union
from contextlib import AsyncExitStack

from dipdup.context import HookContext
from dipdup.enums import MessageType
from dipdup.config import PostgresDatabaseConfig, SqliteDatabaseConfig
from dipdup.hasura import HasuraGateway

import landex.backups as backups

_logger = logging.getLogger(__name__)

async def run_backups(
    ctx: HookContext,
) -> None:
    database_config: Union[SqliteDatabaseConfig, PostgresDatabaseConfig] = ctx.config.database

    if database_config.kind != "postgres":
        _logger.info(f'Not postgres database, skipping backup')
        return

    # update the hasura metadata hash before we backup.
    if ctx.config.hasura:
        async with AsyncExitStack() as stack:
            hasura_gateway = HasuraGateway(ctx.config.package, ctx.config.hasura, database_config)
            await stack.enter_async_context(hasura_gateway)
            await hasura_gateway.update_metadata_hash()

    level = ctx.get_tzkt_datasource("tzkt_mainnet").get_channel_level(MessageType.head)

    backups.backup(level, database_config)

    backups.delete_old_backups()
