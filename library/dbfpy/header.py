"""DBF header definition.

TODO:
  - handle encoding of the character fields
    (encoding information stored in the DBF header)

"""
"""History (most recent first):
04-jul-2006 [als]   added export declaration
15-dec-2005 [yc]    created
"""

__version__ = "$Revision: 1.3 $"[11:-2]
__date__ = "$Date: 2006/07/04 08:10:53 $"[7:-2]

__all__ = ["DbfHeader"]

import cStringIO
import datetime
import struct
import fields
from utils import getDate


class DbfHeader(object):
    """Dbf header definition.

    For more information about dbf header format visit
    `http://www.clicketyclick.dk/databases/xbase/format/dbf.html#DBF_STRUCT`

    Examples:
        Create an empty dbf header and add some field definitions:
            dbfh = DbfHeader()
            dbfh.addField(("name", "C", 10))
            dbfh.addField(("date", "D"))
            dbfh.addField(DbfNumericFieldDef("price", 5, 2))
        Create a dbf header with field definitions:
            dbfh = DbfHeader([
                ("name", "C", 10),
                ("date", "D"),
                DbfNumericFieldDef("price", 5, 2),
            ])

    """

    __slots__ = ("signature", "fields", "lastUpdate", "recordLength",
        "recordCount", "headerLength", "changed", "encoding", "mapNameToIndex", "enableFieldNameDups")

    ## instance construction and initialization methods

    def __init__(self, fields=None, headerLength=0, recordLength=0, recordCount=0,
        signature=0x03, lastUpdate=None, encoding=None, enableFieldNameDups=False
    ):
        """Initialize instance.

        Arguments:
            fields:
                a list of field definitions;
            recordLength:
                size of the records;
            headerLength:
                size of the header;
            recordCount:
                number of records stored in DBF;
            signature:
                version number (aka signature). using 0x03 as a default meaning
                "File without DBT". for more information about this field visit
                ``http://www.clicketyclick.dk/databases/xbase/format/dbf.html#DBF_NOTE_1_TARGET``
            lastUpdate:
                date of the DBF's update. this could be a string ('yymmdd' or
                'yyyymmdd'), timestamp (int or float), datetime/date value,
                a sequence (assuming (yyyy, mm, dd, ...)) or an object having
                callable ``ticks`` field.

        """
        self.signature = signature
        self.fields = []
        self.mapNameToIndex = {}
        if fields is not None:
#            self.fields = list(fields)
            self.addField(*list(fields))
        self.lastUpdate = getDate(lastUpdate)
        self.recordLength = recordLength
        self.headerLength = headerLength
        self.recordCount = recordCount
        # XXX: I'm not sure this is safe to
        # initialize `self.changed` in this way
        self.changed = bool(self.fields)
        self.encoding = encoding
        self.enableFieldNameDups = enableFieldNameDups

    @classmethod
    def fromString(cls, string, enableFieldNameDups=False):
        """Return header instance from the string object."""
        return cls.fromStream(cStringIO.StringIO(str(string)), enableFieldNameDups=enableFieldNameDups)
#    fromString = classmethod(fromString)

    @classmethod
    def fromStream(cls, stream, encoding=None, enableFieldNameDups=False):
        """Return header object from the stream."""
        stream.seek(0)
        _data = stream.read(32)
        (_cnt, _hdrLen, _recLen) = struct.unpack("<I2H", _data[4:12])
        #reserved = _data[12:32]
        ## create header object
        _obj = cls(None, _hdrLen, _recLen, _cnt, ord(_data[0]),
            (1900 + ord(_data[1]), ord(_data[2]), ord(_data[3])), encoding=encoding, enableFieldNameDups=enableFieldNameDups)

        ## append field definitions
        # position 0 is for the deletion flag
        _pos = 1
        _data = stream.read(1)
        while _data[0] != "\x0D":
            _data += stream.read(31)
            _fld = fields.lookupFor(_data[11]).fromString(_data, _pos, encoding=encoding)
            _obj._addField(_fld)
            _pos = _fld.end
            _data = stream.read(1)
        return _obj
