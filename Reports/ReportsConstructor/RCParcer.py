# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.Utils import forceString, forceBool

import re

class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)

class CRCParcer(object):
    def __init__(self,  parent):
        object.__init__(self)
        self._parent = parent

    def parce(self, text):
        """
        Spliting complex expressions to simple expressions with links to other simple expressions

        :param text :type str or unicode - input string
        :return tuple(dict, text):
            dict :type dictionary - cascade dictionary with splited expressions
            text :type unicode
        :example
            text = u'$Sum({a}*({b}-{c})) * ({a} + {b})'
            :return
                dict {
                    u'{0}': u'({b}-{c})',
                    u'{1}': u'({a}*{0})',
                    u'{2}': u'$Sum{1}'
                    }
                text u'{2}'
        """
        #text = u'$Sum({a}*({b}-{c})) * ({a} + {b})'
        #text = u'({a}*({b}-{c})) * ({a} + {b})'
        #text = u'$If({a}, {b}, {c})'
        dict = {}
        counter = 0
        text = forceString(text)
        if len(re.findall('\(', text)) - len(re.findall('\)', text)) != 0:
            return {}, u''
        patterns = []
        patterns.append(re.compile("\([\$a-zA-z0-9 /\+\*\-=><\{\}]+\)")) # '(a + b)' '({a} - {b})' '({1})' - simple expression in brackets
        patterns.append(re.compile("\$\w+\{\d+\}")) # '$Sum{1}' functions
        patterns.append(re.compile("\{\w+\}[ \+\*\-/=<>!]+\{\w+\}")) # '{1} +|-|*|/ {2}' - math expression
        patterns.append(re.compile("""['"]\d+['"]""")) # '|"10'|" number with quotes
        patterns.append(re.compile("""\$\w+\(\{\w+\}(,\{\w+\})+\)"""))

        while re.search('[\(\)\$\+\-\*/,]', text):
            for pattern in patterns:
                match = re.search(pattern, text)
                while match:
                    substr = match.group()
                    key = u'{%d}' %counter
                    text = text.replace(substr, key)
                    dict[key] = substr
                    counter += 1
                    match = re.search(pattern, text)
        return dict, text

    def forceInt(self, val):
        """
        Convert val to integer if it is possible
            else convert to float if it is possible
            else return 0
        :param val
        :return integer, float or 0
        """
        if val == None:
            return 0
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except:
                return 0

    def getData(self, key, data, func=None):
        if func == None:
            func = self.forceInt
        value = None
        if re.search('\{\d+\}', key):
            value = [func(val) for val in data.get(key, [])]
        elif re.search('\{\w+\}', key):
            value = [func(val) for val in data.get(key[1:-1], [])]
        return value

    def count(self, dict, startKey, data, group=False):
        """
        Count expressions in dict with data from data
        :param
            dict :type dictionary - cascade dictionary with splited expressions
            startKey :type unicode - key of dict to start count
            data :type dictionary - data
            group :type boolean
        :return
            integer or float
        """
        expr = dict.get(startKey, u'')
        dataLength = len(data.values()[0]) if data else 0
        for subExpr in re.findall('\{\d+\}', expr):
            value = self.count(dict, subExpr, data, group=group or forceBool(re.search('\$\w+', expr)))
            if not isinstance(value, list):
                value = [value]
            data[subExpr] = value

        expr = expr.replace(' ', '')

        #function with one arg $SUM({2})
        if re.search('(\$[\w]+)(\{\d+\})', expr):
            nodeList = re.search('(\$[\w]+)(\{\d+\})', expr).groups()
            func = nodeList[0].upper()
            value = nodeList[1]
            values = [self.forceInt(val) for val in data.get(value, [])]
            if func == u'$SUM':
                return sum(values)
            elif func == u'$COUNT':
                return len(values)
            elif func == u'$MULTI':
                result = 1
                for val in values:
                    result *= val
                return result

        #function with mnay args $if({1}, {2}, {3})
        if re.search("\$\w+\(\{\w+\}(,\{\w+\})+\)", expr):
            func = re.search("\$\w+", expr).group()
            if func == '$IF':
                cond, ifTrue, ifFalse = re.findall("\{\w+\}", expr)
                cond = self.getData(cond, data)
                ifTrue = self.getData(ifTrue, data)
                ifFalse = self.getData(ifFalse, data)
                if group:
                    return [ifTrue[idx] if cond[idx] else ifFalse[idx] for idx in range(dataLength)]
                return ifTrue[0] if cond[0] else ifFalse[0]

        # number in quotes '12'
        if re.search("""['"]\d+['"]""", expr):
            value = self.forceInt(expr[1:-1])
            if group:
                return [value for idx in range(dataLength)]
            return value

        # brackets ({name})|({11})
        if re.search('(\(\{\w+\}\))', expr):
            nodeList = re.search('(\(\{\w+\}\))', expr).groups()
            value = self.getData(nodeList[0][1:-1], data)
            return value

        # math operations
        if re.search('(\{\w+\})([\-\*\+/=<>!]+)(\{\w+\})', expr):
            nodeList = re.search('(\{\w+\})([\-\*\+/=<>!]+)(\{\w+\})', expr).groups()
            value1 = self.getData(nodeList[0], data)
            value2 = self.getData(nodeList[2], data)

            if nodeList[1] == u'*':
                if group:
                    return [value1[idx] * value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] * value2[0]
            elif nodeList[1] == u'+':
                if group:
                    return [value1[idx] + value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] + value2[0]
            elif nodeList[1] == u'-':
                if group:
                    return [value1[idx] - value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] - value2[0]
            elif nodeList[1] == u'/':
                if group:
                    return [value1[idx] / value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] / value2[0]
            elif nodeList[1] == u'=':
                if group:
                    return [value1[idx] == value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] == value2[0]
            elif nodeList[1] == u'<':
                if group:
                    return [value1[idx] < value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] < value2[0]
            elif nodeList[1] == u'>':
                if group:
                    return [value1[idx] > value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] > value2[0]
            elif nodeList[1] == u'<=':
                if group:
                    return [value1[idx] <= value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] <= value2[0]
            elif nodeList[1] == u'=':
                if group:
                    return [value1[idx] >= value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] >= value2[0]
            elif nodeList[1] == u'!=':
                if group:
                    return [value1[idx] != value2[idx] for idx in range(dataLength)]
                else:
                    return value1[0] != value2[0]



