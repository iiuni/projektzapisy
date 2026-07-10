MONDAY = '1'
TUESDAY = '2'
WEDNESDAY = '3'
THURSDAY = '4'
FRIDAY = '5'
SATURDAY = '6'
SUNDAY = '7'

DAYS_OF_WEEK = [(MONDAY, 'poniedziałek'),
                (TUESDAY, 'wtorek'),
                (WEDNESDAY, 'środa'),
                (THURSDAY, 'czwartek'),
                (FRIDAY, 'piątek'),
                (SATURDAY, 'sobota'),
                (SUNDAY, 'niedziela')]


def get_day_of_week(date):
    return DAYS_OF_WEEK[date.weekday()][0]


def get_python_day_of_week(day_of_week):
    try:
        return [x[0] for x in DAYS_OF_WEEK].index(day_of_week)
    except ValueError:
        return None
