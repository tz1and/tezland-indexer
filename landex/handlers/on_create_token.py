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

    # Add the contract.
    await utils.addContract(ctx,
        contract_address,
        owner=origination.initiator_address,
        level=origination.level,
        timestamp=origination.timestamp)
