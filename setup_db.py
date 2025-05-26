import sqlite3

conn = sqlite3.connect("elomri-kurzy.db")
cursor = conn.cursor()

# Vytvorenie tabuľky Treneri
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Treneri (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Meno TEXT NOT NULL
    )
''')

# Vytvorenie tabuľky Kurzy
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Kurzy (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nazov TEXT NOT NULL,
        TypSportu TEXT NOT NULL,
        MaxKapacita INTEGER NOT NULL,
        ID_Trenera INTEGER,
        FOREIGN KEY (ID_Trenera) REFERENCES Treneri(ID)
    )
''')

# Vytvorenie tabuľky Miesta
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Miesta (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nazov TEXT NOT NULL
    )
''')

# Vytvorenie pohľadu VSETCI_TRENERI_A_ICH_KURZY
cursor.execute("DROP VIEW IF EXISTS VSETCI_TRENERI_A_ICH_KURZY")
cursor.execute('''
    CREATE VIEW VSETCI_TRENERI_A_ICH_KURZY AS
    SELECT T.Meno, K.Nazov, K.TypSportu, K.MaxKapacita
    FROM Treneri T
    JOIN Kurzy K ON T.ID = K.ID_Trenera
''')

conn.commit()
conn.close()
print("Databáza bola úspešne pripravená.")
