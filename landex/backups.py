import re
import gzip, logging
from io import StringIO
from pathlib import Path
from os import remove, walk
from sh import psql, pg_dump, ErrorReturnCode

from dipdup.config import PostgresDatabaseConfig

from landex.metadata import TOKEN_METADATA_DIR

BACKUPS_PATH = f'{TOKEN_METADATA_DIR}/backups'

_logger = logging.getLogger(__name__)
_logger.info(f'BACKUPS_PATH={BACKUPS_PATH}')

# suppress logging on sh
logging.getLogger("sh").setLevel(logging.WARNING)


def get_backup_file(level: int):
    return f'{BACKUPS_PATH}/backup_{level}.sql'


def backup(level: int, database_config: PostgresDatabaseConfig):
    # create directory
    Path(BACKUPS_PATH).mkdir(parents=True, exist_ok=True)

    backup_file = get_backup_file(level)
    _logger.info(f'Backing up database at level {level} to {backup_file}')

    # TODO: use gzip but causes 'invalid byte sequence for encoding "UTF8": 0x8b' on restore
    with open(backup_file, 'wb') as f:
        try:
            err_buf = StringIO()
            pg_dump('-d', f'postgresql://{database_config.user}:{database_config.password}@{database_config.host}:{database_config.port}/{database_config.database}', '--clean',
                '-n', database_config.schema_name, _out=f, _err=err_buf) #, '-E', 'UTF8'
        except ErrorReturnCode:
            err = err_buf.getvalue()
            _logger.error(f'Database backup failed: {err}')


def restore(level: int, database_config: PostgresDatabaseConfig):
    # try to restore or reindex
    backup_file = get_backup_file(level)
    _logger.info(f'Restoring database level {level} from {backup_file}')

    # TODO: use gzip but causes 'invalid byte sequence for encoding "UTF8": 0x8b' on restore
    with open(backup_file, 'r') as f:
        try:
            err_buf = StringIO()
            psql('-d', f'postgresql://{database_config.user}:{database_config.password}@{database_config.host}:{database_config.port}/{database_config.database}',
                '-n', database_config.schema_name, _in=f, _err=err_buf)
        except ErrorReturnCode:
            err = err_buf.getvalue()
            _logger.error(f'Database restore failed: {err}')
            raise Exception("Failed to restore")


def get_available_backups():
    # get all files in backup dir
    backup_files: list[str] = []
    for (dirpath, dirnames, filenames) in walk(BACKUPS_PATH):
        backup_files.extend(filenames)
        break

    # get the available backup levels
    available_levels: list[int] = []
    for backup in backup_files:
        match = re.match(r"backup_([0-9]+)\.sql", backup)
        if match:
            available_levels.append(int(match.group(1)))

    return available_levels


def delete_old_backups():
    backups = get_available_backups()

    # sort in descending order
    backups.sort(reverse=True)

    for index, backup in enumerate(backups):
        # we keep 3 backups but only 2 are really needed
        if index > 2:
            _logger.info(f'Deleting backup level: {backup}')
            backup_file = get_backup_file(backup)
            remove(backup_file)
