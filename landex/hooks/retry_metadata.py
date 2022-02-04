import asyncio
import threading

from dipdup.context import HookContext

from landex.models import PlaceToken, ItemToken
from landex.metadata import get_place_metadata, get_item_metadata

#from multiprocessing.pool import Pool, ThreadPool
#from landex.hooks.retry_metadata_thread import threadFunc

async def fetchMetadata(ctx: HookContext):
    ipfs = ctx.get_ipfs_datasource("local_ipfs")

    while True:
        async for token in PlaceToken.filter(metadata_fetched=False):
            await get_place_metadata(ipfs, token)

        async for token in ItemToken.filter(metadata_fetched=False):
            await get_item_metadata(ipfs, token)
        
        await asyncio.sleep(1)

async def retry_metadata(
    ctx: HookContext,
) -> None:
    print(f'retry_metadata: {threading.get_ident()}')

    await fetchMetadata(ctx)
    #thread_result = await asyncio.gather(ctx.pool_map(Pool, threadFunc, [ctx.config])) #_async(ctx), 
    #print(thread_result)
