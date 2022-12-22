from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandFA2Fungible.parameter.mint import MintParameter
from landex.types.tezlandFA2Fungible.storage import TezlandFA2FungibleStorage
from landex.utils import fromhex


async def on_item_mint(
    ctx: HandlerContext,
    mint: Transaction[MintParameter, TezlandFA2FungibleStorage],
) -> None:
    mint_counter = len(mint.parameter.__root__)
    for mint_batch_item in mint.parameter.__root__:
        # subtract decresing mint counter from last_token_id to get token_id
        token_id = int(mint.storage.last_token_id) - mint_counter
        holder, _ = await models.Holder.get_or_create(address=mint_batch_item.to_)
        contract = await models.Contract.get(address=mint.data.target_address)
        
        minter = holder

        metadata_uri = ''
        # assume minting new tokens. For now, that's the only thing the minter
        # contract allows.
        if mint_batch_item.token.new.metadata['']:
            metadata_uri = fromhex(mint_batch_item.token.new.metadata[''])

        token = models.ItemToken(
            token_id=token_id,
            contract=contract,
            royalties=mint_batch_item.token.new.royalties.royalties,
            minter=minter,
            metadata_uri=metadata_uri,
            supply=int(mint_batch_item.amount),
            level=mint.data.level,
            timestamp=mint.data.timestamp
        )
        await token.save()

        holding, _ = await models.ItemTokenHolder.get_or_create(
            token=token,
            holder=holder,
            quantity=int(mint_batch_item.amount))
        await holding.save()

        mint_counter -= 1
