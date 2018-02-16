PY_STRING_BEGIN = "\#!/usr/bin/env python\n\# -*- coding: utf-8 -*-\n\nCONTENT = u\"\"\"\n"
PY_STRING_END = "\"\"\""

all: temperatureList_html.py

%_html.py: %.html
	echo $(PY_STRING_BEGIN) > $@
	cat $< >> $@
	echo $(PY_STRING_END) >> $@