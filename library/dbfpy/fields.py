"""DBF fields definitions.

TODO:
  - make memos work
"""
import numbers

"""History (most recent first):
01-dec-2006 [als]   Timestamp columns use None for empty values
31-oct-2006 [als]   support field types 'F' (float), 'I' (integer)
                    and 'Y' (currency);
                    automate export and registration of field classes
04-jul-2006 [als]   added export declaration
10-mar-2006 [als]   decode empty values for Date and Logical fields;
                    show field name in errors
10-mar-2006 [als]   fix Numeric value decoding: according to spec,
                    value always is string representation of the number;
                    ensure that encoded Numeric value fits into the field
20-dec-2005 [yc]    use field names in upper case
15-dec-2005 [yc]    field definitions moved from `dbf`.
"""

__version__ = "$Revision: 1.8 $"[11:-2]
__date__ = "$Date: 2006/12/01 11:44:11 $"[7:-2]

__all__ = ["lookupFor",] # field classes added at the end of the module

import datetime
import struct
import sys

import utils

## abstract definitions

class DbfFieldDef(object):
    """Abstract field definition.

    Child classes must override ``type`` class attribute to provide datatype
    infromation of the field definition. For more info about types visit
    `http://www.clicketyclick.dk/databases/xbase/format/data_types.html`

    Also child classes must override ``defaultValue`` field to provide
    default value for the field value.

    If child class has fixed length ``length`` class attribute must be
    overriden and set to the valid value. None value means, that field
    isn't of fixed length.

    Note: ``name`` field must not be changed after instantiation.

    """

    __slots__ = "name", "length", "decimalCount", "start", "end"

    # length of the field, None in case of variable-length field,
    # or a number if this field is a fixed-length field
    length = None

    # field type. for more information about fields types visit
    # `http://www.clicketyclick.dk/databases/xbase/format/data_types.html`
    # must be overriden in child classes
    typeCode = None

    # default value for the field. this field must be
    # overriden in child classes
    defaultValue = None

    def __init__(self, name, length=None, decimalCount=None,
        start=None, stop=None, encoding=None
    ):
        """Initialize instance."""
        assert self.typeCode is not None, "Type code must be overriden"
        assert self.defaultValue is not None, "Default value must be overriden"
        ## fix arguments
#        name = str(name).upper()
        name = name.upper()
        assert len(name)<=10, "DBF field length must be <=10"
        if self.__class__.length is None:
            if length is None:
                raise ValueError("[%s] Length isn't specified" % name)
            length = int(length)
            if length <= 0:
                raise ValueError("[%s] Length must be a positive integer"
                    % name)
        else:
            length = self.length
        if decimalCount is None:
            decimalCount = 0
        ## set fields
        self.name = name
        # FIXME: validate length according to the specification at
        # http://www.clicketyclick.dk/databases/xbase/format/data_types.html
        self.length = length
        self.decimalCount = decimalCount
        self.start = start
        self.end = stop
        self.encoding = encoding

    def __cmp__(self, other):
        return cmp(self.name, other.upper())

    def __hash__(self):
        return hash(self.name)

    @classmethod
    def fromString(cls, string, start, encoding=None):
        """Decode dbf field definition from the string data.

        Arguments:
            string:
                a string, dbf definition is decoded from. length of
                the string must be 32 bytes.
            start:
                position in the database file.
        """
        assert len(string) == 32
        _length = ord(string[16])
        name = utils.unzfill(string)[:11]
        if encoding:
            name = unicode(name, encoding)
        else:
            name = unicode(name)
        return cls(name, _length, ord(string[17]),
            start, start + _length)
#    fromString = classmethod(fromString)

    def toString(self):
        """Return encoded field definition.

        Return:
            Return value is a string object containing encoded
            definition of this field.

        """
        if self.encoding:
            _name = self.name.encode(self.encoding)
        else:
            _name = str(self.name)

        if sys.version_info < (2, 4):
            # earlier versions did not support padding character
            _name = _name[:11] + "\0" * (11 - len(_name))
        else:
            _name = _name.ljust(11, '\0')
        return (
            _name +
            self.typeCode +
            #data address
            chr(0) * 4 +
            chr(self.length) +
            chr(self.decimalCount) +
            chr(0) * 14
        )

    def __repr__(self):
        return "%-10s %1s %3d %3d" % self.fieldInfo()

    def fieldInfo(self):
        """Return field information.

        Return:
            Return value is a (name, type, length, decimals) tuple.

        """
        return (self.name, self.typeCode, self.length, self.decimalCount)

    def decodeFromRecord(self, record, dbf):
        """Return decoded field value from the record string."""
        return self.decodeValue(record[self.start:self.end], dbf)

    def decodeValue(self, value, dbf):
        """Return decoded value from string value.

        This method shouldn't be used publicaly. It's called from the
        `decodeFromRecord` method.

        This is an abstract method and it must be overriden in child classes.
        """
        raise NotImplementedError

    def encodeValue(self, value, dbf):
        """Return str object containing encoded field value.

        This is an abstract method and it must be overriden in child classes.
        """
        raise NotImplementedError

