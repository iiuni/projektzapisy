from datetime import datetime
from typing import Dict


class Notification:

    def __init__(self, id: str, issued_on: datetime, description_id: str,
                 description_args: Dict, target: str = "#"):
        self.id = id
        self.issued_on = issued_on
        self.description_id = description_id
        self.description_args = description_args
        self.target = target
