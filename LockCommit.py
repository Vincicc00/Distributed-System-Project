import threading
from enum import Enum
import sqlite3

class LockType(Enum):
    NONE = 0
    SHARED = 1
    EXCLUSIVE = 2

    def conflicts_with(self, other):
        """
        Definisce se due tipi di lock sono in conflitto.
        tabella conflitto
                    Shared Exclusive
        None        false  false
        SHARED      false  true
        EXCLUSIVE   true   true
        """
        if self == LockType.EXCLUSIVE or (other == LockType.EXCLUSIVE and self != LockType.NONE):
            return True
        else : return False

class Lock:
    def __init__(self, id_squadra : int):
        """
        Inizializza il lock associato a un oggetto protetto.
        """
        self.id_squadra= id_squadra  # L'oggetto protetto dal lock
        self.holders = []  # Lista dei TransID (ID delle transazioni) che detengono il lock
        self.lock_type = LockType.NONE  # Tipo di lock corrente
        self.condition = threading.Condition()  # Per la sincronizzazione

        conn = sqlite3.connect('2pl_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT punteggio_tot FROM squadra WHERE id_squadra = ?", (id_squadra,))
        self.before_points = int(cursor.fetchone()[0])

        self.points = self.before_points


    def acquire(self, trans_id : int, requested_lock_type : LockType):
        """
        Acquisisce un lock per una transazione.
        """
        with self.condition:
            while self.lock_type.conflicts_with(requested_lock_type):
                self.condition.wait()
            if not self.holders: #lista holders è vuota
                # Nessuna transazione detiene il lock, lo appendo e metto il mio TID
                self.holders.append(trans_id)
                self.lock_type = requested_lock_type
            elif self.lock_type == LockType.SHARED and requested_lock_type == LockType.SHARED:
                # Aggiunge la transazione ai detentori per lock condiviso
                self.holders.append(trans_id)



    def release(self, trans_id : int):
        """
        Rilascia un lock detenuto da una transazione.
        """
        with self.condition:
            if trans_id in self.holders:
                self.holders.remove(trans_id)
                if not self.holders:
                    self.lock_type = LockType.NONE  # Resetta il tipo di lock se nessuno lo detiene
            self.condition.notify_all()

    def getPoints(self, trans_id : int):
        if(self.lock_type!= LockType.NONE and trans_id in self.holders):
            return self.points
        
    def setPoints(self, trans_id : int, amount : int):
        if(self.lock_type == LockType.EXCLUSIVE and trans_id in self.holders):
            self.points = amount

    def commit(self, trans_id : int):
        if(self.lock_type == LockType.EXCLUSIVE and trans_id in self.holders):
            self.before_points = self.points
        conn = sqlite3.connect('2pl_database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE squadra SET punteggio_tot = ? WHERE id_squadra = ?", (self.points, self.id_squadra,))
        conn.commit()
        conn.close()


    def abort(self, trans_id : int):
        if(self.lock_type == LockType.EXCLUSIVE and trans_id in self.holders):
            self.points = self.before_points

        






class LockManager:
    _instance = None  # Per implementare il singleton
    _lock = threading.Lock()  # Lock per garantire thread-safety nel singleton

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LockManager, cls).__new__(cls)
                cls._instance.init_singleton()
            return cls._instance

    def init_singleton(self):
        """
        Inizializza l'istanza singleton.
        """
        self.the_locks = {}  # Dizionario che associa gli oggetti ai lock
        self.lock_table_lock = threading.Lock()  # Lock per sincronizzare l'accesso al dizionario

    def set_lock(self, id_squadra : int, trans_id : int, lock_type : LockType):
        """
        Imposta un lock su un oggetto per una determinata transazione.
        """
        with self.lock_table_lock:
            # Trova il lock associato all'oggetto, o creane uno nuovo
            if id_squadra not in self.the_locks:
                self.the_locks[id_squadra] = Lock(id_squadra)  # Lock è la classe definita in precedenza
            found_lock = self.the_locks[id_squadra]
        
        # Acquisisce il lock fuori dal blocco sincronizzato del dizionario
        found_lock.acquire(trans_id, lock_type)

    def unlock(self, trans_id: int, commit : bool):
        """
        Rilascia tutti i lock detenuti da una transazione.
        """
        with self.lock_table_lock:
            for lock in list(self.the_locks.values()):
                # Rimuove il lock se la transazione è un holder
                if commit == True: lock.commit(trans_id) 
                else: lock.abort(trans_id)
                lock.release(trans_id)

    def retrievePoints(self, trans_id : int, id_squadra : int):
        with self.lock_table_lock:
            found_lock=self.the_locks[id_squadra]
            return found_lock.getPoints(trans_id)
        
    def updatePoints(self, trans_id :int, id_squadra : int, amount :int ):
        with self.lock_table_lock:
            found_lock = self.the_locks[id_squadra]
            found_lock.setPoints(trans_id , amount)