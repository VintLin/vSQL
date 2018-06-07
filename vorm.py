from datetime import datetime, timedelta

import pymysql
import json

with open(__file__[:-8] + '/db.json', 'r', encoding='utf-8') as f:
    json_dict = json.loads(f.read())

CREATE = "CREATE TABLE IF NOT EXISTS {} ({})"
INSERT = "INSERT INTO {}({}) VALUES ({})"
UPDATE = "UPDATE {} SET {} WHERE id = {}"
DELETE = "DELETE FROM {} {}"
SELECT = "SELECT * FROM {} {}"
SELECTANDCOUNT = "SELECT SQL_CALC_FOUND_ROWS  * FROM {} {}"
DROP = "DROP TABLE IF EXISTS {}"
SHOWTABLE = "SHOW TABLES LIKE '{}'"
SHOWDATA = "SHOW DATABASES LIKE '{}'"

HOUR_DIFF = "HOUR(timediff(now(), {})) AS {}"
MINUTE_DIFF = "MINUTE(timediff(now(), {})) AS {}"
SECOND_DIFF = "SECOND(timediff(now(), {})) AS {}"
DAY_DIFF = "DAY(timediff(now(), {})) AS {}"

HOST = json_dict['HOST']
USER = json_dict['USER']
PWD = json_dict['PWD']
DB = json_dict['DB']


class Period:
    TIMESTAMP = "{} BETWEEN '{}' AND '{}'"

    def __init__(self, field, time_slot, moment):
        if time_slot[0] is '+':
            self.oper = True
        else:
            self.oper = False
        self.field = field
        self.moment = self.__get_moment(moment)
        self.segment = self.__get_segment(time_slot[1:])
        if self.oper:
            self.other_moment = self.moment + self.segment
        else:
            self.other_moment = self.moment - self.segment

    def __get_moment(self, moment):
        if moment.upper().__eq__('NOW'):
            moment = datetime.now()
        else:
            moment = datetime.strptime(moment, "%Y-%m-%d %H:%M:%S")
        return moment

    def __get_segment(self, time_slot):
        time = time_slot.split(':')
        for i in range(len(time)):
            time[i] = int(time[i])
            delta = None
        if len(time) is 1:
            delta = timedelta(seconds=time[-1])
        elif len(time) is 2:
            delta = timedelta(seconds=time[-1], minutes=time[-2])
        elif len(time) is 3:
            delta = timedelta(seconds=time[-1], minutes=time[-2], hours=time[-3])
        elif len(time) is 4:
            delta = timedelta(seconds=time[-1], minutes=time[-2], hours=time[-3], days=time[-4])
        return delta

    def get_sql(self):
        if self.oper:
            sql = Period.TIMESTAMP.format(self.field, self.moment, self.other_moment)
        else:
            sql = Period.TIMESTAMP.format(self.field, self.other_moment, self.moment)
        return sql


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
        if v is not None:
            keys = keys + k + ', '
            values = values + cover(v, "'{}'") + ', '
    sql = INSERT.format(table, keys[:-2], values[:-2])
    execute(sql)


def update(mod):
    table = mod.table()
    rows = ''
    num = 0
    for k, v in mod.get_attr().items():
        if k.upper() == 'ID' and v is not None:
            num = v
        elif v is not None:
            rows = rows + k + '=' + cover(v, "'{}'") + ', '
    sql = UPDATE.format(table, rows[:-2], num)
    execute(sql)


def delete(mod, islike=False):
    table = mod.table()
    if islike:
        oper = ' like '
        s = "'%{}%'"
    else:
        oper = ' = '
        s = "'{}'"
    rule = 'WHERE '
    flag = False
    if isinstance(mod.period, Period):
        rule = rule + mod.period.get_sql() + ' and '
        flag = True

    for k, v in mod.get_attr().items():
        if v is not None:
            rule = rule + k + oper + cover(v, s) + ' and '
            flag = True
    if flag:
        rule = rule[:-4]
    else:
        rule = ''
    sql = DELETE.format(table, rule)
    execute(sql)


