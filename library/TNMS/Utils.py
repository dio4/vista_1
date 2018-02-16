# -*- coding: utf-8 -*-
prefixes = ['c', 'p', 'r', 'y', 'yc', 'yp', 'a']
categories = ['T', 'N', 'M', 'M1Loc', 'S', 'G', 'L', 'V', 'Pn', 'R', 'St']


def isThis(entry, key):
    if not entry.startswith(key):
        return False
    if key == 'M' and 'Loc' in entry:
        return False
    return True


def convertTNMSStringToDict(s):
    result = {}
    entries = s.split(' ')
    for prefix in prefixes:
        for category in categories:
            key = prefix + category
            for entry in entries:
                if isThis(entry, key):
                    result[key] = entry[len(key):]
                    break
    return result


def convertTNMSDictToString(d):
    l = []

    for prefix in prefixes:
        for param in categories:
            key = prefix + param
            value = d.get(key, '--')
            l.append(key + value)

    return ' '.join(l)


def showThisValue(d, prefix, param, value):
    if value == '--':
        return False
    if param == 'M1Loc' and d.get(prefix + 'M', '--') != '1':
        return False
    if param == 'St' and value == '0' and (prefix not in ['c', 'p']):
        show = False
        for cat in categories:
            if cat != 'St' and d.get(prefix + cat, '--') != '--':
                if cat == 'M1Loc' and d.get(prefix + 'M', '--') != '1':
                    continue
                show = True
                break
        return show
    return True


def convertTNMSDictToDigest(d):
    parts = {}
    for param in categories:
        for prefix in prefixes:
            key = prefix + param
            value = d.get(key, '--')
            if showThisValue(d, prefix, param, value):
                parts.setdefault(prefix, []).append(param + value)
    return ' '.join('%s(%s)' % (param, ' '.join(parts[param])) if parts[param] else ''
                    for param in sorted(parts.keys())
                    )
