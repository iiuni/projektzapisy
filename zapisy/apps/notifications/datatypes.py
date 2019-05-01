from datetime import datetime
from typing import Dict


class Notification:

    def __init__(self, description_id: str, description_args: Dict,
                 target: str = "#", issued_on: datetime = datetime.now()):
        self.description_id = description_id
        self.description_args = description_args
        self.target = target
        self.issued_on = issued_on
