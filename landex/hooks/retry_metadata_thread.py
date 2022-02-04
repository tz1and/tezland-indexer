import os
import asyncio
import threading
from contextlib import AsyncExitStack

from dipdup.config import DipDupConfig
from dipdup.datasources.ipfs.datasource import IpfsDatasource
from dipdup.utils.database import tortoise_wrapper

from landex.models import PlaceToken, ItemToken
from landex.metadata import get_place_metadata, get_item_metadata

async def fetchMetadata(config: DipDupConfig):
    print(f'fetchMetadata: {threading.get_ident()}')

    url = config.database.connection_string
    models = f'{config.package}.models'

    async with AsyncExitStack() as stack:
        await stack.enter_async_context(tortoise_wrapper(url, models))

        IPFS_GATEWAY = os.environ.get('IPFS_GATEWAY', 'http://localhost:8080/ipfs')

        ipfs = IpfsDatasource(IPFS_GATEWAY, IpfsDatasource._default_http_config)

        while True:
            async for token in PlaceToken.filter(metadata_fetched=False):
                await get_place_metadata(ipfs, token)

            async for token in ItemToken.filter(metadata_fetched=False):
                await get_item_metadata(ipfs, token)
            
            await asyncio.sleep(1)

def threadFunc(config: DipDupConfig):
    print(f'threadFunc: {threading.get_ident()}')
    
    try:
        asyncio.run(fetchMetadata(config))
        return True
    except Exception as err:
        print(f'threadFunc error: {err}')
        return err