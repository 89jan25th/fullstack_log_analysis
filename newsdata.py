import psycopg2
import pandas as pd
DBNAME = "news"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()

c.execute("create view popular as select slug, count(*) as num from articles, log where log.path like '%' || articles.slug || '%' group by slug order by num desc")
c.execute("create view popular_result as select title, author, num from popular, articles where popular.slug = articles.slug")

print("1. What are the most popular three articles of all time?")
df = pd.read_sql_query("select title as article, num as views from popular_result order by num desc limit 3", db)
print(df)

print("\n2. Who are the most popular article authors of all time?")
df = pd.read_sql_query("select name, sum(num)::bigint as views from popular_result, authors where authors.id = popular_result.author group by name order by views desc", db)
print(df)

c.execute("create view traffic as select id, time::timestamp::date, status from log")
c.execute("create view traffic_ok as select time, count(*) as ok from traffic where status like '200%' group by time order by ok desc")
c.execute("create view traffic_bad as select time, count(*) as bad from traffic where status like '404%' group by time order by bad desc")

print("\n3. On which days did more than 1 percent of requests lead to erroers?")
df = pd.read_sql_query("select traffic_bad.time, ok, bad, bad/(bad+ok)::decimal*100 as ratio from traffic_ok, traffic_bad where traffic_ok.time = traffic_bad.time and bad/(bad+ok)::decimal*100 > 1", db)
print(df)

db.close()
