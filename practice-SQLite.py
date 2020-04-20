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
  'Uses' INTEGER
  'Temp' REAL,
  'Press' REAL,
  'SpecVol' REAL,
  'Energy' REAL,
  'Enthalpy' REAL,
  'Entropy' REAL,
  'Cv' REAL,
  'Cp' REAL,
  'Phase' TEXT
);
"""

cur.execute(drop_Cycles)
cur.execute(create_Cycles)
cur.execute(drop_States)
cur.execute(create_States)

conn.commit()