## real classes

class DbfCharacterFieldDef(DbfFieldDef):
    """Definition of the character field."""

    typeCode = "C"
    defaultValue = ""

    def decodeValue(self, value, dbf):
        """Return string object.

        Return value is a ``value`` argument with stripped right spaces.

        """
        raw = value.rstrip(' \0')
        if self.encoding:
            return unicode(raw, self.encoding)
        else:
            return unicode(raw)

    def encodeValue(self, value, dbf):
        """Return raw data string encoded from a ``value``."""
        if self.encoding:
            return str(unicode(value).encode(self.encoding, 'replace'))[:self.length].ljust(self.length)
        else:
            return str(value)[:self.length].ljust(self.length)


class DbfNumericFieldDef(DbfFieldDef):
    """Definition of the numeric field."""

    typeCode = "N"
    # XXX: now I'm not sure it was a good idea to make a class field
    # `defaultValue` instead of a generic method as it was implemented
    # previously -- it's ok with all types except number, cuz
    # if self.decimalCount is 0, we should return 0 and 0.0 otherwise.
    defaultValue = 0

    def decodeValue(self, value, dbf):
        """Return a number decoded from ``value``.

        If decimals is zero, value will be decoded as an integer;
        or as a float otherwise.

        Return:
            Return value is a int (long) or float instance.

        """
        value = value.strip(' \0')
        if self.decimalCount > 0:
            # a float (has decimal digits)
            if value:
                return float(value)
            return 0.0
        else:
            # an integer
            if value:
                return int(value)
            return 0

    def encodeValue(self, value, dbf):
        """Return string containing encoded ``value``."""
        try:
            if not isinstance(value, numbers.Number):
                raise TypeError('Number is needed')
            _rv = ("%*.*f" % (self.length, self.decimalCount, value))
        except TypeError, e:
            raise ValueError("[%s] %s: present %s" % (self.name, e.message, repr(value)))

        if len(_rv) > self.length:
            _ppos = _rv.find(".")
            if 0 <= _ppos <= self.length:
                _rv = _rv[:self.length]
            else:
                raise ValueError("[%s] Numeric overflow: %s (field width: %i)"
                    % (self.name, _rv, self.length))
        return _rv

class DbfFloatFieldDef(DbfNumericFieldDef):
    """Definition of the float field - same as numeric."""

    typeCode = "F"

class DbfIntegerFieldDef(DbfFieldDef):
    """Definition of the integer field."""

    typeCode = "I"
    length = 4
    defaultValue = 0

    def decodeValue(self, value, dbf):
        """Return an integer number decoded from ``value``."""
        return struct.unpack("<i", value)[0]

    def encodeValue(self, value, dbf):
        """Return string containing encoded ``value``."""
        return struct.pack("<i", int(value))

class DbfCurrencyFieldDef(DbfFieldDef):
    """Definition of the currency field."""

    typeCode = "Y"
    length = 8
    defaultValue = 0.0

    def decodeValue(self, value, dbf):
        """Return float number decoded from ``value``."""
        return struct.unpack("<q", value)[0] / 10000.

    def encodeValue(self, value, dbf):
        """Return string containing encoded ``value``."""
        return struct.pack("<q", round(value * 10000))

class DbfLogicalFieldDef(DbfFieldDef):
    """Definition of the logical field."""

    typeCode = "L"
    defaultValue = -1
    length = 1

    def decodeValue(self, value, dbf):
        """Return True, False or -1 decoded from ``value``."""
        # Note: value always is 1-char string
        if value == "?":
            return -1
        if value in "NnFf ":
            return False
        if value in "YyTt":
            return True
        raise ValueError("[%s] Invalid logical value %r" % (self.name, value))

    def encodeValue(self, value, dbf):
        """Return a character from the "TF?" set.

        Return:
            Return value is "T" if ``value`` is True
            "?" if value is -1 or False otherwise.

        """
        if value is True:
            return "T"
        if value == -1:
            return "?"
        return "F"


