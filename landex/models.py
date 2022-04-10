#from datetime import datetime
from tortoise import Model, fields


# TODO: probably shouldn't be called holder?
# maybe Account or TezosAccount or TezlandAccount?
# TODO: holder should be by id, probably, we can union the address in queries.
class Holder(Model):
    address = fields.CharField(max_length=36, pk=True)
    balance = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    volume = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    tx_count = fields.BigIntField(default=0)
    last_seen = fields.DatetimeField(null=True)

class ItemToken(Model):
    id = fields.BigIntField(pk=True)
    minter = fields.ForeignKeyField('models.Holder', 'itemtokens', index=True, null=True)
    royalties = fields.SmallIntField(default=0)
    supply = fields.BigIntField(default=0)

    name = fields.TextField(default='')
    description = fields.TextField(default='')
    artifact_uri = fields.TextField(default='')
    thumbnail_uri = fields.TextField(default='')
    mime_type = fields.TextField(default='')
    file_size = fields.BigIntField(default=34359738368) # Assume very large if not set.
    base_scale = fields.FloatField(default=1) # baseScale default is 1
    polygon_count = fields.FloatField(default=0) # polygonCount default is 0
    metadata = fields.TextField(default='')
    metadata_fetched = fields.BooleanField(default=False)

    level = fields.BigIntField(default=0)
    timestamp = fields.DatetimeField(null=False)

class PlaceToken(Model):
    id = fields.BigIntField(pk=True)
    minter = fields.ForeignKeyField('models.Holder', 'placetokens', index=True, null=True)

    name = fields.TextField(default='')
    description = fields.TextField(default='')
    thumbnail_uri = fields.TextField(default='')
    center_coordinates = fields.TextField(default='')
    border_coordinates = fields.TextField(default='')
    build_height = fields.FloatField(default=0)
    place_type = fields.TextField(default='')
    metadata = fields.TextField(default='')
    metadata_fetched = fields.BooleanField(default=False)

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
    fa2 = fields.CharField(max_length=36)

    finished = fields.BooleanField(default=False)
    finishing_bid = fields.BigIntField(null=True)

    level = fields.BigIntField(default=0)
    timestamp = fields.DatetimeField(null=False)

    class Meta:
        table = 'dutch_auction'

# TODO: have distinct models for Item and Place metadata?