import sqlite3

conn = sqlite3.connect("practice-DB.sqlite")
cur = conn.cursor()

drop_Cycles = '''
    DROP TABLE IF EXISTS "Cycles";
'''

drop_States = """
DROP TABLE IF EXISTS 'States';
"""

create_Cycles = '''
    CREATE TABLE IF NOT EXISTS "Cycles" (
        "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Efficiency"  REAL,
        "SearchTimes" INTEGER NOT NULL,
        "s1_Id"  INTEGER,
        "s2_Id"  INTEGER,
        "s3_Id"  INTEGER,
        "s4_Id"  INTEGER
    );
'''

create_States = """
CREATE TABLE IF NOT EXISTS 'States' (
  'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
  'Uses' INTEGER,
  'Temp' REAL,
  'Press' REAL,
  'SpecVol' REAL,
  'Energy' REAL,
  'Enthalpy' REAL,
  'Entropy' REAL,
  'Quality' REAL,
  'Phase' TEXT
);
"""

populate_state1 = """
INSERT INTO States
    VALUES (NULL, 0, 1, 1, 1, 1, 1, 1, NULL, 'vapor')
"""

populate_state2 = """
INSERT INTO States
    VALUES (NULL, 34, 2, 2, 2, 2, 2, 2, NULL, 'liquid')
"""

query1 = """
SELECT Temp, Press, Enthalpy, Entropy, Quality, SpecVol, Energy, Phase
    FROM States
    WHERE Temp = 2 and Enthalpy = 2
    """

query2 = """
SELECT Temp, Press, Enthalpy, Entropy, Quality, SpecVol, Energy, Phase
    FROM States
    WHERE Temp = 1 and Press = 2
    """


cur.execute(drop_Cycles)
cur.execute(create_Cycles)
cur.execute(drop_States)
cur.execute(create_States)

cur.execute(populate_state1)
cur.execute(populate_state2)

cur.execute(query1)
listing = cur.fetchone()
print(listing)
print(listing[4])

cur.execute(query2)
print(cur.fetchone())

print(cur.fetchone() == None)

conn.commit()

