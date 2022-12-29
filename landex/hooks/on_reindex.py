import logging

from dipdup.context import HookContext

import landex.backups as backups
import landex.utils as utils

_logger = logging.getLogger(__name__)


async def on_reindex(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_reindex')

    try:
        await backups.restore(ctx)
    except Exception as e:
        _logger.info(f'db restore failed: {e}')
        _logger.info(f'Reindexing...')

        await utils.addContract(ctx, ctx.config.contracts.get("tezlandPlaces").address)
        await utils.addContract(ctx, ctx.config.contracts.get("tezlandPlacesV2").address)
        await utils.addContract(ctx, ctx.config.contracts.get("tezlandInteriors").address)

        await utils.addContract(ctx, ctx.config.contracts.get("tezlandItems").address)
        await utils.addContract(ctx, ctx.config.contracts.get("tezlandItemsV2").address)
