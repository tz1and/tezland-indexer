import logging

from dipdup.context import HookContext

import landex.backups as backups
import landex.utils as utils

_logger = logging.getLogger(__name__)


async def on_reindex(
    ctx: HookContext,
) -> None:
    try:
        await backups.restore(ctx)
    except Exception as e:
        _logger.info(f'db restore failed: {e}')
        _logger.info(f'Reindexing...')

        await ctx.execute_sql('on_reindex')

        head_block = await ctx.get_tzkt_datasource("tzkt_mainnet").get_head_block()

        default_tokens = [
            # Place tokens
            "tezlandPlaces",
            "tezlandPlacesV2",
            "tezlandInteriors",
            # Item tokens
            "tezlandItems",
            "tezlandItemsV2"
        ]

        for contract in default_tokens:
            await utils.addContract(ctx,
                ctx.config.contracts.get(contract).address,
                None, head_block.level, head_block.timestamp)
