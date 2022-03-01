import json, logging
from pathlib import Path
from os import environ as env

from dipdup.datasources.ipfs.datasource import IpfsDatasource

import landex.models as models

IPFS_GATEWAY = env.get('IPFS_GATEWAY', 'http://localhost:8080/ipfs')
TOKEN_METADATA_DIR = env.get('TOKEN_METADATA_DIR', './tz1aND_metadata')
ITEM_METADTA_PATH = f'{TOKEN_METADATA_DIR}/items'
PLACE_METADTA_PATH = f'{TOKEN_METADATA_DIR}/places'

_logger = logging.getLogger(__name__)
_logger.info(f'IPFS_GATEWAY={IPFS_GATEWAY}')


async def get_place_metadata(ipfs: IpfsDatasource, token):
    metadata = await fetch_metadata(ipfs, token, PLACE_METADTA_PATH)
    if metadata is None:
        token.metadata_fetched = True
        await token.save()
    elif metadata != {}:
        token.name = metadata.get('name', '')
        token.description = metadata.get('description', '')
        token.thumbnail_uri = metadata.get('thumbnailUri', '')
        token.center_coordinates = metadata.get('centerCoordinates', '')
        token.border_coordinates = metadata.get('borderCoordinates', '')
        token.build_height = metadata.get('buildHeight', 0)
        token.place_type = metadata.get('placeType', '')
        token.metadata_fetched = True
        await token.save()


async def get_item_metadata(ipfs: IpfsDatasource, token):
    metadata = await fetch_metadata(ipfs, token, ITEM_METADTA_PATH)
    if metadata is None:
        token.metadata_fetched = True
        await token.save()
    elif metadata != {}:
        token.name = metadata.get('name', '')
        token.description = metadata.get('description', '')
        token.artifact_uri = metadata.get('artifactUri', '')
        token.thumbnail_uri = metadata.get('thumbnailUri', '')
        token.mime_type = get_mime_type(metadata)
        token.file_size = get_file_size(metadata)
        token.base_scale = metadata.get('baseScale', 1)
        token.metadata_fetched = True
        await token.save()


# fetches metadata from disk or from external
# returns a dict for valid metadata, none for invalid.
async def fetch_metadata(ipfs: IpfsDatasource, token, base_path: str):
    cache_path = file_path(token.id, base_path)
    # try to read the metadata from cache
    # if it previously failed, return.
    try:
        with open(cache_path, 'r') as json_file:
            metadata = json.load(json_file)
            invalid_json = metadata.get('__invalid_json')
            if invalid_json:
                _logger.info(f'Metadata from cache invalid json for: {token.id}')
                return None

            _logger.info(f'Got metadata for {token.id} from cache')
            return metadata
    except Exception:
        pass

    # try to fetch the metadata from ipfs.
    return await fetch_metadata_ipfs(ipfs, token, cache_path)


# download metadata from ipfs.
# TODO: change __invalid_json stuff. store it in the db maybe?
async def fetch_metadata_ipfs(ipfs: IpfsDatasource, token, cache_path):
    addr = token.metadata.replace('ipfs://', '')
    try:
        data = await ipfs.get(addr)
        if isinstance(data, bytes):
            _logger.warning(f'Not a json metadata file: {addr}')
            with open(cache_path, 'w') as write_file:
                json.dump({'__invalid_json': True}, write_file)
            return None
        else:
            _logger.info(f'Got metadata for {token.id} from IPFS')
            with open(cache_path, 'w') as write_file:
                json.dump(data, write_file) # normalise_metadata?
            return data
    except Exception as err:
        _logger.warning(f'Failed to fetch metadata {addr} from ipfs: {err}')
        return None


# returns path of the ondisk cache of a tokens metadata
def file_path(token_id: str, base_path: str):
    token_id_int = int(token_id)
    lvl2 = token_id_int % 10
    lvl1 = int((token_id_int % 100 - lvl2) / 10)
    dir = f'{base_path}/{lvl1}/{lvl2}'
    Path(dir).mkdir(parents=True, exist_ok=True)
    return f'{dir}/{token_id}.json'


def get_mime_type(metadata):
    if ('formats' in metadata) and metadata['formats'] and ('mimeType' in metadata['formats'][0]):
        return metadata['formats'][0]['mimeType']
    return ''

def get_file_size(metadata):
    if ('formats' in metadata) and metadata['formats'] and ('fileSize' in metadata['formats'][0]):
        return metadata['formats'][0]['fileSize']
    return 34359738368 # if not set, we assume very large. Tough luck.