import sqlite3

conn = sqlite3.connect("kekw.db")
c = conn.cursor()

s1 = "ghi:"
s2 = "???"

print(s1)
c.execute(f"CREATE TABLE test_table(abc VARCHAR, def VARCHAR, {s1} VARCHAR, '{s2}' VARCHAR)")