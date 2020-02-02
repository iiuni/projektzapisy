"""Object prepares attachments to send to Slack. Then sends all collected attachments"""

import json
import os
import requests


class Slack:
    def __init__(self):
        self.attachments = []

    def add_attachment(self, color, title, text):
        attachment = {
            "color": color,
            "title": title,
            "text": text
        }
        self.attachments.append(attachment)

    def prepare_slack_message(self, summary: 'Summary'):
        for term in summary.created_terms:
            text = "day: {}\nstart_time: {}\nend_time: {}\nteacher: {}".format(
                term.dayOfWeek, term.start_time, term.end_time, term.group.teacher)
            self.add_attachment('good', "Created: {}".format(term.group), text)

        for term, diffs in summary.updated_terms:
            text = ""
            for diff in diffs:
                text = text + "{}: {}->{}\n".format(diff[0], diff[1], diff[2])
            self.add_attachment('warning', "Updated: {}".format(term.group), text)

        for term_str, group_str in summary.deleted_terms:
            self.add_attachment('danger', 'Deleted a term:',
                                "group: {}\nterm: {}".format(group_str, term_str))

        for scheduler_data_str, map_str in summary.maps_added:
            self.add_attachment('good', 'Added map:',
                                "{} mapped to {}".format(scheduler_data_str, map_str))

        for prop_str in summary.multiple_proposals:
            self.add_attachment('warning', 'Multiple proposals:',
                                "proposal {} has multiple instances with different status".format(prop_str))

    def write_to_slack(self):
        slack_data = {
            'text': "The following groups were updated in fereol (scheduler's sync):",
            'attachments': self.attachments
        }
        slack_webhook_url = os.environ['slack_url']
        response = requests.post(
            slack_webhook_url, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
