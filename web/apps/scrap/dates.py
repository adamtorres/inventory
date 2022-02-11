from django.conf import settings
from django.utils import timezone

from dateutil import relativedelta
import pytz


def first_of_month(dt=None):
    if not dt:
        dt = timezone.now().date()
    return dt - relativedelta.relativedelta(days=dt.day-1)


def humanize_date(dt):
    dt = timezone.make_aware(
        timezone.datetime.combine(dt, timezone.datetime.min.time()), pytz.timezone(settings.TIME_ZONE))
    local_dt = timezone.localtime(dt, pytz.timezone(settings.TIME_ZONE))
    return f'{local_dt.strftime("%Y-%m-%d")}'


def humanize_datetime(dt):
    local_dt = timezone.localtime(dt, pytz.timezone(settings.TIME_ZONE))
    return f'{local_dt.strftime("%Y-%m-%d %H:%M")}'


def last_of_month(dt=None):
    if not dt:
        dt = timezone.now().date()
    return dt - relativedelta.relativedelta(days=dt.day, months=-1)


def relative_months(date_or_how_many, start_of_month=False, end_of_month=False, first_dow=None, last_dow=None):
    if 1 < sum([1 for i in [start_of_month, end_of_month, first_dow, last_dow] if i]):
        raise ValueError("Must supply zero or one kwarg.  Cannot supply more than one.")
    dt = timezone.now().date()
    if date_or_how_many:
        if isinstance(date_or_how_many, int):
            dt = dt + relativedelta.relativedelta(months=date_or_how_many)
        else:
            dt = date_or_how_many
    if start_of_month:
        dt = first_of_month(dt)
    if end_of_month:
        dt = last_of_month(dt)
    if first_dow:
        if first_dow not in ('SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'):
            raise ValueError("first_dow must be one of 'SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'.")
        dow = getattr(relativedelta, first_dow)
        dt = dt + relativedelta.relativedelta(day=1, weekday=dow(1))
    if last_dow:
        if last_dow not in ('SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'):
            raise ValueError("last_dow must be one of 'SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'.")
        dow = getattr(relativedelta, last_dow)
        dt = dt + relativedelta.relativedelta(day=31, weekday=dow(-1))
    return dt