def select(mod, islike=False, oderby='', isasc=True, limit=0, getone=False):
    table = mod.table()
    if islike:
        oper = ' like '
        s = "'%{}%'"
    else:
        oper = ' = '
        s = "'{}'"
    rule = 'WHERE '
    flag = False
    if mod.period:
        rule = rule + mod.period.get_sql() + ' and '
        flag = True

    if mod.no_field:
        rule = rule + mod.no_field
        flag = True

    for k, v in mod.get_attr().items():
        if v is not None:
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
            rule = rule + 'LIMIT {}'.format(limit)
        if mod.pagination:
            limit = mod.pagination.get_limit()
            rule = rule + 'LIMIT {}, {}'.format(limit[0], limit[1])
    if mod.pagination:
        sql = SELECTANDCOUNT.format(table, rule)
    else:
        sql = SELECT.format(table, rule)
    if getone:
        return execute_get_one(sql, mod)
    else:
        return execute_get(sql, mod.__class__, pagination=mod.pagination)


def drop(mod):
    table = mod.table()
    sql = DROP.format(table)
    execute(sql)


def cover(attr, s):
    if isinstance(attr, str) or isinstance(attr, datetime):
        return s.format(attr)
    else:
        return str(attr)


def execute(sql):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
    except TypeError:
        print('ERROR: unable to connect')
        db.rollback()
        db.close()


def execute_get(sql, clazz, pagination=None):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        items = []
        for rows in results:
            mod = clazz()
            mod.set_attr(list(rows))
            items.append(mod)
        if pagination:
            cursor.execute('SELECT FOUND_ROWS()')
            count = cursor.fetchall()[0][0]
            pagination.item_count = count
            pagination.items = items
            pagination.set_default()
            return pagination
        else:
            return items
    except IndexError:
        print("Error: unable to fetch data")
    finally:
        db.close()


def execute_get_one(sql, mod):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            mod.set_attr(list(results[0]))
        return mod
    except IndexError:
        print("Error: unable to fetch data")
    finally:
        db.close()


def execute_get_bool(sql):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            results = results[0][0]
        else:
            results = None
        return results
    except TypeError:
        print("Error: unable to fetch data")
    finally:
        db.close()


class Pagination:
    def __init__(self, page, paging):
        self.page = page            # now page
        self.paging = paging        # one page items count
        self.item_count = None      # all page items count
        self.items = None           # all items
        self.pages = None
        self.hasPrev = None
        self.hasNext = None
        self.hasItem = None

    def get_limit(self):
        return [(self.page - 1) * self.paging, self.paging]

    def set_default(self):
        self.pages = self.item_count // self.paging + 1
        self.hasPrev = self.page is not 1
        self.hasNext = self.page is not self.pages
        self.hasItem = self.item_count


class ValueOfvSQLError(Exception):
    def __init__(self, arg):
        self.args = arg

    
class Module:
    INIT = True
    M_SELECT = 1
    M_INSERT = 2
    M_UPDATE = 3
    M_DELETE = 4
    M_DROP = 5

    def __init__(self, **args):
        self.pagination = None
        self.period = None
        self.no_field = None
        for k in self.rows():
            v = args.get(k)
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
            if params or isinstance(params, int) or isinstance(params, bool):
                self.__setattr__(row, params.pop(0))

    def get_attr(self):
        attr = {}
        for k in self.rows():
            attr[k] = self.__getattribute__(k)
        return attr

    def __str__(self):
        for k in self.rows():
            v = self.__getattribute__(k)

    def set_pagination(self, page, paging):
        self.pagination = Pagination(paging=paging, page=page)
        return self

    def set_period(self, field, time_slot, moment="now"):
        self.period = Period(field, time_slot, moment)
        return self

    def set_no_field(self, **args):
        field = ''
        for k, v in args:
            field = field + k + '!=' + cover(v, "'{}'") + ' and '
        self.no_field = field
        return self

    def isexists(self):
        return isexists(self.table()) is not None

    def create(self):
        create(self)

    def insert(self):
        self.listener_begin(do=Module.M_INSERT)
        insert(self)
        item = select(self, getone=True)
        self.listener_end(do=Module.M_INSERT)
        return item

    def insert_without_return(self):
        insert(self)

    def update(self):
        self.listener_begin(do=Module.M_UPDATE)
        update(self)
        item = select(self, getone=True)
        self.listener_end(do=Module.M_UPDATE)
        return item

    def delete(self, islike=False):
        self.listener_begin(do=Module.M_DELETE)
        delete(self, islike=islike)
        self.listener_end(do=Module.M_DELETE)

    def select(self, islike=False, oderby='', isasc=True, limit=0, getone=False):
        self.listener_begin(do=Module.M_SELECT)
        items = select(self, islike=islike, oderby=oderby, isasc=isasc, limit=limit, getone=getone)
        self.listener_end(do=Module.M_SELECT)
        return items

    def drop(self):
        return drop(self)

    def listener_begin(self, do): pass

    def listener_end(self, do): pass