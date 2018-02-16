"""String utilities.

TODO:
  - allow strings in getDateTime routine;
"""
"""History (most recent first):
20-dec-2005 [yc]    handle long objects in getDate/getDateTime
16-dec-2005 [yc]    created from ``strutil`` module.
"""

__version__ = "$Revision: 1.2 $"[11:-2]
__date__ = "$Date: 2005/12/20 21:19:23 $"[7:-2]

import datetime
import time


def unzfill(str):
    """Return a string without ASCII NULs.

    This function searchers for the first NUL (ASCII 0) occurance
    and truncates string till that position.

    """
    try:
        return str[:str.index('\0')]
    except ValueError:
        return str


def getDate(date=None):
    """Return `datetime.date` instance.

    Type of the ``date`` argument could be one of the following:
        None:
            use current date value;
        datetime.date:
            this value will be returned;
        datetime.datetime:
            the result of the date.date() will be returned;
        string:
            assuming "%Y%m%d" or "%y%m%dd" format;
        number:
            assuming it's a timestamp (returned for example
            by the time.time() call;
        sequence:
            assuming (year, month, day, ...) sequence;

    Additionaly, if ``date`` has callable ``ticks`` attribute,
    it will be used and result of the called would be treated
    as a timestamp value.

    """
    if date is None:
        # use current value
        return datetime.date.today()
    if isinstance(date, datetime.date):
        return date
    if isinstance(date, datetime.datetime):
        return date.date()
    if isinstance(date, (int, long, float)):
        # date is a timestamp
        return datetime.date.fromtimestamp(date)
    if isinstance(date, basestring):
        try:
            if len(date) == 6:
                # yymmdd
                return datetime.date(*time.strptime(date, "%y%m%d")[:3])
            # yyyymmdd
            return datetime.date(*time.strptime(date, "%Y%m%d")[:3])
        except ValueError, e:
            print '{'+date+'}', e
            return None
    if hasattr(date, "__getitem__"):
        # a sequence (assuming date/time tuple)
        return datetime.date(*date[:3])
    return datetime.date.fromtimestamp(date.ticks())


def getDateTime(value=None):
    """Return `datetime.datetime` instance.

    Type of the ``value`` argument could be one of the following:
        None:
            use current date value;
        datetime.date:
            result will be converted to the `datetime.datetime` instance
            using midnight;
        datetime.datetime:
            ``value`` will be returned as is;
        string:
            *** CURRENTLY NOT SUPPORTED ***;
        number:
            assuming it's a timestamp (returned for example
            by the time.time() call;
        sequence:
            assuming (year, month, day, ...) sequence;

    Additionaly, if ``value`` has callable ``ticks`` attribute,
    it will be used and result of the called would be treated
    as a timestamp value.

    """
    if value is None:
        # use current value
        return datetime.datetime.today()
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.date):
        return datetime.datetime.fromordinal(value.toordinal())
    if isinstance(value, (int, long, float)):
        # value is a timestamp
        return datetime.datetime.fromtimestamp(value)
    if isinstance(value, basestring):
        raise NotImplementedError("Strings aren't currently implemented")
    if hasattr(value, "__getitem__"):
        # a sequence (assuming date/time tuple)
        return datetime.datetime(*tuple(value)[:6])
    return datetime.datetime.fromtimestamp(value.ticks())


class classproperty(property):
    """Works in the same way as a ``property``, but for the classes."""

    def __get__(self, obj, cls):
        return self.fget(cls)


# vim: set et sts=4 sw=4 :
