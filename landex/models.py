#from datetime import datetime
from enum import Enum, unique
#from tortoise import Model, fields
from tortoise import fields
from dipdup.models import Model


@unique
class MetadataStatus(Enum):
    New = 0
    Valid = 1
    Failed = 2
    Invalid = 3


# TODO: probably shouldn't be called holder?
# maybe Account or TezosAccount or TezlandAccount?
class Holder(Model):
    address = fields.CharField(max_length=36, pk=True)
    balance = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    volume = fields.DecimalField(decimal_places=8, max_digits=20, default=0)
    tx_count = fields.BigIntField(default=0)
    last_seen = fields.DatetimeField(null=True)

    class Meta:
        table = 'holder'


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


# Levelled base where no pk is provided
class LevelledBaseNoPk(Model):
    level = fields.BigIntField(null=False)
    timestamp = fields.DatetimeField(null=False)

    class Meta:
        abstract = True


# Contracts
class Contract(LevelledBaseNoPk):
    address = fields.CharField(max_length=36, pk=True)
    owner = fields.ForeignKeyField('models.Holder', 'collections', null=True, index=True)

    metadata_uri = fields.TextField(null=False)
    metadata_status = fields.BigIntField(default=int(MetadataStatus.New.value))
    metadata = fields.OneToOneField('models.ContractMetadata', 'contract', null=True)

    class Meta:
        table = 'token_contract'


# Tokens
class BaseToken(LevelledBaseTransient):
    token_id = fields.BigIntField(null=False, index=True)

    metadata_uri = fields.TextField(null=False)
    metadata_status = fields.BigIntField(default=int(MetadataStatus.New.value))

    class Meta:
        abstract = True


class ItemToken(BaseToken):
    contract = fields.ForeignKeyField('models.Contract', 'item_tokens', null=False, index=True)
    minter = fields.ForeignKeyField('models.Holder', 'item_tokens', null=False, index=True)
    royalties = fields.SmallIntField(default=0)
    supply = fields.BigIntField(default=0)

    metadata = fields.OneToOneField('models.ItemTokenMetadata', 'token', null=True)

    class Meta:
        table = 'item_token'
        unique_together = ('token_id', 'contract')


class PlaceToken(BaseToken):
    contract = fields.ForeignKeyField('models.Contract', 'place_tokens', null=False, index=True)
    minter = fields.ForeignKeyField('models.Holder', 'place_tokens', null=False, index=True)

    metadata = fields.OneToOneField('models.PlaceTokenMetadata', 'token', null=True)

    class Meta:
        table = 'place_token'
        unique_together = ('token_id', 'contract')


# Metadata
class IpfsMetadataCache(Model):
    metadata_uri = fields.CharField(max_length=255, pk=True)
    metadata_json = fields.JSONField()

    class Meta:
        table = 'ipfs_metadata_cache'


class BaseMetadata(LevelledBaseTransient):
    name = fields.TextField(default='')
    description = fields.TextField(default='')

    class Meta:
        abstract = True


class BaseTokenMetadata(BaseMetadata):
    contract = fields.CharField(max_length=36, index=True)
    token_id = fields.BigIntField(index=True)

    class Meta:
        abstract = True
        unique_together = ('token_id', 'contract')


class ItemTokenMetadata(BaseTokenMetadata):
    artifact_uri = fields.TextField(null=False)
    thumbnail_uri = fields.TextField(null=True)
    display_uri = fields.TextField(null=True)

    mime_type = fields.TextField(null=False)
    file_size = fields.BigIntField(null=False)
    base_scale = fields.FloatField(null=False)
    polygon_count = fields.BigIntField(null=False)

    width = fields.IntField(null=True)
    height = fields.IntField(null=True)
    image_frame_json = fields.JSONField(null=True)

    class Meta:
        table = 'item_token_metadata'


class PlaceTokenMetadata(BaseTokenMetadata):
    place_type = fields.TextField(null=False)
    center_coordinates = fields.TextField(null=False)
    border_coordinates = fields.TextField(null=False)
    build_height = fields.FloatField(null=False)
    grid_hash = fields.TextField(null=False)

    class Meta:
        table = 'place_token_metadata'


class ContractMetadata(BaseMetadata):
    address = fields.CharField(max_length=36, index=True)

    user_description = fields.TextField(null=True)

    class Meta:
        table = 'contract_metadata'


# Token holders
class ItemTokenHolder(Model):
    holder = fields.ForeignKeyField('models.Holder', 'holders_item_token', null=False, index=True)
    # NOTE: use source_field so id field generated is not token_id. Which would be ambiguous.
    token = fields.ForeignKeyField('models.ItemToken', 'item_token_holders', null=False, index=True, source_field="token_transient_id")
    quantity = fields.BigIntField(default=0)

    class Meta:
        table = 'item_token_holder'


