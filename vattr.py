def zchar(size, default=''):
    return 'CHAR({}) {}'.format(size, cover(default))


def zvarchar(size, default=''):
    return 'VARCHAR({}) {}'.format(size, cover(default))


def zintger(size, isunsigned=False, default=''):
    if isunsigned:
        unsigned = 'UNSIGNED'
    else:
        unsigned = ''
    return 'INTEGER({}) {} {}'.format(size, unsigned, cover(default))


def zdouble(size_M, size_D, isunsigmed=False, default=''):
    if isunsigmed:
        unsigned = 'UNSIGNED'
    else:
        unsigned = ''
    return 'DOUBLE({}, {}) {} {}'.format(size_M, size_D, unsigned, cover(default))


def zdatetime(default=''):
    return 'DATETIME {}'.format(cover(default))


def zdate(default=''):
    return 'DATE {}'.format(cover(default))


def ztime(default=''):
    return 'DATE {}'.format(cover(default))


def cover(s):
    if len(s) is not 0:
        s = 'DEFAULT ' + s
    else:
        s = ''
    return s


def column(type, isPrimary=False, isAutocount=False, isUnique=False, isNotnull=False):
    col = type
    if isNotnull:
        col = col + ' NOT NULL'
    if isUnique:
        col = col + ' UNIGUE'
    if isAutocount:
        col = col + ' AUTO_INCREMENT'
    if isPrimary:
        col = col + ' PRIMARY KEY'

    return col
