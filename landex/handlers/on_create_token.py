import logging
from dipdup.models import Origination, OperationData
from dipdup.config import ContractConfig
from dipdup.context import HandlerContext
from dipdup.exceptions import ContractAlreadyExistsError

import landex.utils as utils
#from landex.types.tezlandFactory.storage import TezlandFactoryStorage

_logger = logging.getLogger(__name__)


async def on_create_token(
    ctx: HandlerContext,
    origination: OperationData #Origination[TezlandFactoryStorage].data
) -> None:
    contract_address = origination.originated_contract_address
    contract_name = f'itemCollection{contract_address[-12:]}'

    # Add the contract.
    await utils.addContract(ctx,
        contract_address,
        owner=origination.initiator_address,
        level=origination.level,
        timestamp=origination.timestamp)

    await ctx.add_contract(contract_name, contract_address, typename='tezlandItemsCollection')

    _logger.info(f'Adding index for item collection {contract_name}')
    await ctx.add_index(contract_name, 'tezland_item_collection_template',
        {'contract': contract_name}, first_level=origination.level)
