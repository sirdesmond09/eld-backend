from datetime import datetime

import pendulum


def get_formatted_durations(datetime: datetime) -> str:
    return pendulum.instance(datetime).diff_for_humans() 