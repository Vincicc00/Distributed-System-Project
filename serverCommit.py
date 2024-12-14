from flask import Flask, request, jsonify, render_template # type: ignore
import sqlite3
from LockCommit import LockManager, LockType
from TransactionManager import TransactionManager

app = Flask(__name__)
lock_manager = LockManager()
transaction_manager = TransactionManager()

# Database setup
def init_db():
    conn = sqlite3.connect('2pl_database.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS passaggio')
    cursor.execute('DROP TABLE IF EXISTS partecipante')
    cursor.execute('DROP TABLE IF EXISTS stazione')
    cursor.execute('DROP TABLE IF EXISTS squadra')

    cursor.execute('''CREATE TABLE IF NOT EXISTS squadra(
                        nome TEXT,
                        punteggio_tot INTEGER,
                        id_squadra INTEGER,
                        PRIMARY KEY(id_squadra)
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS partecipante(
                        nome TEXT,
                        u_id TEXT,
                        nome_squadra TEXT,
                        CONSTRAINT FK_nomesquadra
                        FOREIGN KEY(nome_squadra) references squadra(nome),
                        PRIMARY KEY(u_id)
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS stazione(
                        ip_stazione TEXT,
                        punteggio_stazione INTEGER,
                        PRIMARY KEY(ip_stazione)
                       )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS passaggio(
                        nome_squadra TEXT,
                        ip_stazione TEXT,
                        CONSTRAINT FK_nomesquadra
                        FOREIGN KEY(nome_squadra) references squadra(nome),
                        CONSTRAINT FK_ipstazione
                        FOREIGN KEY(ip_stazione) references stazione(ip_stazione),
                        PRIMARY KEY(nome_squadra,ip_stazione)
                       )''')

    # Inserimento delle squadre "blu" e "rosso"
    cursor.execute('''INSERT OR IGNORE INTO squadra (nome, id_squadra, punteggio_tot)
                      VALUES ('blu', 1, 0)''')
    cursor.execute('''INSERT OR IGNORE INTO squadra (nome, id_squadra, punteggio_tot)
                      VALUES ('rosso', 0, 0)''')

    conn.commit()
    conn.close()

    #creo tutti i lock qua impsotati a none con già il punteggio in memoria che sarà utilizzato per letture e scritture
    # mi prendo tutti gli id_squadra dal db
    # creo i lock inizializzati a none al cui interno c'è il punteggio
    # li lascio in memoria per le prossime transaazioni
    # nel caso in cui una transazione dove essere abortita perché va oltre l'expiry time, il valore del lock in memoria
    #volatile non viene committata e restituisce il valore

@app.route('/open_transaction', methods=['GET'])
def open_transaction():
    id = transaction_manager.nextId()
    return jsonify({"TID": id})

@app.route('/lock', methods=['POST'])
def lock():
    data = request.get_json()
    if(transaction_manager.isValid(data['trans_id'])): #controllo per ogni route se la transazione è ancora valida
        if data['lock_type'] == 'w':
            lock_manager.set_lock(data['id_squadra'], data['trans_id'], LockType.EXCLUSIVE)
        else:
            lock_manager.set_lock(data['id_squadra'], data['trans_id'], LockType.SHARED)
        return '', 200

@app.route('/retrieve_point', methods=['GET'])
def retrieve_point():
    id_squadra = request.args.get('id_squadra', type=int)
    trans_id = request.args.get('trans_id', type=int)
    if(transaction_manager.isValid(trans_id)):
        result = lock_manager.retrievePoints(trans_id, id_squadra)
        return jsonify({"Punteggio": result})
    else: return '', 500

@app.route('/update_points', methods=['POST'])
def add_points():
    data = request.get_json()
    if(transaction_manager.isValid(data['trans_id'])):
        lock_manager.updatePoints(data['trans_id'],data['id_squadra'],data['amount'])
        return '', 200
    else: return '', 500

@app.route('/unlockClose', methods=['POST'])
def unlockClose():
    trans_id = request.json.get('trans_id')
    if(transaction_manager.isValid(trans_id)):
        lock_manager.unlock(trans_id,commit=True)
        transaction_manager.closeTransaction(trans_id)
        print("The transaction is commited. ", trans_id)
        commit = True
    else:
        commit = False
    
    return jsonify({"Commit": commit})

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    return render_template('leaderboard.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, threaded=True)