#    fromStream = classmethod(fromStream)

    ## properties

    year = property(lambda self: self.lastUpdate.year)
    month = property(lambda self: self.lastUpdate.month)
    day = property(lambda self: self.lastUpdate.day)

    ## object representation

    def __repr__(self):
        _rv = """\
Version (signature): 0x%02x
        Last update: %s
      Header length: %d
      Record length: %d
       Record count: %d
 FieldName Type Len Dec
""" % (self.signature, self.lastUpdate, self.headerLength,
            self.recordLength, self.recordCount)
        _rv += "\n".join(
            ["%10s %4s %3s %3s" % _fld.fieldInfo() for _fld in self.fields]
        )
        return _rv

    ## internal methods

    def _addField(self, *defs):
        """Internal variant of the `addField` method.

        This method doesn't set `self.changed` field to True.

        Return value is a length of the appended records.
        Note: this method doesn't modify ``recordLength`` and
        ``headerLength`` fields. Use `addField` instead of this
        method if you don't exactly know what you're doing.

        """
        _recordLength = 0
        for _def in defs:
            if isinstance(_def, fields.DbfFieldDef):
                _obj = _def
            else:
                (_name, _type, _len, _dec, _encoding) = (tuple(_def) + (None,) * 5)[:5]
                _cls = fields.lookupFor(_type)
                _obj = _cls(_name, _len, _dec, _encoding)
            _recordLength += _obj.length
            if _obj.encoding is None:
                _obj.encoding = self.encoding
            if isinstance(_obj, fields.DbfMemoFieldDef):
                self.signature |= 0x80
            if _obj.name in self.mapNameToIndex:
                if self.enableFieldNameDups:
                    index = self.mapNameToIndex[_obj.name]
                    if isinstance(index, int):
                        index = [index]
                    index.append(len(self.fields))
                else:
                    raise Exception, 'DBF field name "%s" duplicated' % _obj.name
            else:
                index = len(self.fields)
            self.mapNameToIndex[_obj.name] = index
            self.fields.append(_obj)
        return _recordLength

    ## interface methods
    def indexOfFieldName(self, name):
        """Index of field named ``name``."""
        return self.mapNameToIndex[name.upper()]


    def addField(self, *defs):
        """Add field definition to the header.

        Examples:
            dbfh.addField(
                ("name", "C", 20),
                dbf.DbfCharacterFieldDef("surname", 20),
                dbf.DbfDateFieldDef("birthdate"),
                ("member", "L"),
            )
            dbfh.addField(("price", "N", 5, 2))
            dbfh.addField(dbf.DbfNumericFieldDef("origprice", 5, 2))

        """
        _oldLen = self.recordLength
        self.recordLength += self._addField(*defs)
        if not _oldLen:
            self.recordLength += 1
            # XXX: may be just use:
            # self.recordeLength += self._addField(*defs) + bool(not _oldLen)
        # recalculate headerLength
        self.headerLength = 32 + (32 * len(self.fields)) + 1
        self.changed = True

    def write(self, stream):
        """Encode and write header to the stream."""
        stream.seek(0)
        stream.write(self.toString())
        stream.write("".join([_fld.toString() for _fld in self.fields]))
        stream.write(chr(0x0D))   # cr at end of all hdr data
        self.changed = False

    def toString(self):
        """Returned 32 chars length string with encoded header."""
        return struct.pack("<4BI2H",
            self.signature,
            self.year - 1900,
            self.month,
            self.day,
            self.recordCount,
            self.headerLength,
            self.recordLength) + "\0" * 20

    def setCurrentDate(self):
        """Update ``self.lastUpdate`` field with current date value."""
        self.lastUpdate = datetime.date.today()

# vim: et sts=4 sw=4 :
