import logging

from dipdup.context import HookContext

async def trigger_reindex(
    ctx: HookContext
) -> None:
    await ctx.reindex('manual')
