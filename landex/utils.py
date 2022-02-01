# Some utility
import logging

_logger = logging.getLogger(__name__)


def clean_null_bytes(string: str) -> str:
    return string.replace('\x00','')


def fromhex(hexbytes: str) -> str:
    try:
        return clean_null_bytes(bytes.fromhex(hexbytes).decode('utf-8'))
    except Exception as err:
        _logger.error(f'Failed to decode {hexbytes} as utf-8 string: {err}')
    return ''
