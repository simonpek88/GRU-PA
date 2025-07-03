# coding utf-8
import sys

from commFunc import execute_sql, execute_sql_and_commit
from mysql_pool import get_connection

# cSpell:ignoreRegExp /[^\s]{16,}/
# cSpell:ignoreRegExp /\b[A-Z]{3,15}\b/g
# cSpell:ignoreRegExp /\b[A-Z]\b/g


def reset_id():
    i = 1
    j = 1
    sql = "SELECT ID from bjs_pa order by task_group, pa_num"
    rows = execute_sql(cur2, sql)
    for row in rows:
        sql = f"UPDATE bjs_pa SET ID = {j}, pa_num = {i} where ID = {row[0]}"
        execute_sql_and_commit(conn2, cur2, sql)
        i += 2
        j += 1

conn2 = get_connection()
cur2 = conn2.cursor()
if sys.argv[1].upper() == "RESETID":
    reset_id()
