from typing import Optional, get_args
from decimal import Decimal

from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandDutchAuctions.parameter.manage_whitelist import ManageWhitelistParameter, ManageWhitelistParameterItem, ManageWhitelistParameterItem1
from landex.types.tezlandDutchAuctions.storage import TezlandDutchAuctionsStorage


async def on_manage_wl(
    ctx: HandlerContext,
    manage_whitelist: Transaction[ManageWhitelistParameter, TezlandDutchAuctionsStorage],
) -> None:
    for manage_batch_item in manage_whitelist.parameter.__root__:
        if type(manage_batch_item) is ManageWhitelistParameterItem:
            for add_item in manage_batch_item.whitelist_add:
                wl, _ = await models.DutchAuctionWhitelist.get_or_create(address=add_item)
                if wl.current_status == False:
                    wl.current_status = True
                    wl.added_count += 1
                    await wl.save()

        elif type(manage_batch_item) is ManageWhitelistParameterItem1:
            for remove_item in manage_batch_item.whitelist_remove:
                wl = await models.DutchAuctionWhitelist.get_or_none(address=remove_item)
                if wl and wl.current_status == True:
                    wl.current_status = False
                    wl.removed_count += 1
                    await wl.save()
