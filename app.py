import os
import sqlite3
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cesta k databáze
DB_FILE = "elomri-kurzy.db"
db_path = os.path.abspath(DB_FILE)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}".replace("\\", "/")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Afinná šifra
A, B = 5, 8  # pevne dané kľúče

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

def affin_desifra(text, A, B):
    # Hľadanie inverzného modulu
    def modularna_inverzia(a, m):
        for i in range(1, m):
            if (a * i) % m == 1:
                return i
        return None

    M = modularna_inverzia(A, 26)
    if M is None:
        return "[CHYBA: Neexistuje inverzia pre A]"

    vysledok = ""
    for znak in text.upper():
        if znak.isalpha():
            c = ord(znak) - ord('A')
            desifrovane_c = (M * (c - B)) % 26
            vysledok += chr(desifrovane_c + ord('A'))
        else:
            vysledok += znak
    return vysledok

# SQLAlchemy modely
class Trener(db.Model):
    __tablename__ = "Treneri"
    ID = db.Column(db.Integer, primary_key=True)
    Meno = db.Column(db.String, nullable=False)
    Priezvisko = db.Column(db.String, nullable=False)
    Specializacia = db.Column(db.String)
    Telefon = db.Column(db.String)
    Heslo = db.Column(db.String)

class Kurz(db.Model):
    __tablename__ = "Kurzy"
    ID = db.Column(db.Integer, primary_key=True)
    Nazov = db.Column(db.String, nullable=False)
    TypSportu = db.Column(db.String, nullable=False)
    MaxKapacita = db.Column(db.Integer, nullable=False)
    ID_Trenera = db.Column(db.Integer, db.ForeignKey('Treneri.ID'))

class Miesto(db.Model):
    __tablename__ = "Miesta"
    ID = db.Column(db.Integer, primary_key=True)
    Nazov = db.Column(db.String, nullable=False)
    Adresa = db.Column(db.String)
    Kapacita = db.Column(db.Integer)

# ROUTES
@app.route('/')
def index():
    return '''
        <h1>Výber z databázy</h1>
        <a href="/treneri"><button>Zobraz trénerov</button></a>
        <a href="/kurzy"><button>Zobraz všetky kurzy</button></a>
        <a href="/miesta"><button>Zobraz všetky miesta</button></a>
        <a href="/sucet_kapacity"><button>Súčet kapacity kurzov na 'P'</button></a><br><br>
        <a href="/vloz_kurz"><button>Vlož nový kurz</button></a>
    '''

@app.route('/treneri')
def zobraz_trenerov():
    treneri = Trener.query.all()
    return "<h2>Tréneri:</h2>" + "".join(f"<p>{t.Meno} {t.Priezvisko} – {t.Specializacia}</p>" for t in treneri) + '<a href="/">Späť</a>'

@app.route('/kurzy')
def zobraz_kurzy():
    kurzy = Kurz.query.all()
    return "<h2>Kurzy:</h2>" + "".join(f"<p>{k.ID}: {k.Nazov} ({affin_desifra(k.Nazov, A, B)}), {k.TypSportu} ({affin_desifra(k.TypSportu, A, B)}), {k.MaxKapacita}</p>" for k in kurzy) + '<a href="/">Späť</a>'

@app.route('/miesta')
def zobraz_miesta():
    miesta = Miesto.query.all()
    return "<h2>Miesta:</h2>" + "".join(f"<p>{m.ID}: {m.Nazov}, {m.Adresa}</p>" for m in miesta) + '<a href="/">Späť</a>'

@app.route('/sucet_kapacity')
def sucet_kapacity():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(MaxKapacita), 0) FROM Kurzy WHERE Nazov LIKE 'P%'")
    sucet = cursor.fetchone()[0]
    conn.close()
    return f"<h2>Súčet kapacity kurzov na 'P': {sucet}</h2><a href='/'>Späť</a>"

@app.route('/vloz_kurz', methods=['GET', 'POST'])
def vloz_kurz():
    if request.method == 'POST':
        nazov = affin_sifra(request.form['nazov'], A, B)
        typ = affin_sifra(request.form['typ'], A, B)
        max_kapacita = int(request.form['max_kapacita'])
        id_trenera = int(request.form['id_trenera'])

        novy_kurz = Kurz(Nazov=nazov, TypSportu=typ, MaxKapacita=max_kapacita, ID_Trenera=id_trenera)
        db.session.add(novy_kurz)
        db.session.commit()

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
    with app.app_context():
        db.create_all()
    app.run(debug=True)