class PlaceTokenHolder(Model):
    holder = fields.ForeignKeyField('models.Holder', 'holders_place_token', null=False, index=True)
    # NOTE: use source_field so id field generated is not token_id. Which would be ambiguous.
    token = fields.ForeignKeyField('models.PlaceToken', 'place_token_holders', null=False, index=True, source_field="token_transient_id")

    class Meta:
        table = 'place_token_holder'


# World
class WorldItemPlacement(LevelledBaseTransient):
    place = fields.ForeignKeyField('models.PlaceToken', 'world_item_placements', null=False, index=True)
    chunk = fields.BigIntField(null=False)
    issuer = fields.ForeignKeyField('models.Holder', 'item_token_placements', null=True, index=True)
    item_token = fields.ForeignKeyField('models.ItemToken', 'item_token_placements', null=False, index=True)

    item_id = fields.BigIntField(null=False)
    amount = fields.BigIntField(null=False)
    rate = fields.BigIntField(null=False)
    data = fields.TextField(null=False)

    class Meta:
        table = 'world_item_placement'
        unique_together = ('chunk', 'item_id', 'place')

class PlacePermissions(LevelledBaseTransient):
    place = fields.ForeignKeyField('models.PlaceToken', 'permissions', null=False, index=True)
    owner = fields.ForeignKeyField('models.Holder', 'given_permissions', null=False, index=True)
    permittee = fields.ForeignKeyField('models.Holder', 'held_permissions', null=False, index=True)
    premissions = fields.SmallIntField(default=0)

    class Meta:
        table = 'place_permissions'
        unique_together = ('place_id', 'owner_id', 'permittee_id')


# TODO:
# class WorldFA2ItemPlacement
# class WorldOtherItemPlacement
# Or: handle all of those this the same table (prob preferred)

class ItemCollectionHistory(LevelledBaseTransient):
    place = fields.ForeignKeyField('models.PlaceToken', 'item_collection_histories', null=False, index=True)
    item_token = fields.ForeignKeyField('models.ItemToken', 'collection_histories', null=False, index=True)

    issuer = fields.ForeignKeyField('models.Holder', 'item_collection_histories', null=True, index=True)
    collector = fields.ForeignKeyField('models.Holder', 'collected_items_histories', null=False, index=True)
    
    rate = fields.BigIntField(null=False)
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

    is_primary = fields.BooleanField(null=False)
    finished = fields.BooleanField(default=False)
    finishing_bid = fields.BigIntField(null=True)
    bid_op_hash = fields.CharField(max_length=51, null=True)

    class Meta:
        table = 'dutch_auction'
        # Note: auctions should not be unique on these, because finished auctions
        # are kept around for history.
        # NOTE: should maybe put them into another table: DutchAuctionFinished
        # and keep the unique constraint?
        #unique_together = ('token_id', 'fa2', 'owner')


# Whitelists
class DutchAuctionWhitelistV1(Model):
    address = fields.CharField(max_length=36, pk=True)
    current_status = fields.BooleanField(default=False)
    added_count = fields.IntField(default=0)
    removed_count = fields.IntField(default=0)
    used_count = fields.IntField(default=0)

    class Meta:
        table = 'dutch_auction_whitelist_v1'

class DutchAuctionWhitelist(Model):
    id = fields.BigIntField(pk=True)
    fa2 = fields.CharField(max_length=36, index=True)
    address = fields.CharField(max_length=36, index=True)
    current_status = fields.BooleanField(default=False)
    added_count = fields.IntField(default=0)
    removed_count = fields.IntField(default=0)
    used_count = fields.IntField(default=0)

    class Meta:
        table = 'dutch_auction_whitelist'
        unique_together = ('fa2', 'address')


# Tags
class Tag(LevelledBaseTransient):
    name = fields.CharField(max_length=255, null=False, unique=True, index=True)

    class Meta:
        table = 'tag'


class ItemTagMap(LevelledBaseTransient):
    item_metadata = fields.ForeignKeyField('models.ItemTokenMetadata', 'tags', null=False, index=True, on_delete=fields.CASCADE)
    tag = fields.ForeignKeyField('models.Tag', 'items', null=False, index=True)

    class Meta:
        table = 'item_tag_map'


class ContractTagMap(LevelledBaseTransient):
    contract_metadata = fields.ForeignKeyField('models.ContractMetadata', 'tags', null=False, index=True, on_delete=fields.CASCADE)
    tag = fields.ForeignKeyField('models.Tag', 'contracts', null=False, index=True)

    class Meta:
        table = 'contract_tag_map'