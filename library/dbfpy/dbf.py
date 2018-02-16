#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""DBF accessing helpers.

FIXME: more documentation needed

Examples:

    Create new table, setup structure, add records:

        dbf = Dbf(filename, new=True)
        dbf.addField(
            ("NAME", "C", 15),
            ("SURNAME", "C", 25),
            ("INITIALS", "C", 10),
            ("BIRTHDATE", "D"),
        )
        for (n, s, i, b) in (
            ("John", "Miller", "YC", (1980, 10, 11)),
            ("Andy", "Larkin", "", (1980, 4, 11)),
        ):
            rec = dbf.newRecord()
            rec["NAME"] = n
            rec["SURNAME"] = s
            rec["INITIALS"] = i
            rec["BIRTHDATE"] = b
            rec.store()
        dbf.close()

    Open existed dbf, read some data:

        dbf = Dbf(filename, True)
        for rec in dbf:
            for fldName in dbf.fieldNames:
                print '%s:\t %s (%s)' % (fldName, rec[fldName],
                    type(rec[fldName]))
            print
        dbf.close()

"""
"""History (most recent first):
04-jul-2006 [als]   added export declaration
20-dec-2005 [yc]    removed fromStream and newDbf methods:
                    use argument of __init__ call must be used instead;
                    added class fields pointing to the header and
                    record classes.
