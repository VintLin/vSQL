import pymysql

CREATE = "CREATE TABLE IF NOT EXISTS {} ({})"
INSERT = """INSERT INTO {}({}) VALUES ({})"""
SELECT = "SELECT * FROM {} {}"
DROP = "DROP TABLE IF EXISTS {}"
SHOWTABLE = "SHOW TABLES LIKE '{}'"
SHOWDATA = "SHOW DATABASES LIKE '{}'"

HOST = 'localhost'
USER = 'root'
PWD = '123456'
DB = 'text'


def create_all_table():
    print('VSQL : THIS CREATE ALL TABLE')
    print('This', Module.__subclasses__())
    for table in Module.tables():
        rows = ''
        if not isexists(table['table']):
            for k, v in table['rows'].items():
                rows = rows + k + ' ' + v + ', '
            sql = CREATE.format(table['table'], rows[:-2])
            execute(sql)


def isexists(table):
    sql = SHOWTABLE.format(table)
    result = execute_get_bool(sql)
    return result


def create(mod):
    table = mod.get_statement()['table']
    rows = ''
    for k, v in mod.get_statement()['rows'].items():
        rows = rows + k + ' ' + v + ', '
    sql = CREATE.format(table, rows[:-2])
    execute(sql)


def insert(mod):
    table = mod.table()
    keys = ''
    values = ''
    for k, v in mod.get_attr().items():
        if v is not None and len(v) is not 0:
            keys = keys + k + ', '
            values = values + cover(v, "'{}'") + ', '
    sql = INSERT.format(table, keys[:-2], values[:-2])
    execute(sql)


def select(mod, islike=False, oderby='', isasc=True, limit=0):
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
        if v is not None and len(v) is not 0:
            rule = rule + k + oper + cover(v, s) + ', '
            flag = True
    if flag:
        rule = rule[:-2]
    else:
        rule = ''
    if oderby:
        rule = rule + ' ORDER BY ' + oderby
        if isasc:
            rule = rule + ' ASC '
        else:
            rule = rule + ' DESC '
        if limit:
            rule = rule + 'LIMIT {}'.format(limit)
    sql = SELECT.format(table, rule)
    return execute_get(sql, mod.__class__)


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


def execute_get(sql, clazz):
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
        db.close()
        return items
    except IndexError:
        print("Error: unable to fetch data")
        # 关闭数据库连接
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

    def __init__(self):
        for k in self.rows():
            self.__setattr__(k, None)
        if Module.INIT and Module.__subclasses__():
            Module.INIT = False
            create_all_table()

    @staticmethod
    def tables():
        tables = []
        for clazz in Module.__subclasses__():
            tables.append(clazz().get_statement())

        return tables

    def get_statement(self):
        return {'table': self.table(), 'rows': self.rows()}

    def table(self):
        return self.__class__.__name__

    def rows(self):
        items = self.__class__.__dict__.items()
        rows = {}
        for r in items:
            if type(r[1]) is str and r[0][0] is not '_':
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

    def insert(self):
        insert(self)

    def select(self, islike=False, oderby='', isasc=True, limit=0):
        return select(self, islike, oderby, isasc, limit)

    def drop(self):
        return drop(self)

