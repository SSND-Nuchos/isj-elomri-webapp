from flask import Flask
import sqlite3

app = Flask(__name__)

def pripoj_db():
    return sqlite3.connect("elomri-kurzy.db")

@app.route('/')
def index():
    return '''
        <h1>Výber z databázy</h1>
        <a href="/treneri"><button>Zobraz trénerov a ich kurzy</button></a>
        <a href="/kurzy"><button>Zobraz všetky kurzy</button></a>
        <a href="/miesta"><button>Zobraz všetky miesta</button></a>
        <a href="/sucet_kapacity"><button>Súčet kapacity kurzov na 'P'</button></a>
    '''

@app.route('/treneri')
def zobraz_trenerov():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM VSETCI_TRENERI_A_ICH_KURZY")
    treneri = cursor.fetchall()
    conn.close()
    return "".join(f"<p>{row}</p>" for row in treneri) + '<a href="/">Späť</a>'

@app.route('/kurzy')
def zobraz_kurzy():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Nazov, MaxKapacita FROM Kurzy")
    kurzy = cursor.fetchall()
    conn.close()
    return "".join(f"<p>{row}</p>" for row in kurzy) + '<a href="/">Späť</a>'

@app.route('/miesta')
def zobraz_miesta():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Nazov FROM Miesta")
    miesta = cursor.fetchall()
    conn.close()
    return "".join(f"<p>{row}</p>" for row in miesta) + '<a href="/">Späť</a>'

@app.route('/sucet_kapacity')
def sucet_kapacity():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(MaxKapacita), 0) FROM Kurzy WHERE Nazov LIKE 'P%'")
    sucet = cursor.fetchall()
    conn.close()
    return f"<h2>Súčet kapacity: {sucet}</h2><a href='/'>Späť</a>"

if __name__ == '__main__':
    app.run(debug=True)