17-dec-2005 [yc]    splitted to several modules; reimplemented
13-dec-2005 [yc]    adapted to the changes of the `strutil` module.
13-sep-2002 [als]   suppot FoxPro Timestamp datatype
15-nov-1999 [jjk]   documentation updates, add demo
24-aug-1998 [jjk]   add some encodeValue methods (not tested), other tweaks
08-jun-1998 [jjk]   fix problems, add more features
20-feb-1998 [jjk]   fix problems, add more features
19-feb-1998 [jjk]   add create/write capabilities
18-feb-1998 [jjk]   from dbfload.py
"""

__version__ = "$Revision: 1.6 $"[11:-2]
__date__ = "$Date: 2006/07/04 08:09:13 $"[7:-2]
__author__ = "Jeff Kunce <kuncej@mail.conservation.state.mo.us>"

__all__ = ["Dbf"]

import header
import record
import dbt

class Dbf(object):
    """DBF accessor.

    FIXME:
        docs and examples needed (dont' forget to tell
        about problems adding new fields on the fly)

    Implementation notes:
        ``_new`` field is used to indicate whether this is
        a new data table. `addField` could be used only for
        the new tables! If at least one record was appended
        to the table it's structure couldn't be changed.

    """

    __slots__ = "name", "header", "stream", "_changed", "_new", "_dbt", "_readOnly"

    HeaderClass = header.DbfHeader
    RecordClass = record.DbfRecord

    ## initialization and creation helpers

    def __init__(self, f, readOnly=False, new=False, encoding=None, enableFieldNameDups=False):
        """Initialize instance.

        Arguments:
            f:
                Filename or file-like object.
            new:
                True if new data table must be created. Assume
                data table exists if this argument is False.
            readOnly:
                if ``f`` argument is a string file will
                be opend in read-only mode; in other cases
                this argument is ignored. This argument is ignored
                even if ``new`` argument is True.
            headerObj:
                `header.DbfHeader` instance or None. If this argument
                is None, new empty header will be used with the
                all fields set by default.

        """
        if isinstance(f, basestring):
            # a filename
            self.name = f
            if new:
                # new table (table file must be
                # created or opened and truncated)
                self.stream = file(f, "w+b")
            else:
                # tabe file must exist
                self.stream = file(f, ("r+b", "rb")[bool(readOnly)])
        else:
            # a stream
            self.name = getattr(f, "name", "")
            self.stream = f
        if new:
            # if this is a new table, header will be empty
            self.header = self.HeaderClass(encoding=encoding, enableFieldNameDups=enableFieldNameDups)
        else:
            # or instantiated using stream
            self.header = self.HeaderClass.fromStream(self.stream, encoding=encoding, enableFieldNameDups=enableFieldNameDups)
        self._readOnly = bool(readOnly)
        self._new = bool(new)
        self._changed = False
        self._dbt = None

    ## properties

    closed = property(lambda self: self.stream.closed)
    recordCount = property(lambda self: self.header.recordCount)
    fieldNames = property(
        lambda self: [_fld.name for _fld in self.header.fields])
    fieldDefs = property(lambda self: self.header.fields)
    changed = property(lambda self: self._changed or self.header.changed)

    ## protected methods

    def _fixIndex(self, index):
        """Return fixed index.

        This method fails if index isn't a numeric object
        (long or int). Or index isn't in a valid range
        (less or equal to the number of records in the db).

        If ``index`` is a negative number, it will be
        treated as a negative indexes for list objects.

        Return:
            Return value is numeric object maning valid index.

        """
        if not isinstance(index, (int, long)):
            raise TypeError("Index must be a numeric object")
        if index < 0:
            # index from the right side
            # fix it to the left-side index
            index += len(self) + 1
        if index >= len(self):
            raise IndexError("Record index out of range")
        return index

    ## iterface methods

    def close(self):
        self.flush()
        self.stream.close()
        if self._dbt:
            self._dbt.close()

    def flush(self):
        """Flush data to the associated stream."""
        if self.changed:
            self.header.setCurrentDate()
            self.header.write(self.stream)
            self.stream.flush()
            self._changed = False

    def indexOfFieldName(self, name):
        """Index of field named ``name``."""
        return self.header.indexOfFieldName(name)

    def newRecord(self):
        """Return new record, which belong to this table."""
        return self.RecordClass(self)

    def append(self, record):
        """Append ``record`` to the database."""
        record.index = self.header.recordCount
        record._write()
        self.header.recordCount += 1
        self._changed = True
        self._new = False

    def addField(self, *defs):
        """Add field definitions.

        For more information see `header.DbfHeader.addField`.

        """
        if self._new:
            self.header.addField(*defs)
        else:
            raise TypeError("At least one record was added, "
                "structure can't be changed")

    def getDbt(self):
        if self._dbt is None:
            self._dbt = dbt.Dbt3(self.name, self._readOnly, self._new)
        return self._dbt

    def getDbtItem(self, idx):
        return self.getDbt().getItem(idx)

    def putDbtItem(self, raw):
        return self.getDbt().putItem(raw)


    ## 'magic' methods (representation and sequence interface)

    def __repr__(self):
        return "Dbf stream '%s'\n" % self.stream + repr(self.header)

    def __len__(self):
        """Return number of records."""
        return self.recordCount

    def __getitem__(self, index):
        """Return `DbfRecord` instance."""
        return self.RecordClass.fromStream(self, self._fixIndex(index))

    def __setitem__(self, index, record):
        """Write `DbfRecord` instance to the stream."""
        record.index = self._fixIndex(index)
        record._write()
        self._changed = True
        self._new = False

    #def __del__(self):
    #    """Flush stream upon deletion of the object."""
    #    self.flush()


class CDbf(Dbf):
    """ using:
     with CDbf('filename.dbf', 'r', encoding='cp866') as dbf:
        ...
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def demoRead(filename):
    _dbf = Dbf(filename, True)
    for _rec in _dbf:
        print
        print repr(_rec)
    _dbf.close()

def demoCreate(filename):
    _dbf = Dbf(filename, new=True)
    _dbf.addField(
        ("NAME", "C", 15),
        ("SURNAME", "C", 25),
        ("INITIALS", "C", 10),
        ("BIRTHDATE", "D"),
    )
    for (_n, _s, _i, _b) in (
        ("John", "Miller", "YC", (1981, 1, 2)),
        ("Andy", "Larkin", "AL", (1982, 3, 4)),
        ("Bill", "Clinth", "", (1983, 5, 6)),
        ("Bobb", "McNail", "", (1984, 7, 8)),
    ):
        _rec = _dbf.newRecord()
        _rec["NAME"] = _n
        _rec["SURNAME"] = _s
        _rec["INITIALS"] = _i
        _rec["BIRTHDATE"] = _b
        _rec.store()
    print repr(_dbf)
    _dbf.close()

if (__name__=='__main__'):
    import sys
    _name = len(sys.argv) > 1 and sys.argv[1] or "county.dbf"
    demoCreate(_name)
    demoRead(_name)

# vim: set et sw=4 sts=4 :
