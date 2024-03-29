from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandFA2NFT.parameter.mint import MintParameter
from landex.types.tezlandFA2NFT.storage import TezlandFA2NFTStorage
from landex.utils import fromhex


async def on_place_mint(
    ctx: HandlerContext,
    mint: Transaction[MintParameter, TezlandFA2NFTStorage],
) -> None:
    mint_counter = len(mint.parameter.__root__)
    for mint_batch_item in mint.parameter.__root__:
        # subtract decresing mint counter from last_token_id to get token_id
        token_id = int(mint.storage.last_token_id) - mint_counter
        holder, _ = await models.Holder.get_or_create(address=mint_batch_item.to_)
        contract = await models.Contract.get(address=mint.data.target_address)
        
        minter = holder

        metadata_uri = ''
        if mint_batch_item.metadata['']:
            metadata_uri = fromhex(mint_batch_item.metadata[''])

        token = models.PlaceToken(
            token_id=token_id,
            contract=contract,
            minter=minter,
            metadata_uri=metadata_uri,
            level=mint.data.level,
            timestamp=mint.data.timestamp
        )
        await token.save()

        holding, _ = await models.PlaceTokenHolder.get_or_create(token=token, holder=holder)
        await holding.save()

        mint_counter -= 1
