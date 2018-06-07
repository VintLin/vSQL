def zbool(default=0):
    return 'TINYINT(1) DEFAULT {} '.format(default)


def zchar(size, default=''):
    return 'CHAR({}) {}'.format(size, cover(default))


def zvarchar(size, default=''):
    return 'VARCHAR({}) {}'.format(size, cover(default))


def zintger(size=20, isunsigned=False, default=''):
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


def ztext(default=''):
    return 'TEXT {}'.format(cover(default))


def cover(s):
    if type(s) is int:
        s = 'DEFAULT ' + str(s)
    elif len(s) is not 0:
        s = 'DEFAULT ' + s
    else:
        s = ''
    return s


class column:
    def __init__(self, type, isPrimary=False, isAutocount=False, isUnique=False, isNotnull=False):
        col = ''
        if isNotnull:
            col = col + ' NOT NULL'
        if isUnique:
            col = col + ' UNIQUE'
        if isAutocount:
            col = col + ' AUTO_INCREMENT'
        if isPrimary:
            col = col + ' PRIMARY KEY'
        self.col = col
        self.type = type


class foreign:
    def __init__(self, key, table, foreignkey, keyname=''):
        if keyname:
            self.col = "KEY '{0}'('{1}'), CONSTRAINT '{0}' FOREIGN KEY  ('{1}')  REFERENCES  '{2}' ('{3}')".\
                format(keyname, key, table, foreignkey)
        else:
            self.col = "FOREIGN KEY({}) REFERENCES {}({})".format(key, table, foreignkey)