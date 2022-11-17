#from datetime import datetime
from enum import Enum, unique
from tortoise import Model, fields


# TODO: have an FA2 table, maybe, for references to contracts, fa2.
# TODO: whitelist for different place types.


# TODO: probably shouldn't be called holder?
# maybe Account or TezosAccount or TezlandAccount?
class Holder(Model):
    address = fields.CharField(max_length=36, pk=True)
    balance = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    volume = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    tx_count = fields.BigIntField(default=0)
    last_seen = fields.DatetimeField(null=True)

# Levelled base with transient id
class LevelledBaseTransient(Model):
    # Call the pk transient_id, to let there be no doubt what it is.
    transient_id = fields.BigIntField(pk=True)

    level = fields.BigIntField(null=False)
    timestamp = fields.DatetimeField(null=False)

    class Meta:
        abstract = True

# Levelled base where id == onchain id
class LevelledBase(Model):
    id = fields.BigIntField(pk=True)

    level = fields.BigIntField(null=False)
    timestamp = fields.DatetimeField(null=False)

    class Meta:
        abstract = True

# Tokens
@unique
class MetadataStatus(Enum):
    New = 0
    Valid = 1
    Failed = 2
    Invalid = 3

class BaseToken(LevelledBaseTransient):
    token_id = fields.BigIntField(null=False, index=True)
    contract = fields.CharField(max_length=36, null=False, index=True)

    metadata_uri = fields.TextField(null=False)
    metadata_status = fields.BigIntField(default=int(MetadataStatus.New.value))

    class Meta:
        abstract = True
        unique_together = ('token_id', 'contract')

