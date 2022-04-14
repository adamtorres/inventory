from dateutil import relativedelta
from django.utils import timezone


def get_monthly_date_range(months):
    first_of_current_month = timezone.now().date().replace(day=1)
    last_of_current_month = first_of_current_month + relativedelta.relativedelta(months=1, days=-1)
    if timezone.now().date() == last_of_current_month:
        # If today is the last day of the month, then we have a full 'months' worth.  If not, we will end up with
        # months + the current partial month.
        months -= 1
    first_of_months_ago = first_of_current_month - relativedelta.relativedelta(months=months - 1)
    return [first_of_months_ago, last_of_current_month]
