# vSQL
基于pymysql的关系映射型数据库框架
[![vSQL](https://github.com/VoterLin/vSQL)](https://github.com/VoterLin/vSQL/)
[![Python3.7](https://www.mysql.com)](https://pypi.python.org/pypi/pubnub/)
[![MySQL](https://www.python.org)](https://www.python.org)

### 项目结构：

##### vSQL
###### |- vattr.py
###### |_ vorm.py
    

### 如何使用：
  将vSQL放入到项目包中。
  导入vSQL包
```pyhton
from vSQL.vorm import Module
from vSQL.vattr import *
```
### 创建
####  根据你想要创建的表名和列名创建相应的类(使该类继承vorm中的Module类)和类属性。
####  例如：
```pyhton
class News(Module):
    id = column(zintger(20), isAutocount=True, isPrimary=True, isNotnull=True)
    name = column(zchar(20), isNotnull=True)
```
#### （注意，要想编写__init__构造函数，请务必调用super().__init__()，否则会报错）
当创建如上述代码中的类时。
等效于SQL语句中的：
```
"CREATE TABLE IF NOT EXISTS News(id INTGER(20) AUTO_INCREMENT PRIMARY KEY NOT NULL, name CHAR(20) NOT NULL)"
```
之后程序就会自动帮你创建出该表与其列。
### 插入
```pyhton
def main():
    news = News()
    news.id = 123456
    news.name = 'VoterLin'
    news.insert()
```
等效于SQL语句中的：
```
"INSERT INTO News (id, name) VALUES (123456, 'VoterLin')"
```
### 查找
```pyhton
def main()
    news = News()
    news.id = 123456
    newsList = news.select()
```
等效于SQL语句中的：
```
"SELECT * FROM News WHERE id = 123456"
```
也可以不赋值
```pyhton
    news = News()
    newsList = news.select()
```
等效于SQL语句中的：
```
"SELECT * FROM News"
```
其返回值newsList的是包含查找结果的数组，其中每一项是一个News类型。
对newsList可以
```pyhton
    for news in newsList：
        print(news.id, news.name)
```
打印结果
#### 除了上述方法以外还可以添加其他的约束条件：
```python
    news = News()
    news.name = 'Lin'
    newsList = news.select(oderby='id', isasc=True, limit=5)
```
等效于SQL语句中的：
```
"SELECT * FROM News WHERE name = 'Lin' ODER BY id ASC LIMIT 5"
```
