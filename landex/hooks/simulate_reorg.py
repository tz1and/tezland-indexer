import logging

from dipdup.datasources.datasource import Datasource
from dipdup.context import HookContext
from dipdup.enums import MessageType

_logger = logging.getLogger(__name__)

async def simulate_reorg(
    ctx: HookContext
) -> None:
    level = ctx.get_tzkt_datasource("tzkt_mainnet").get_channel_level(MessageType.head)

    await ctx.fire_hook("on_rollback", wait=True, datasource=ctx.get_tzkt_datasource("tzkt_mainnet"), from_level=level, to_level=level-2)
