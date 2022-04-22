from dateutil import relativedelta
from django.utils import timezone


def get_monthly_date_range(months):
    """
    Given a number of months, returns the first day of `months` ago and last day of the current month.
    """
    first_of_current_month = timezone.now().date().replace(day=1)
    last_of_current_month = first_of_current_month + relativedelta.relativedelta(months=1, days=-1)
    if timezone.now().date() == last_of_current_month:
        # If today is the last day of the month, then we have a full 'months' worth.  If not, we will end up with
        # months + the current partial month.
        months -= 1
    first_of_months_ago = first_of_current_month - relativedelta.relativedelta(months=months - 1)
    return [first_of_months_ago, last_of_current_month]


def last_months(months=3, start_at_first=True):
    """
    Returns a start/end datetime pair for the last # months.

    :param months: Number of months to cover in the returned range.
    :param start_at_first: When True, the returned start date will be the first of the month.  False will be the current
        day.
    :return: Returns a dict with the start datetime and two options for end datetime.
    """
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = today - relativedelta.relativedelta(months=months)
    if start_at_first:
        start_date = start_date.replace(day=1)
    end_date = today + relativedelta.relativedelta(days=1)
    return {
        "start__gte": start_date,
        "end__lt": end_date,
        "end__lte": end_date + relativedelta.relativedelta(microseconds=-1),
    }


def recent_quarters():
    """
    Returns the calendar year quarters starting from the most recent complete quarter and going back 2 years for a total
    of 8 quarters.

    :return: dict with "yyyyQ#" keys and values of dict with "start__gte", "end__lt", "end__lte" keys.
    """
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    first_of_year = timezone.make_aware(timezone.datetime(today.year, 1, 1))
    _quarters = {}
    q = now.month % 4
    while len(_quarters) < 8:
        quarter_str = f"{(first_of_year + relativedelta.relativedelta(months=3 * q)).year}Q{(q%4)+1}"
        quarter_limits = {
            "name": quarter_str,
            "start__gte": first_of_year + relativedelta.relativedelta(months=3 * q),
            "end__lt": first_of_year + relativedelta.relativedelta(months=3 * (q + 1)),
            "end__lte": first_of_year + relativedelta.relativedelta(months=3 * (q + 1), microseconds=-1),
        }
        if quarter_limits['end__lte'] < now:
            _quarters[quarter_str] = quarter_limits
        q -= 1
    return _quarters
