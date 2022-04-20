import sqlite3 as sl

con = sl.connect("press.db")

# with con:
#     con.execute("""
#         CREATE TABLE INFO (
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             x REAL,
#             y REAL,
#             z REAL
#         );
#     """)

# corners INTEGER,
# side TEXT


def show():
    with con:
        data = con.execute("SELECT * FROM INFO")
        for row in data:
            print(row)


def insert(name, x, y, z):
    sql = 'INSERT INTO INFO (name, x, y, z) values(?, ?, ?, ?)'
    data = [
        (name, x, y, z)
        # ("press1", 12.5, 15, 19.65, 4, "5 5 4 4")
    ]
    with con:
        con.executemany(sql, data)