class DbfMemoFieldDef(DbfFieldDef):
    """Definition of the memo field.

    Note: memos aren't currenly completely supported.

    """

    typeCode = "M"
    defaultValue = " " * 10
    length = 10

    def decodeValue(self, value, dbf):
        """Return string object."""
        value = value.strip()
        if value:
            raw = dbf.getDbtItem(int(value))
            if self.encoding:
                return unicode(raw, self.encoding)
            else:
                return unicode(raw)
        return u''

    def encodeValue(self, value, dbf):
        """Return memo item number."""
        if value:
            if self.encoding:
                raw = str(unicode(value).encode(self.encoding, 'replace'))
            else:
                raw = str(value)
#            raw.replace('\r\n', '\x93\n')
            return str(dbf.putDbtItem(raw))[:self.length].ljust(self.length)
        else:
            return self.defaultValue


class DbfDateFieldDef(DbfFieldDef):
    """Definition of the date field."""

    typeCode = "D"
#    defaultValue = utils.classproperty(lambda cls: datetime.date.today())
    # "yyyymmdd" gives us 8 characters
    length = 8
    defaultValue = ''
    emptyValue = " " * length

    def decodeValue(self, value, dbf):
        """Return a ``datetime.date`` instance decoded from ``value``."""
        value = value.strip(' \0')
        if value:
            return utils.getDate(value)
        else:
            return None

    def encodeValue(self, value, dbf):
        """Return a string-encoded value.

        ``value`` argument should be a value suitable for the
        `utils.getDate` call or None.

        Return:
            Return value is a string in format "yyyymmdd" or empty string

        """
        result = self.emptyValue
        if value:
            value = utils.getDate(value)
            try:
                result = value.strftime("%Y%m%d")
            except ValueError, e:
                pass
        return result


class DbfDateTimeFieldDef(DbfFieldDef):
    """Definition of the timestamp field."""

    # a difference between JDN (Julian Day Number)
    # and GDN (Gregorian Day Number). note, that GDN < JDN
    JDN_GDN_DIFF = 1721425
    typeCode = "T"
    defaultValue = utils.classproperty(lambda cls: datetime.datetime.now())
    # two 32-bits integers representing JDN and amount of
    # milliseconds respectively gives us 8 bytes.
    # note, that values must be encoded in LE byteorder.
    length = 8

    def decodeValue(self, value, dbf):
        """Return a `datetime.datetime` instance."""
        assert len(value) == self.length
        # LE byteorder
        _jdn, _msecs = struct.unpack("<2I", value)
        if _jdn >= 1:
            _rv = datetime.datetime.fromordinal(_jdn - self.JDN_GDN_DIFF)
            _rv += datetime.timedelta(0, _msecs / 1000.0)
        else:
            # empty date
            _rv = None
        return _rv

    def encodeValue(self, value, dbf):
        """Return a string-encoded ``value``."""
        if value:
            value = utils.getDateTime(value)
            # LE byteorder
            _rv = struct.pack("<2I", value.toordinal() + self.JDN_GDN_DIFF,
                (value.hour * 3600 + value.minute * 60 + value.second) * 1000)
        else:
            _rv = "\0" * self.length
        assert len(_rv) == self.length
        return _rv


_fieldsRegistry = {}

def registerField(fieldCls):
    """Register field definition class.

    ``fieldCls`` should be subclass of the `DbfFieldDef`.

    Use `lookupFor` to retrieve field definition class
    by the type code.

    """
    assert fieldCls.typeCode is not None, "Type code isn't defined"
    # XXX: use fieldCls.typeCode.upper()? in case of any decign
    # don't forget to look to the same comment in ``lookupFor`` method
    _fieldsRegistry[fieldCls.typeCode] = fieldCls


def lookupFor(typeCode):
    """Return field definition class for the given type code.

    ``typeCode`` must be a single character. That type should be
    previously registered.

    Use `registerField` to register new field class.

    Return:
        Return value is a subclass of the `DbfFieldDef`.

    """
    # XXX: use typeCode.upper()? in case of any decign don't
    # forget to look to the same comment in ``registerField``
    return _fieldsRegistry[typeCode]

## register generic types

for (_name, _val) in globals().items():
    if isinstance(_val, type) and issubclass(_val, DbfFieldDef) \
    and (_name != "DbfFieldDef"):
        __all__.append(_name)
        registerField(_val)
del _name, _val

# vim: et sts=4 sw=4 :
