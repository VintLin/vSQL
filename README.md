# vSQL
## Version : v011
基于pymysql的关系映射型数据库框架
[![vSQL](https://github.com/VoterLin/vSQL)](https://github.com/VoterLin/vSQL/)
[![Python3.7](https://www.mysql.com)](https://pypi.python.org/pypi/pubnub/)
[![MySQL](https://www.python.org)](https://www.python.org)

## 项目结构：

##### vSQL
###### |-__init__.py
###### |- vattr.py
###### |- vorm.py
###### |_ db.json 打开此文件，在对应位置输入值(host,user,password,database)。


## 如何使用：
### 0.导入包：
  将vSQL放入到项目包中。
  导入vSQL包
  例:创建Model.py文件
```python
from vSQL.vorm import Module
from vSQL.vattr import *
```
### 1.创建
####  根据你想要创建的表名和列名创建相应的类(使该类继承vorm中的Module类)和类属性。
####  例如:(同样在Model.py)
```python
# 创建一个名为News的表(table)
class News(Module):
    id = column(zintger(20), isAutocount=True, isPrimary=True, isNotnull=True)
    name = column(zchar(20), isNotnull=True)
    # 分别创建id，name两个列
```
#### （注意，要想编写__init__构造函数，请务必调用super().__init__()，否则会报错）
  当创建如上述代码中的类时。
  等效于SQL语句中的：
```sql
CREATE TABLE IF NOT EXISTS News(id INTEGER(20) AUTO_INCREMENT PRIMARY KEY NOT NULL, name CHAR(20) NOT NULL)
```
  之后程序就会自动帮你创建出该表与其列。
### 2.插入
  创建Test.py文件
```python
from Model import *
# 从Model.py中导入
def main():
    News(name='VoterLin').insert()
    # insert() 方法中可设置参数getback为True，
    news = News(name='VoterLin').insert(getback)
    id = news.id
    # 由于id被AUTO_INCREMENT约束，在数据插入时，将会自动生成。
    # 此时需要获得插入后生成的id时。就可以用getback参数。
```
  等效于SQL语句中的：
```sql
INSERT INTO News (id, name) VALUES (123456, 'VoterLin')
```
### 查找
```python
def main()
    # 获取对应的查询结果(数组)
    newsList = News(id=123456).select()
    # 获取第一个查询结果(News实例)
    news = News(id=123456).select(getone=True)
    # 只需在select方法中定义getone为True就行
```
  等效于SQL语句中的：
```sql
SELECT * FROM News WHERE id = 123456
```
  也可以不赋值
```python
    newsList = News().select()
```
  等效于SQL语句中的：
```sql
SELECT * FROM News
```
  其返回值newsList的是包含查找结果的数组，其中每一项是一个News类型。
  打印newsList的结果:
```python
    for news in newsList：
        print(news.id, news.name)
```
#### 除了上述方法以外还可以添加其他的约束条件：
```python
    news = News()
    news.name = 'Lin'
    newsList = news.select(oderby='id', isasc=True, limit=5)
```
  等效于SQL语句中的：
```sql
SELECT * FROM News WHERE name = 'Lin' ODER BY id ASC LIMIT 5
```
## 详细
  由上述已知vSQL的基本操作。接下来是详细内容
### 1.column类
  还是这个例子:
```python
class News(Module):
    id = column(zintger(20), isAutocount=True, isPrimary=True, isNotnull=True)
    name = column(zchar(20), isNotnull=True)
```
  其中给列赋值的column是一个类。
  column类的构造方法中可以传入以下参数:

```python
    参数        参数类型      默认值       对应sql
    type        method      None        CHAR / VARCHAR / INTEGER / DOUBLE / DATETIME / DATE / TIME
    isPrimary   bool        False       PRIMARY KEY
    isAutocount bool        False       AUTO_INCREMENT
    isNotnull   bool        False       NOT NULL
```
  按上述参数全部赋值就是下面这样:
```python
    col = column(zchar(20), isPrimary=True, isAutocount=True, isNotnull=True)
```
  等效于SQL语句中的：
```sql
    col CHAR(20) AUTO_INCREMENT PRIMARY KEY NOT NULL
```
#### column中的type参数
  按之前的代码应该可以大致知道，type就对应SQL语句中相应的类型(如 CHAR / VARCHAR / INTEGER 等等...)。
  我在vSQL中现在只编写了一小部分类型。
```python
    type        必传入参数      可传入参数                    对应sql
    zbool()                     default                     TINYINT
    zchar()     size            default                     CHAR
    zvarchar()  size            default                     VARCHAR
    zintger()                   size/default/isunsigned     INTGER
    zdouble()   size_M/size_D   default/isunsigned          DOUBLE
    zdatetime()                 default                     DATETIME
    zdate()                     default                     DATE
    ztime()                     default                     TIME
    # 赋值给default，等于给该类型一个
    # 赋值给isunsigned，是设 整形/浮点型 为无符号
```
### 2.Module类
  通过上述代码知道继承Module后，就在可以相应的在MySQL数据库中创建表与列。
  并且拥有了 select/insert 等方法
  下面是继承Module类后可以调用的方法，详解:
```python
    可调用方法       参数
    insert()        getback
    update()        getback
    select()        islike/oderby/isasc/limit/iscount/getone
    create()        无(子类调用时，创建相应的表，一般是不需要调用此方法的，可以与drop()配合使用)
    drop()          无(子类调用时，删除相应的表)
    isexists()      无(子类调用时，判断相应的表是否存在，与前两个方法配合使用)
```
