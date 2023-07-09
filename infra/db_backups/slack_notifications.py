#!/usr/bin/env python3
from slack import WebClient


def get_connected_slack_client(secrets_env):
    slack_client = WebClient(token=secrets_env.str('SLACK_TOKEN'))
    return slack_client

    # for real time connection
    # if slack_client.rtm_connect(with_team_state=False):
    #     return slack_client
    #raise RuntimeError('SlackClient.rtm_connect failed')


def _send_slack_msg(slack_client, channel_id: str, msg: str, attachments):
    slack_client.chat_postMessage(
        channel=channel_id,
        text=msg,
        attachments=attachments
    )


def send_success_notification(slack_client, dev_db_link: str, seconds_elapsed: int, channel_id: str, attempts: int, attachments):
    if attempts == 1:
        msg = f'Databases backed up successfully in {seconds_elapsed} seconds. *Dev DB download link:* {dev_db_link}'
    else:
        msg = f'Databases backed up successfully in {seconds_elapsed} seconds, after {attempts} attempts. *Dev DB download link:* {dev_db_link} \nFailed attempt(s) tracebacks:'
        
    _send_slack_msg(slack_client, channel_id, msg, attachments)


def send_error_notification(slack_client, error_msg: str, channel_id: str, attachments):
    msg = f'*Failed to back up databases. Failed attempt(s) tracebacks:'
    _send_slack_msg(slack_client, channel_id, msg, attachments)
