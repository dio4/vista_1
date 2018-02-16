PY_STRING_BEGIN = "\#!/usr/bin/env python\n\# -*- coding: utf-8 -*-\n\nCOMMAND = u\"\"\"\n"
PY_STRING_END = "\"\"\""

all: updateSMO_sql.py updateLPU_sql.py importServices_create_sql.py importServices_sql.py importServices_deltemp_sql.py importServicesMes_sql.py 

%_sql.py: %.sql
	echo $(PY_STRING_BEGIN) > $@
	cat $< >> $@
	echo $(PY_STRING_END) >> $@