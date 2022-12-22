
import sys
from dipdup.context import HookContext
from dipdup.datasources.tzkt.datasource import TzktDatasource

import landex.backups as backups
import landex.models as models

async def on_reindex(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_reindex')

    # pretty sure we want to delete the backups on reindex.
    backups.delete_old_backups(0)

    tzkt: TzktDatasource = ctx.get_tzkt_datasource("tzkt_mainnet")

    async def addContract(address: str):
        big_maps = await tzkt.get_contract_big_maps(address)
        metadata_ptr: int = -1
        for big_map in big_maps:
            if (big_map["path"] == "metadata"):
                metadata_ptr = int(big_map["ptr"])
                #print(f"found metadata map at: {metadata_ptr}")
                break

        metadata_uri = "error_no_metadata"
        if metadata_ptr >= 0:
            # TODO: don't specify level, offset, limit! waiting for dipdup fix.
            metadata_map = await tzkt.get_big_map(metadata_ptr, active=True, level=sys.maxsize, offset=0, limit=10)
            
            for item in metadata_map:
                if item["key"] == "":
                    metadata_uri = bytes.fromhex(item["value"]).decode()
                    #print(f"found metadata_uri: {metadata_uri}")
                    break

        await models.Contract.create(address=address, metadata_uri=metadata_uri, level=0, timestamp=0)

    await addContract(ctx.config.contracts.get("tezlandPlaces").address)
    await addContract(ctx.config.contracts.get("tezlandPlacesV2").address)
    await addContract(ctx.config.contracts.get("tezlandInteriors").address)

    await addContract(ctx.config.contracts.get("tezlandItems").address)
    await addContract(ctx.config.contracts.get("tezlandItemsV2").address)
