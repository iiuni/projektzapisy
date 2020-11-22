import os
from datetime import datetime, timedelta

import dropbox

DROPBOX_DEV_DUMPS_DIRNAME = '/dev_dumps'
DROPBOX_PROD_DUMPS_DIRNAME = '/prod_dumps'
DUMPS_THRESHOLD = timedelta(weeks=-4)


def upload_dumps(dropbox_token, prod_file, dev_file):
    dbx = dropbox.Dropbox(dropbox_token)
    check_directories(dbx)
    remove_old_files(dbx)
    upload_file(dbx, prod_file, DROPBOX_PROD_DUMPS_DIRNAME)
    dev_dbx_path = upload_file(dbx, dev_file, DROPBOX_DEV_DUMPS_DIRNAME)
    return dbx.sharing_create_shared_link(dev_dbx_path)


def check_directories(dbx):
    """Checks if required directories exist.

    Raises:
        dropbox.exceptions.ApiError: Directories don't exist.
    """
    try:
        dbx.files_get_metadata(DROPBOX_PROD_DUMPS_DIRNAME)
        dbx.files_get_metadata(DROPBOX_DEV_DUMPS_DIRNAME)
    except dropbox.exceptions.ApiError:
        raise


def remove_old_files(dbx):
    """Removes files older than set threshold."""
    oldest_allowed_modtime = datetime.now() + DUMPS_THRESHOLD
    remove_files_older_than_date(dbx, DROPBOX_PROD_DUMPS_DIRNAME, oldest_allowed_modtime)
    remove_files_older_than_date(dbx, DROPBOX_DEV_DUMPS_DIRNAME, oldest_allowed_modtime)


def remove_files_older_than_date(dbx, folder_path, threshold_dt):
    file_list = dbx.files_list_folder(folder_path)
    for file in file_list.entries:
        if file.client_modified < threshold_dt:
            dbx.files_delete(file.path_lower)


def upload_file(dbx, file_path, folder_path):
    file_bytes = open(file_path, mode='rb').read()
    file_name = os.path.basename(file_path)
    dropbox_path = os.path.join(folder_path, file_name)
    dbx.files_upload(file_bytes, dropbox_path)
    return dropbox_path