class ItemToken(BaseToken):
    minter = fields.ForeignKeyField('models.Holder', 'item_tokens', null=False, index=True)
    royalties = fields.SmallIntField(default=0)
    supply = fields.BigIntField(default=0)

    metadata = fields.ForeignKeyField('models.ItemTokenMetadata', 'item_token', index=True, null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = 'item_token'

class PlaceToken(BaseToken):
    minter = fields.ForeignKeyField('models.Holder', 'place_tokens', null=False, index=True)

    metadata = fields.ForeignKeyField('models.PlaceTokenMetadata', 'place_token', index=True, null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = 'place_token'

# Metadata
class BaseMetadata(LevelledBaseTransient):
    # TODO: probably not needed if we always search metadata by token.
    token_id = fields.BigIntField(null=False, index=True)
    contract = fields.CharField(max_length=36, null=False, index=True)

    name = fields.TextField(default='')
    description = fields.TextField(default='')

    class Meta:
        abstract = True
        unique_together = ('token_id', 'contract')

class ItemTokenMetadata(BaseMetadata):
    artifact_uri = fields.TextField(null=False)
    thumbnail_uri = fields.TextField(null=True)
    display_uri = fields.TextField(null=True)

    mime_type = fields.TextField(null=False)
    file_size = fields.BigIntField(null=False)
    base_scale = fields.FloatField(null=False)
    polygon_count = fields.BigIntField(null=False)

    class Meta:
        table = 'item_token_metadata'

class PlaceTokenMetadata(BaseMetadata):
    place_type = fields.TextField(null=False)
    center_coordinates = fields.TextField(null=False)
    border_coordinates = fields.TextField(null=False)
    build_height = fields.FloatField(null=False)
    grid_hash = fields.TextField(null=False)

    class Meta:
        table = 'place_token_metadata'

# Token holders
class ItemTokenHolder(Model):
    holder = fields.ForeignKeyField('models.Holder', 'holders_item_token', null=False, index=True)
    # NOTE: this will result in a field tokenId, which is the transient id, not the onchain id...
    # Unfortunatly can't change the foreign key name.
    token = fields.ForeignKeyField('models.ItemToken', 'item_token_holders', null=False, index=True)
    quantity = fields.BigIntField(default=0)

    class Meta:
        table = 'item_token_holder'

class PlaceTokenHolder(Model):
    holder = fields.ForeignKeyField('models.Holder', 'holders_place_token', null=False, index=True)
    # NOTE: this will result in a field tokenId, which is the transient id, not the onchain id...
    # Unfortunatly can't change the foreign key name.
    token = fields.ForeignKeyField('models.PlaceToken', 'place_token_holders', null=False, index=True)

    class Meta:
        table = 'place_token_holder'

# World
class WorldItemPlacement(LevelledBaseTransient):
    place = fields.ForeignKeyField('models.PlaceToken', 'world_item_placements', null=False, index=True)
    chunk = fields.BigIntField(null=False)
    issuer = fields.ForeignKeyField('models.Holder', 'item_token_placements', null=False, index=True)
    item_token = fields.ForeignKeyField('models.ItemToken', 'item_token_placements', null=False, index=True)

    item_id = fields.BigIntField(null=False)
    token_amount = fields.BigIntField(null=False)
    mutez_per_token = fields.BigIntField(null=False)
    item_data = fields.TextField(null=False)

    class Meta:
        table = 'world_item_placement'
        unique_together = ('chunk', 'item_id', 'place')

# TODO:
# class WorldFA2ItemPlacement
# class WorldOtherItemPlacement
# Or: handle all of those this the same table (prob preferred)

class ItemCollectionHistory(LevelledBaseTransient):
    place = fields.ForeignKeyField('models.PlaceToken', 'item_collection_histories', null=False, index=True)
    item_token = fields.ForeignKeyField('models.ItemToken', 'collection_histories', null=False, index=True)

    issuer = fields.ForeignKeyField('models.Holder', 'item_collection_histories', null=False, index=True)
    collector = fields.ForeignKeyField('models.Holder', 'collected_items_histories', null=False, index=True)
    
    mutez_per_token = fields.BigIntField(null=False)
    op_hash = fields.CharField(max_length=51, null=False)

    class Meta:
        table = 'item_collection_history'

# TODO:
#class PlaceProps(LevelledBase):
#    place = fields.ForeignKeyField('models.PlaceToken', 'place_props', null=False, index=True)
#
#    class Meta:
#        table = 'place_prop'

# Auctions
class DutchAuction(LevelledBaseTransient):
    token_id = fields.BigIntField(index=True)
    owner = fields.ForeignKeyField('models.Holder', 'created_dutch_auctions', null=False, index=True)
    start_time = fields.DatetimeField(null=False)
    end_time = fields.DatetimeField(null=False)
    start_price = fields.BigIntField(null=False)
    end_price = fields.BigIntField(null=False)
    fa2 = fields.CharField(max_length=36)

    is_primary = fields.BooleanField(default=False)
    finished = fields.BooleanField(default=False)
    finishing_bid = fields.BigIntField(null=True)
    bid_op_hash = fields.CharField(max_length=51, null=True)

    class Meta:
        table = 'dutch_auction'
        unique_together = ('token_id', 'fa2', 'owner')

# Whitelist
class DutchAuctionWhitelist(Model):
    address = fields.CharField(max_length=36, pk=True)
    current_status = fields.BooleanField(default=False)
    added_count = fields.IntField(default=0)
    removed_count = fields.IntField(default=0)
    used_count = fields.IntField(default=0)

    #level = fields.BigIntField(default=0)
    #timestamp = fields.DatetimeField(null=False)

    class Meta:
        table = 'dutch_auction_whitelist'

# Tags
class Tag(LevelledBaseTransient):
    name = fields.CharField(max_length=255, null=False, unique=True, index=True)

    class Meta:
        table = 'tag'

class ItemTagMap(LevelledBaseTransient):
    item_metadata = fields.ForeignKeyField('models.ItemTokenMetadata', 'tag_map', null=False, index=True, on_delete=fields.CASCADE)
    tag = fields.ForeignKeyField('models.Tag', 'tag_map', null=False, index=True)

    class Meta:
        table = 'item_tag_map'