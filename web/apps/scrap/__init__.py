from .change_source_mixin import ChangeSourceMixin
from .dates import humanize_date, humanize_datetime, first_of_month, last_of_month, relative_months


def snip_text(text, max_length=50, snip_str="...", head_and_tail=False):
    """
    Will snip a string so it is no longer than max_length.  Defaults to snipping the end but
    if head_and_tail, will snip the middle.
    """
    if (len(text) + len(snip_str)) > max_length:
        if head_and_tail:
            part_len = int((max_length - len(snip_str)) / 2)
            return f"{text[:part_len]}{snip_str}{text[-part_len:]}"
        else:
            return f"{text[:max_length-3]}{snip_str}"
    else:
        return text


def undecimal(value):
    """
    Converts a decimal value to int if there are no non-zero decimals.
    """
    return int(value) if not value % 1 else value
