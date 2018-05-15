import pymysql
from . import js

CREATE = "CREATE TABLE IF NOT EXISTS {} ({})"
INSERT = "INSERT INTO {}({}) VALUES ({})"
UPDATE = "UPDATE {} SET {} WHERE id = {}"
SELECT = "SELECT * FROM {} {}"
SELECTANDCOUNT = "SELECT SQL_CALC_FOUND_ROWS  * FROM {} {}"
DROP = "DROP TABLE IF EXISTS {}"
SHOWTABLE = "SHOW TABLES LIKE '{}'"
SHOWDATA = "SHOW DATABASES LIKE '{}'"

HOST = js['DB']
USER = js['USER']
PWD = js['PWD']
DB = js['DB']


def create_all_table():
    for table in Module.get_tables():
        rows = ''
        role = ''
        if not isexists(table['table']):
            for k, v in table['rows'].items():
                if v.__class__.__name__ == 'column':
                    rows = '{} {} {}, '.format(rows + k, v.type, v.col)
                if v.__class__.__name__ == 'foreign':
                    role = '{} {}, '.format(role, v.col)
            if role:
                rows = rows + role
            sql = CREATE.format(table['table'], rows[:-2])
            execute(sql)


def isexists(table):
    sql = SHOWTABLE.format(table)
    result = execute_get_bool(sql)
    return result


def create(mod):
    table = mod.get_sql()['table']
    rows = ''
    for k, v in mod.get_sql()['rows'].items():
        rows = rows + k + ' ' + v + ', '
    sql = CREATE.format(table, rows[:-2])
    execute(sql)


def insert(mod):
    table = mod.table()
    keys = ''
    values = ''
    for k, v in mod.get_attr().items():
        print(k, v)
        if v:
            keys = keys + k + ', '
            values = values + cover(v, "'{}'") + ', '
    sql = INSERT.format(table, keys[:-2], values[:-2])
    execute(sql)


def update(mod):
    table = mod.table()
    rows = ''
    num = 0
    for k, v in mod.get_attr().items():
        if k.upper() == 'ID' and v:
            num = v
        elif v:
            rows = rows + k + '=' + cover(v, "'{}'") + ', '
    sql = UPDATE.format(table, rows[:-2], num)
    execute(sql)
    

def select(mod, islike=False, oderby='', isasc=True, limit=0, iscount=False, getone=False):
    table = mod.table()
    if islike:
        oper = ' like '
        s = "'%{}%'"
    else:
        oper = ' = '
        s = "'{}'"
    rule = 'WHERE '
    flag = False
    for k, v in mod.get_attr().items():
        if v:
            rule = rule + k + oper + cover(v, s) + ' and '
            flag = True
    if flag:
        rule = rule[:-4]
    else:
        rule = ''
    if oderby:
        rule = rule + ' ORDER BY ' + oderby
        if isasc:
            rule = rule + ' ASC '
        else:
            rule = rule + ' DESC '
        if limit:
            if type(limit) is list:
                rule = rule + 'LIMIT {}, {}'.format(limit[0], limit[1])
            else:
                rule = rule + 'LIMIT {}'.format(limit)
    if iscount:
        sql = SELECTANDCOUNT.format(table, rule)
    else:
        sql = SELECT.format(table, rule)
    if getone:
        return execute_get_one(sql, mod)
    else:
        return execute_get(sql, mod.__class__, iscount=iscount)


def drop(mod):
    table = mod.table()
    sql = DROP.format(table)
    execute(sql)


def cover(attr, s):
    if type(attr) is str:
        return s.format(attr)
    else:
        return str(attr)


def execute(sql):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 查询语句
    try:
        # 执行SQL语句
        print(sql)
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        db.close()
    except TypeError:
        print('ERROR: unable to connect')
        # 如果发生错误则回滚
        db.rollback()
        # 关闭数据库连接
        db.close()


def execute_get(sql, clazz, iscount=False):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    # SQL 查询语句
    # sql = "SELECT * FROM EMPLOYEE WHERE INCOME > '%d'" % (1000)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        items = []
        for rows in results:
            mod = clazz()
            mod.set_attr(list(rows))
            items.append(mod)
            # 打印结果
        if iscount:
            cursor.execute('SELECT FOUND_ROWS()')
            count = cursor.fetchall()[0][0]
            return [items, count]
        else:
            return items
    except IndexError:
        print("Error: unable to fetch data")
        # 关闭数据库连接
    finally:
        db.close()


def execute_get_one(sql, mod):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        print(sql)
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        if results:
            mod.set_attr(list(results[0]))
            # 打印结果
        return mod
    except IndexError:
        print("Error: unable to fetch data")
        # 关闭数据库连接
    finally:
        db.close()


def execute_get_bool(sql):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    # SQL 查询语句
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        if results:
            results = results[0][0]
        else:
            results = None
        return results
    except TypeError:
        print("Error: unable to fetch data")
        # 关闭数据库连接
    finally:
        db.close()


class Module:
    INIT = True

    def __init__(self, **args):
        for k in self.rows():
            v = args.get(k)
            if not v:
                v = None
            self.__setattr__(k, v)

        if Module.INIT and Module.__subclasses__():
            Module.INIT = False
            create_all_table()

    @staticmethod
    def get_tables():
        tables = []
        for clazz in Module.__subclasses__():
            tables.append(clazz().get_sql())
        return tables

    def get_sql(self):
        return {'table': self.table(), 'rows': self.rows()}

    def table(self):
        return self.__class__.__name__

    def rows(self):
        rows = {}
        for r in self.__class__.__dict__.items():
            if (r[1].__class__.__name__ is 'column' or r[1].__class__.__name__ is 'foreign') \
                    and r[0][0] is not '_':
                rows[r[0]] = r[1]
        return rows

    def set_attr(self, params):
        for row in self.rows().keys():
            self.__setattr__(row, params.pop(0))

    def get_attr(self):
        attr = {}
        for k in self.rows():
            attr[k] = self.__getattribute__(k)
        return attr

    def isexists(self):
        return isexists(self.table()) is not None

    def create(self):
        create(self)

    def insert(self, getback=False):
        if getback:
            insert(self)
            select(self, getone=True)
        else:
            insert(self)

    def update(self, getback=False):
        if getback:
            update(self)
            select(self, getone=True)
        else:
            update(self)

    def select(self, islike=False, oderby='', isasc=True, limit=0, iscount=False, getone=False):
        return select(self, islike=islike, oderby=oderby, isasc=isasc, limit=limit, iscount=iscount, getone=getone)

    def drop(self):
        return drop(self)

