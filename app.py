from flask import Flask, request
import sqlite3

app = Flask(__name__)

def pripoj_db():
    return sqlite3.connect("elomri-kurzy.db")

def affin_sifra(text, A, B):
    vysledok = ""
    for znak in text.upper():
        if znak.isalpha():
            c = ord(znak) - ord('A')
            sifrovane_c = (A * c + B) % 26
            vysledok += chr(sifrovane_c + ord('A'))
        else:
            vysledok += znak
    return vysledok

@app.route('/')
def index():
    return '''
        <h1>Výber z databázy</h1>
        <a href="/treneri"><button>Zobraz trénerov a ich kurzy</button></a>
        <a href="/kurzy"><button>Zobraz všetky kurzy</button></a>
        <a href="/miesta"><button>Zobraz všetky miesta</button></a>
        <a href="/sucet_kapacity"><button>Súčet kapacity kurzov na 'P'</button></a><br><br>
        <a href="/vloz_kurz"><button>Vlož nový kurz</button></a>
    '''

@app.route('/treneri')
def zobraz_trenerov():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Meno, Priezvisko, Specializacia FROM Treneri")
    treneri = cursor.fetchall()
    conn.close()
    return "<h2>Tréneri:</h2>" + "".join(f"<p>{row}</p>" for row in treneri) + '<a href="/">Späť</a>'

@app.route('/kurzy')
def zobraz_kurzy():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Nazov, TypSportu, MaxKapacita FROM Kurzy")
    kurzy = cursor.fetchall()
    conn.close()
    return "<h2>Kurzy:</h2>" + "".join(f"<p>{row}</p>" for row in kurzy) + '<a href="/">Späť</a>'

@app.route('/miesta')
def zobraz_miesta():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Nazov, Adresa FROM Miesta")
    miesta = cursor.fetchall()
    conn.close()
    return "<h2>Miesta:</h2>" + "".join(f"<p>{row}</p>" for row in miesta) + '<a href="/">Späť</a>'

@app.route('/sucet_kapacity')
def sucet_kapacity():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(MaxKapacita), 0) FROM Kurzy WHERE Nazov LIKE 'P%'")
    sucet = cursor.fetchall()
    conn.close()
    return f"<h2>Súčet kapacity kurzov na 'P': {sucet[0][0]}</h2><a href='/'>Späť</a>"

@app.route('/vloz_kurz', methods=['GET', 'POST'])
def vloz_kurz():
    if request.method == 'POST':
        nazov = request.form['nazov']
        typ = request.form['typ']
        max_kapacita = request.form['max_kapacita']
        id_trenera = request.form['id_trenera']

        A, B = 5, 8
        nazov_sifra = affin_sifra(nazov, A, B)
        typ_sifra = affin_sifra(typ, A, B)

        conn = pripoj_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Kurzy (Nazov, TypSportu, MaxKapacita, ID_Trenera) VALUES (?, ?, ?, ?)",
                       (nazov_sifra, typ_sifra, max_kapacita, id_trenera))
        conn.commit()
        conn.close()
        return '<p>Úspešne pridané!</p><a href="/">Späť na úvod</a>'

    return '''
        <h2>Vloženie kurzu</h2>
        <form method="post">
            Názov kurzu: <input name="nazov"><br>
            Typ športu: <input name="typ"><br>
            Max kapacita: <input name="max_kapacita" type="number"><br>
            ID trénera: <input name="id_trenera" type="number"><br>
            <input type="submit" value="Vložiť">
        </form>
        <a href="/">Späť</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)
