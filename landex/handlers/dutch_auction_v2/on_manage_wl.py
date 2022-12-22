from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctionsV2.parameter.manage_whitelist import ManageWhitelistParameter
from landex.types.tezlandDutchAuctionsV2.storage import TezlandDutchAuctionsV2Storage


# TODO: v2 wl changes.

async def on_manage_wl(
    ctx: HandlerContext,
    manage_whitelist: Transaction[ManageWhitelistParameter, TezlandDutchAuctionsV2Storage],
) -> None:
    for manage_batch_item in manage_whitelist.parameter.__root__:
        if hasattr(manage_batch_item, "whitelist_add"):
            for add_item in manage_batch_item.whitelist_add:
                wl, _ = await models.DutchAuctionWhitelist.get_or_create(fa2=add_item.fa2, address=add_item.user)
                if wl.current_status == False:
                    wl.current_status = True
                    wl.added_count += 1
                    await wl.save()

        if hasattr(manage_batch_item, "whitelist_remove"):
            for remove_item in manage_batch_item.whitelist_remove:
                wl = await models.DutchAuctionWhitelist.get_or_none(fa2=remove_item.fa2, address=remove_item.user)
                if wl and wl.current_status == True:
                    wl.current_status = False
                    wl.removed_count += 1
                    await wl.save()
