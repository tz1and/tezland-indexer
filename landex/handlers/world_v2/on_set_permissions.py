from dipdup.models import Transaction
from dipdup.context import HandlerContext

import landex.models as models

from landex.types.tezlandWorldV2.parameter.set_permissions import SetPermissionsParameter
from landex.types.tezlandWorldV2.storage import TezlandWorldV2Storage


async def on_set_permissions(
    ctx: HandlerContext,
    set_permissions: Transaction[SetPermissionsParameter, TezlandWorldV2Storage],
) -> None:
    for task in set_permissions.parameter.__root__:
        values = task.add if hasattr(task, "add") else task.remove

        place_contract = await models.PlaceContract.get(address=values.place_key.fa2)
        place = await models.PlaceToken.get(token_id=int(values.place_key.id), contract=place_contract)
        owner, _ = await models.Holder.get_or_create(address=values.owner)
        permittee, _ = await models.Holder.get_or_create(address=values.permittee)

        existing_place_permission = await models.PlacePermissions.get_or_none(place=place, owner=owner, permittee=permittee)
        if existing_place_permission: await existing_place_permission.delete()

        if hasattr(task, "add"):
            place_permission = await models.PlacePermissions.create(
                place=place,
                owner=owner,
                permittee=permittee,
                level=set_permissions.data.level,
                timestamp=set_permissions.data.timestamp)
            place_permission.premissions = int(task.add.perm)
            await place_permission.save()