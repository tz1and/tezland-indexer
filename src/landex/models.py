#from datetime import datetime
from tortoise import Model, fields


# TODO: probably shouldn't be called holder?
# maybe Account or TezosAccount or TezlandAccount?
class Holder(Model):
    address = fields.CharField(max_length=36, pk=True)
    balance = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    volume = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    tx_count = fields.BigIntField(default=0)
    last_seen = fields.DatetimeField(null=True)

class ItemToken(Model):
    id = fields.BigIntField(pk=True)
    minter = fields.ForeignKeyField('models.Holder', 'itemtokens', index=True, null=True)
    name = fields.TextField(default='')
    description = fields.TextField(default='')
    artifact_uri = fields.TextField(default='')
    thumbnail_uri = fields.TextField(default='')
    metadata = fields.TextField(default='')
    mime = fields.TextField(default='')
    royalties = fields.SmallIntField(default=0)
    supply = fields.BigIntField(default=0)

    level = fields.BigIntField(default=0)
    timestamp = fields.DatetimeField(null=False)

class PlaceToken(Model):
    id = fields.BigIntField(pk=True)
    minter = fields.ForeignKeyField('models.Holder', 'placetokens', index=True, null=True)
    name = fields.TextField(default='')
    description = fields.TextField(default='')
    thumbnail_uri = fields.TextField(default='')
    metadata = fields.TextField(default='')

    # TODO: add center coords and the other one

    level = fields.BigIntField(default=0)
    timestamp = fields.DatetimeField(null=False)

class ItemTokenHolder(Model):
    holder = fields.ForeignKeyField('models.Holder', 'holders_item_token', null=False, index=True)
    token = fields.ForeignKeyField('models.ItemToken', 'item_token_holders', null=False, index=True)
    quantity = fields.BigIntField(default=0)

    class Meta:
        table = 'item_token_holder'

class PlaceTokenHolder(Model):
    holder = fields.ForeignKeyField('models.Holder', 'holders_place_token', null=False, index=True)
    token = fields.ForeignKeyField('models.PlaceToken', 'place_token_holders', null=False, index=True)

    class Meta:
        table = 'place_token_holder'

class DutchAuction(Model):
    id = fields.BigIntField(pk=True)
    token_id = fields.BigIntField(index=True)
    owner = fields.ForeignKeyField('models.Holder', 'created_dutch_auctions', index=True)
    start_time = fields.DatetimeField(null=False)
    end_time = fields.DatetimeField(null=False)
    start_price = fields.BigIntField(null=False)
    end_price = fields.BigIntField(null=False)

    level = fields.BigIntField(default=0)
    timestamp = fields.DatetimeField(null=False)

    class Meta:
        table = 'dutch_auction'
