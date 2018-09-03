#!/usr/bin/env python3
from slackclient import SlackClient


def get_connected_slack_client(secrets_env):
    slack_client = SlackClient(secrets_env.str('SLACK_TOKEN'))
    if slack_client.rtm_connect(with_team_state=False):
        return slack_client
    raise RuntimeError('SlackClient.rtm_connect failed')


def _send_slack_msg(slack_client, msg: str):
    slack_client.api_call(
        'chat.postMessage',
        channel='db_backups',
        text=msg
    )


def send_success_notification(slack_client, dev_db_link: str, seconds_elapsed: int):
    msg = f'Databases backed up successfully in {seconds_elapsed} seconds. *Dev DB download link:* {dev_db_link}'
    _send_slack_msg(slack_client, msg)


def send_error_notification(slack_client, error_msg: str):
    msg = f'*Failed to back up databases:*\n```{error_msg}```'
    _send_slack_msg(slack_client, msg)
