import json, logging, aiohttp
from pathlib import Path
from os import environ as env

import landex.models as models
from landex.utils import clean_null_bytes, http_request

IPFS_GATEWAY = env.get('IPFS_GATEWAY', 'http://localhost:8080/ipfs')
TOKEN_METADATA_DIR = env.get('TOKEN_METADATA_DIR', './tz1aND_metadata')
ITEM_METADTA_PATH = f'{TOKEN_METADATA_DIR}/items'
PLACE_METADTA_PATH = f'{TOKEN_METADATA_DIR}/places'

_logger = logging.getLogger(__name__)


async def get_place_metadata(token):
    metadata = await fetch_metadata(token, PLACE_METADTA_PATH)
    if metadata.get('__stop_trying'):
        token.metadata_fetched = True
        await token.save()
    elif metadata != {}:
        token.name = metadata.get('name', '')
        token.description = metadata.get('description', '')
        token.thumbnail_uri = metadata.get('thumbnailUri', '')
        token.center_coordinates = metadata.get('centerCoordinates', '')
        token.border_coordinates = metadata.get('borderCoordinates', '')
        token.place_type = metadata.get('placeType', '')
        token.metadata_fetched = True
        await token.save()


async def get_item_metadata(token):
    metadata = await fetch_metadata(token, ITEM_METADTA_PATH)
    if metadata.get('__stop_trying'):
        token.metadata_fetched = True
        await token.save()
    elif metadata != {}:
        token.name = metadata.get('name', '')
        token.description = metadata.get('description', '')
        token.artifact_uri = metadata.get('artifactUri', '')
        token.thumbnail_uri = metadata.get('thumbnailUri', '')
        token.mime_type = get_mime_type(metadata)
        token.metadata_fetched = True
        await token.save()


# fetches metadata from disk or from external
async def fetch_metadata(token, base_path: str):
    num_retries = 10
    failed_attempt = 0
    cache_path = file_path(token.id, base_path)
    # try to read the metadata from cache
    # if it doesn't exist or has previously failed,
    # try to fetch it again. up to num_retries.
    try:
        with open(cache_path, 'r') as json_file:
            metadata = json.load(json_file)
            failed_attempt = metadata.get('__failed_attempt')
            if failed_attempt and failed_attempt > num_retries:
                _logger.info(f'Too many attempts to download metadata for {token.id}')
                return { '__stop_trying': True }
            if not failed_attempt:
                _logger.info(f'Got metadata for {token.id} from cache')
                return metadata
    except Exception:
        pass

    # try to fetch the metadata from ipfs.
    data = await fetch_metadata_ipfs(token, cache_path, failed_attempt)
    if data != {}:
        _logger.info(f'Got metadata for {token.id} from IPFS')

    return data


# returns path of the ondisk cache of a tokens metadata
def file_path(token_id: str, base_path: str):
    token_id_int = int(token_id)
    lvl2 = token_id_int % 10
    lvl1 = int((token_id_int % 100 - lvl2) / 10)
    dir = f'{base_path}/{lvl1}/{lvl2}'
    Path(dir).mkdir(parents=True, exist_ok=True)
    return f'{dir}/{token_id}.json'


# download metadata from ipfs.
# TODO: change __failed_attempt stuff. store it in the db maybe?
async def fetch_metadata_ipfs(token, cache_path, failed_attempt):
    addr = token.metadata.replace('ipfs://', '')
    try:
        # try dl the file from ipfs
        session = aiohttp.ClientSession()
        matadata = await http_request(session, 'get', url=f'{IPFS_GATEWAY}/{addr}', timeout=10)
        await session.close()

        # if we succeed, normalise it and write it.
        if matadata and not isinstance(matadata, list):
            with open(cache_path, 'w') as write_file:
                json.dump(matadata, write_file) # normalise_metadata?
            return matadata
    except Exception:
        # if we got nothing, write a failed attempt.
        with open(cache_path, 'w') as write_file:
            json.dump({'__failed_attempt': failed_attempt + 1}, write_file)
        await session.close()
    return {}


# normalise the metadata strings
# TODO: do I really need to do this? it's json data
#def normalise_metadata(metadata):
#    normalised = {}
#    for key in metadata:
#        value = metadata[key]
#        if isinstance(value, str):
#            normalised[key] = clean_null_bytes(value)
#        else:
#            normalised[key] = value
#    return normalised


def get_mime_type(metadata):
    if ('formats' in metadata) and metadata['formats'] and ('mimeType' in metadata['formats'][0]):
        return metadata['formats'][0]['mimeType']
    return ''