import re
import gzip, logging
from io import StringIO
from pathlib import Path
from os import remove, walk
from os import environ as env
from sh import psql, pg_dump, ErrorReturnCode

from dipdup.context import HookContext
from dipdup.enums import MessageType
from dipdup.config import PostgresDatabaseConfig

BACKUPS_DIR = env.get('BACKUPS_DIR', './backups')

_logger = logging.getLogger(__name__)
_logger.info(f'BACKUPS_DIR={BACKUPS_DIR}')

# suppress logging on sh
logging.getLogger("sh").setLevel(logging.WARNING)


async def backup(ctx: HookContext):
    """Backup database.
    Raises an Exception on error."""
    level, database_config = _get_level_and_dbconfig(ctx)
    head_block = await ctx.get_tzkt_datasource("tzkt_mainnet").get_head_block()

    _backup(head_block.chain_id, level, database_config)


async def backup_if_older_than(ctx: HookContext, age_in_blocks: int):
    """Backup database if current_level - last_backup_level > `age_in_blocks`.
    Raises an Exception on error."""
    level, database_config = _get_level_and_dbconfig(ctx)
    head_block = await ctx.get_tzkt_datasource("tzkt_mainnet").get_head_block()

    available_levels = _get_available_backups(head_block.chain_id)

    # find highest level
    highest_level = 0
    for level in available_levels:
        if level > highest_level:
            highest_level = level

    # if highest level is old-ish, run a backup.
    if level - highest_level > age_in_blocks:
        _backup(head_block.chain_id, level, database_config)
    else:
        _logger.info(f'Latest backup is recent, skipped backup.')


async def restore(ctx: HookContext):
    """Restore database from last backup (highest level).
    Raises an Exception on error."""
    database_config = _get_dbconfig(ctx)
    head_block = await ctx.get_tzkt_datasource("tzkt_mainnet").get_head_block()

    available_levels = _get_available_backups(head_block.chain_id)

    # if no backups available, reindex
    if not available_levels:
        raise Exception('Not backups available, skipping restore')

    # find highest level
    highest_level = 0
    for level in available_levels:
        if level > highest_level:
            highest_level = level

    # Try to restore or reindex. Will throw on error.
    _restore_level(head_block.chain_id, highest_level, database_config)
    _logger.info('Restarting dipdup...')
    await ctx.restart()


async def delete_old_backups(ctx: HookContext, keep: int = 3):
    """Deletes backups if there are more than `keep` backups.
    Raises an Exception on error."""
    head_block = await ctx.get_tzkt_datasource("tzkt_mainnet").get_head_block()

    backups = _get_available_backups(head_block.chain_id)

    # sort in descending order
    backups.sort(reverse=True)

    for index, backup in enumerate(backups):
        if index >= keep:
            _logger.info(f'Deleting backup level: {backup}')
            backup_file = _get_backup_file(head_block.chain_id, backup)
            remove(backup_file)


def _get_backup_file(chain_id: str, level: int):
    return f'{BACKUPS_DIR}/backup_{chain_id}_{level}.sql'


def _get_level_and_dbconfig(ctx: HookContext):
    level = ctx.get_tzkt_datasource("tzkt_mainnet").get_channel_level(MessageType.head)
    database_config = _get_dbconfig(ctx)

    return level, database_config


def _get_dbconfig(ctx: HookContext):
    # if not a postgres db, reindex.
    if ctx.config.database.kind != "postgres":
        raise Exception('Not postgres database, skipping backup')

    return ctx.config.database


def _backup(chain_id: str, level: int, database_config: PostgresDatabaseConfig):
    # create directory
    # NOTE: prob not needed?
    Path(BACKUPS_DIR).mkdir(parents=True, exist_ok=True)

    backup_file = _get_backup_file(chain_id, level)

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


def _restore_level(chain_id: str, level: int, database_config: PostgresDatabaseConfig):
    # try to restore or reindex
    backup_file = _get_backup_file(chain_id, level)
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


def _get_available_backups(chain_id: str):
    # get all files in backup dir
    backup_files: list[str] = []
    for (_, _, filenames) in walk(BACKUPS_DIR):
        backup_files.extend(filenames)
        break

    # get the available backup levels
    available_levels: list[int] = []
    for backup in backup_files:
        match = re.match(rf"backup_{chain_id}_([0-9]+)\.sql", backup)
        if match:
            available_levels.append(int(match.group(1)))

    return available_levels
