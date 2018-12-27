# News website log analysis
## From Udacity Full Stack Web Developer Nanodegree Program Project: Logs Analysis
### Preface
This repository has a python code for analyzing fictional newspaper site's database. The database contains newspaper articles, as well as the web server log for the site. The log has a database row for each time a reader loaded a web page. The program is to find which authors and articles are most popular and on which day the 404 error rate was the highest.

### How to run the program
With VMbox, vagrant, python, pyscopg2, pandas, and database(newsdata.sql), run "python newsdata.py" in terminal.
* VMbox: https://www.virtualbox.org/wiki/Download_Old_Builds_5_1
* Vagrant: https://www.vagrantup.com/downloads.html
* Python: https://www.python.org/downloads/
* Pyscopg2: 
```
pip install -U pip # make sure to have an up-to-date pip
pip install psycopg2
```
* Pandas: http://pandas.pydata.org
* newsdata.sql: https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip

### What the program shows
```
vagrant@vagrant:/vagrant/fullstack_log_analysis$ python newsdata.py
1. What are the most popular three articles of all time?
                            article   views
0  Candidate is jerk, alleges rival  338647
1  Bears love berries, alleges bear  253801
2  Bad things gone, say good people  170098

2. Who are the most popular article authors of all time?
                     name   views
0         Ursula La Multa  507594
1  Rudolf von Treppenwitz  423457
2   Anonymous Contributor  170098
3          Markoff Chaney   84557

3. On which days did more than 1 percent     of requests lead to erroers?
         time     ok   bad     ratio
0  2016-07-17  54642  1265  2.262686
```

### Source code
```
#!/usr/bin/env python2.7

import psycopg2
import pandas as pd
DBNAME = "news"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()

c.execute("create view popular as select slug, count(*) as num \
    from articles, log where log.path like '%'||articles.slug||'%' \
    and log.status like '200%' group by slug order by num desc")
c.execute("create view popular_result as select title, author, \
    num from popular, articles where popular.slug = articles.slug")

print("1. What are the most popular three articles of all time?")
df = pd.read_sql_query("select title as article, num as views \
    from popular_result order by num desc limit 3", db)
print(df)

print("\n2. Who are the most popular article authors of all time?")
df = pd.read_sql_query("select name, sum(num)::bigint as views \
    from popular_result, authors where authors.id = popular_result.author \
    group by name order by views desc", db)
print(df)

c.execute("create view traffic as select id, \
    time::timestamp::date, status from log")
c.execute("create view traffic_ok as select time, count(*) \
    as ok from traffic where status like '200%' \
    group by time order by ok desc")
c.execute("create view traffic_bad as select time, count(*) \
    as bad from traffic where status like '404%' \
    group by time order by bad desc")

print("\n3. On which days did more than 1 percent \
    of requests lead to erroers?")
df = pd.read_sql_query("select traffic_bad.time, ok, bad, \
    bad/(bad+ok)::decimal*100 as ratio from traffic_ok, traffic_bad where \
    traffic_ok.time = traffic_bad.time and bad/(bad+ok)::decimal*100 > 1", db)
print(df)

db.close()
```

### Explanation of the code
1. Question #1: What are the most popular three articles of all time?
* In order to find articles with the most views, you have to join two tables(articles, log) by matching articles.slug and log.path. Since they are not in the same form, an asterisk is needed to use the like function. **Please note that only log with status '200 OK' should count.**
```
c.execute("create view popular as select slug, count(*) as num \
    from articles, log where log.path like '%'||articles.slug||'%' \
    and log.status like '200%' group by slug order by num desc")
c.execute("create view popular_result as select title, author, \
    num from popular, articles where popular.slug = articles.slug")

print("1. What are the most popular three articles of all time?")
df = pd.read_sql_query("select title as article, num as views \
    from popular_result order by num desc limit 3", db)
print(df)
```

2. Question #2: Who are the most popular article authors of all time?
* A table from the previous question has articles and their ID and views. Therfore, you can join it to the author table for author's name. Note that bigint type was used for views in case of the number is large.
```
print("\n2. Who are the most popular article authors of all time?")
df = pd.read_sql_query("select name, sum(num)::bigint as views \
    from popular_result, authors where authors.id = popular_result.author \
    group by name order by views desc", db)
print(df)
```

3. Question #3: On which days did more than 1 percent of requests lead to erroers?
* OK request has text '200' and bad one has text '404.' So you can make two tables for each OK and bad requests, then find the bad rate of each day's request. Remarkably, you need to put ::decimal\*100 for a rate value so you get decimal numbers.
```
c.execute("create view traffic as select id, \
    time::timestamp::date, status from log")
c.execute("create view traffic_ok as select time, count(*) \
    as ok from traffic where status like '200%' \
    group by time order by ok desc")
c.execute("create view traffic_bad as select time, count(*) \
    as bad from traffic where status like '404%' \
    group by time order by bad desc")

print("\n3. On which days did more than 1 percent \
    of requests lead to erroers?")
df = pd.read_sql_query("select traffic_bad.time, ok, bad, \
    bad/(bad+ok)::decimal*100 as ratio from traffic_ok, traffic_bad where \
    traffic_ok.time = traffic_bad.time and bad/(bad+ok)::decimal*100 > 1", db)
print(df)
```

4. Note
* This code passed pycodestyle.
* Pandas library was used to display the result more clearly.
