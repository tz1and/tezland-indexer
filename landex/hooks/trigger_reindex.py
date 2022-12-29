from dipdup.context import HookContext, ReindexingReason

async def trigger_reindex(
    ctx: HookContext
) -> None:
    # NOTE: doesn't really work. who knows why. we'll see in prod.
    await ctx.reindex(ReindexingReason.manual)
