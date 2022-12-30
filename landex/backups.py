import re
import sys
import gzip, logging
from typing import Union
from io import StringIO
from pathlib import Path
from os import remove, walk
from os import environ as env
from sh import psql, pg_dump, ErrorReturnCode

from dipdup.context import HookContext
from dipdup.enums import MessageType
from dipdup.config import PostgresDatabaseConfig, SqliteDatabaseConfig

TOKEN_METADATA_DIR = env.get('TOKEN_METADATA_DIR', './tz1aND_metadata')
BACKUPS_PATH = f'{TOKEN_METADATA_DIR}/backups'

_logger = logging.getLogger(__name__)
_logger.info(f'BACKUPS_PATH={BACKUPS_PATH}')

# suppress logging on sh
logging.getLogger("sh").setLevel(logging.WARNING)


def backup(ctx: HookContext):
    """Backup database.
    Raises an Exception on error."""
    level, database_config = _get_level_and_dbconfig(ctx)
    _backup(level, database_config)


def backup_if_older_than(ctx: HookContext, age_in_blocks: int):
    """Backup database if current_level - last_backup_level > `age_in_blocks`.
    Raises an Exception on error."""
    level, database_config = _get_level_and_dbconfig(ctx)

    available_levels = _get_available_backups()

    # find highest level
    highest_level = 0
    for level in available_levels:
        if level > highest_level:
            highest_level = level

    # if highest level is old-ish, run a backup.
    if level - highest_level > age_in_blocks:
        _backup(level, database_config)
    else:
        _logger.info(f'Latest backup is recent, skipped backup.')


async def restore(ctx: HookContext):
    """Restore database from last leve <= head.
    Raises an Exception on error."""
    database_config = _get_dbconfig(ctx)

    available_levels = _get_available_backups()

    # if no backups available, reindex
    if not available_levels:
        raise Exception('Not backups available, skipping restore')

    # find the right level. ie the on that's closest to to_level
    chosen_level: int = 0
    to_level: int = sys.maxsize
    for level in available_levels:
        if level <= to_level and level > chosen_level:
            chosen_level = level

    # Try to restore or reindex. Will throw on error.
    _restore_level(chosen_level, database_config)
    _logger.info('Restarting dipdup...')
    await ctx.restart()


def delete_old_backups(keep: int = 3):
    """Deletes backups if there are more than `keep` backups."""
    backups = _get_available_backups()

    # sort in descending order
    backups.sort(reverse=True)

    for index, backup in enumerate(backups):
        if index >= keep:
            _logger.info(f'Deleting backup level: {backup}')
            backup_file = _get_backup_file(backup)
            remove(backup_file)


def _get_backup_file(level: int):
    return f'{BACKUPS_PATH}/backup_{level}.sql'


def _get_level_and_dbconfig(ctx: HookContext):
    level = ctx.get_tzkt_datasource("tzkt_mainnet").get_channel_level(MessageType.head)
    database_config = _get_dbconfig(ctx)

    return level, database_config


def _get_dbconfig(ctx: HookContext):
    database_config: Union[SqliteDatabaseConfig, PostgresDatabaseConfig] = ctx.config.database

    # if not a postgres db, reindex.
    if database_config.kind != "postgres":
        raise Exception('Not postgres database, skipping backup')

    return database_config


def _backup(level: int, database_config: PostgresDatabaseConfig):
    # create directory
    Path(BACKUPS_PATH).mkdir(parents=True, exist_ok=True)

    backup_file = _get_backup_file(level)

    # check if backup at this level exists and skip.
    #if Path(backup_file).is_file():
    #    _logger.info(f'Backup at level {level} exists')
    #    return

    # TODO: use gzip but causes 'invalid byte sequence for encoding "UTF8": 0x8b' on restore
    _logger.info(f'Backing up database at level {level} to {backup_file}')
    with open(backup_file, 'wb') as f:
        try:
            err_buf = StringIO()
            pg_dump('-d', f'postgresql://{database_config.user}:{database_config.password}@{database_config.host}:{database_config.port}/{database_config.database}', '--clean',
                '-n', database_config.schema_name, _out=f, _err=err_buf) #, '-E', 'UTF8'
        except ErrorReturnCode:
            err = err_buf.getvalue()
            raise Exception(f'Database backup failed: {err}')


def _restore_level(level: int, database_config: PostgresDatabaseConfig):
    # try to restore or reindex
    backup_file = _get_backup_file(level)
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


def _get_available_backups():
    # get all files in backup dir
    backup_files: list[str] = []
    for (_, _, filenames) in walk(BACKUPS_PATH):
        backup_files.extend(filenames)
        break

    # get the available backup levels
    available_levels: list[int] = []
    for backup in backup_files:
        match = re.match(r"backup_([0-9]+)\.sql", backup)
        if match:
            available_levels.append(int(match.group(1)))

    return available_levels
