#!/usr/bin/env python3
from slack import WebClient


def get_connected_slack_client(secrets_env):
    slack_client = WebClient(token=secrets_env.str('SLACK_TOKEN'))
    return slack_client

    # for real time connection
    # if slack_client.rtm_connect(with_team_state=False):
    #     return slack_client
    #raise RuntimeError('SlackClient.rtm_connect failed')


def _send_slack_msg(slack_client, channel_id: str, msg: str):
    slack_client.chat_postMessage(
        channel=channel_id,
        text=msg
    )


def send_success_notification(slack_client, dev_db_link: str, seconds_elapsed: int, channel_id: str):
    msg = f'Databases backed up successfully in {seconds_elapsed} seconds. *Dev DB download link:* {dev_db_link}'
    _send_slack_msg(slack_client, channel_id, msg)


def send_error_notification(slack_client, error_msg: str, channel_id: str):
    msg = f'*Failed to back up databases:*\n```{error_msg}```'
    _send_slack_msg(slack_client, channel_id, msg)
