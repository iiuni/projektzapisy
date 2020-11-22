import subprocess
import os
import traceback
import time
from datetime import datetime
import bz2

import environ
import anonymize
from slack_notifications import connect_slack_client, send_success_notification, \
    send_error_notification
from dropbox_upload import upload_dumps


TEMP_DB_NAME = "ii_zapisy_db_dump"


def get_secrets():
    """Returns environment with data required to open database."""
    env = environ.Env()
    secrets_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     os.pardir, 'env', '.env')
    environ.Env.read_env(secrets_file_path)
    return env


def get_filename(suff):
    time_now_str = time.strftime('%Y_%m_%d__%H_%M_%S')
    path = f'/tmp/ii_zapisy_db_dump_{time_now_str}_{suff}.bz2'
    return path


def get_temp_filename(suff):
    return f'/tmp/ii_zapisy_db_dump_{suff}.sql'


def run_psql_command(comm):
    res = subprocess.run(['sudo', '-su', 'postgres', 'psql', '-c', comm])
    try:
        res.check_returncode()
    except subprocess.CalledProcessError:
        raise


def run_script_command(db_user, db_port, db_name, db_password, input_file):
    res = subprocess.run(['psql', '-U', db_user, '-h', 'localhost', '-p', db_port,
                          '-f', input_file, db_name], env={'PGPASSWORD': db_password})
    try:
        res.check_returncode()
    except subprocess.CalledProcessError:
        raise


def run_pg_dump(db_user, db_port, db_name, db_password, output_file):
    res = subprocess.run(['pg_dump', '-U', db_user, '-h', 'localhost', '-p', db_port,
                          '-f', output_file, db_name], env={'PGPASSWORD': db_password})
    try:
        res.check_returncode()
    except subprocess.CalledProcessError:
        raise


def compress_file(inp, output):
    bz2file = bz2.open(output, "wb")
    source = open(inp, 'rb')
    bz2file.write(source.read())
    bz2file.close()


def perform_dump(secrets_env):
    """Performs production's and developers' database backup.

    Dev backup is created from prod backup after anonymization is performed
    on temporary copy of main database. After compression both files are
    uploaded to dropbox.

    Returns:
        Link to dropbox to developers' database
    """
    prod_filename = get_filename('prod')
    dev_filename = get_filename('dev')
    temp_prod_filename = get_temp_filename('prod')
    temp_dev_filename = get_temp_filename('dev')

    DATABASE_USER = secrets_env.str('DATABASE_USER')
    DATABASE_PORT = secrets_env.str('DATABASE_PORT')
    DATABASE_NAME = secrets_env.str('DATABASE_NAME')
    DATABASE_PASSWORD = secrets_env.str('DATABASE_PASSWORD')

    run_pg_dump(DATABASE_USER, DATABASE_PORT, DATABASE_NAME, DATABASE_PASSWORD,
                temp_prod_filename)
    run_psql_command(f'DROP DATABASE IF EXISTS {TEMP_DB_NAME}')
    run_psql_command(f'CREATE DATABASE {TEMP_DB_NAME}')
    run_script_command(DATABASE_USER, DATABASE_PORT, TEMP_DB_NAME, DATABASE_PASSWORD,
                       temp_prod_filename)
    run_script_command(DATABASE_USER, DATABASE_PORT, TEMP_DB_NAME, DATABASE_PASSWORD,
                       'anonymize.sql')
    anonymize.connect_and_anonymize(DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME,
                                    DATABASE_PORT)
    run_pg_dump(DATABASE_USER, DATABASE_PORT, TEMP_DB_NAME, DATABASE_PASSWORD,
                temp_dev_filename)
    run_psql_command(f'DROP DATABASE {TEMP_DB_NAME}')

    compress_file(temp_prod_filename, prod_filename)
    os.remove(temp_prod_filename)
    compress_file(temp_dev_filename, dev_filename)
    os.remove(temp_dev_filename)

    # send to dropbox
    dev_link = upload_dumps(secrets_env.str('DROPBOX_OAUTH2_TOKEN'), prod_filename,
                            dev_filename)
    return dev_link


def main():
    """Performs database backup and sends notification with result to Slack."""
    secrets_env = get_secrets()
    slack_client = connect_slack_client(secrets_env.str('SLACK_TOKEN'))
    try:
        start_time = datetime.now()
        # perform dump
        dev_link = perform_dump(secrets_env)
        end_time = datetime.now()
        seconds_elapsed = (end_time - start_time).seconds
        # send slack message
        send_success_notification(slack_client, dev_link.url, seconds_elapsed)
    except Exception:
        # send error slack massage
        err_description = traceback.format_exc()
        send_error_notification(slack_client, err_description)


if __name__ == '__main__':
    main()
