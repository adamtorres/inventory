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
