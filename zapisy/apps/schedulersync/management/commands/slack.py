"""Writes informations about changes.

Object prepares messages (attachments) from given Summary object.
Then sends all collected attachments to Slack or writes onto screen.

"""

import json

import requests


DAYS_OF_WEEK = {'1': 'monday',
                '2': 'tuesday',
                '3': 'wednesday',
                '4': 'thursday',
                '5': 'friday',
                '6': 'saturday',
                '7': 'sunday', }


class Slack:
    def __init__(self, slack_webhook_url):
        self.attachments = []
        self.slack_webhook_url = slack_webhook_url

    def add_attachment(self, color, title, text):
        attachment = {
            'color': color,
            'title': title,
            'text': text
        }
        self.attachments.append(attachment)

    def prepare_message(self, summary: 'Summary'):
        for term in summary.created_terms:
            text = "day: {}\nstart_time: {}\nend_time: {}\nteacher: {}".format(
                DAYS_OF_WEEK[term.dayOfWeek], term.start_time, term.end_time, term.group.teacher)
            self.add_attachment('good', "Created: {}".format(term.group), text)

        for term, diffs in summary.updated_terms:
            text = ""
            for diff in diffs:
                text = text + "{}: {}->{}\n".format(diff[0], diff[1], diff[2])
            self.add_attachment('warning', "Updated: {}".format(term.group), text)

        for term_str, group_str in summary.deleted_terms:
            self.add_attachment('danger', "Deleted a term:",
                                "group: {}\nterm: {}".format(group_str, term_str))

        for course in summary.deleted_courses:
            self.add_attachment('danger', "Deleted a course instance:",
                                "course instance: {}".format(course))

        for scheduler_data_str, map_str in summary.maps_added:
            self.add_attachment('good', "Added map:",
                                "{} mapped to {}".format(scheduler_data_str, map_str))

        for prop_str in summary.multiple_proposals:
            self.add_attachment('warning', "Multiple proposals:",
                                "proposal {} has multiple instances with different status".format(prop_str))

    def write_to_slack(self):
        slack_data = {
            'text': "The following groups were updated in fereol (scheduler's sync):",
            'attachments': self.attachments
        }
        response = requests.post(
            self.slack_webhook_url, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )

    def write_to_screen(self):
        print("\nChanges:\n")
        for attachment in self.attachments:
            print(attachment['title'])
            print(attachment['text'])
            print()
