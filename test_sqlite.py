import sqlite3
import datetime
import time

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE file (id INTEGER, exif_datetime REAL, last_displayed REAL)")

# photo taken 2020-04-10 (April 10, 2020)
ts_2020 = time.mktime((2020, 4, 10, 12, 0, 0, 0, 0, -1))
# photo played 200 days ago
ts_displayed_recent = time.time() - 200 * 24 * 3600
# photo played 350 days ago
ts_displayed_old = time.time() - 350 * 24 * 3600

conn.execute("INSERT INTO file VALUES(1, ?, 0)", (ts_2020,))
conn.execute("INSERT INTO file VALUES(2, ?, ?)", (ts_2020, ts_displayed_recent))
conn.execute("INSERT INTO file VALUES(3, ?, ?)", (ts_2020, ts_displayed_old))

today = datetime.date.fromtimestamp(time.time())
date_range = 15
candidates = []
for i in range(-date_range, date_range + 1):
    d = today + datetime.timedelta(days=i)
    candidates.append(d.strftime('%m-%d'))
in_clause = ",".join(f"'{c}'" for c in candidates)

cooldown_days = max(1, 365 - (date_range * 2) - 30)
cooldown_seconds = cooldown_days * 24 * 3600

query = f"SELECT id FROM file WHERE strftime('%m-%d', exif_datetime, 'unixepoch', 'localtime') IN ({in_clause}) AND last_displayed < {(time.time() - cooldown_seconds):.0f}"
print(f"Candidates size: {len(candidates)}")
print(f"Query: {query}")
for row in conn.execute(query):
    print("Found ID:", row[0])

