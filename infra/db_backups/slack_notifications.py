from slack import WebClient


def connect_slack_client(slack_token):
    slack_client = WebClient(slack_token)
    if slack_client.rtm_connect(with_team_state=False):
        return slack_client
    raise RuntimeError('SlackClient.rtm_connect failed')


def send_slack_msg(slack_client, chan, msg: str):
    slack_client.api_call('chat.postMessage', channel=chan, text=msg)


def send_success_notification(slack_client, dev_db_link: str, seconds_elapsed: int):
    msg = f'Databases backed up successfully in {seconds_elapsed} seconds. *Dev DB download link:* {dev_db_link}'
    send_slack_msg(slack_client, 'db_backups', msg)


def send_error_notification(slack_client, error_msg: str):
    msg = f'*Failed to back up databases:*\n```{error_msg}```'
    send_slack_msg(slack_client, 'bugs', msg)
