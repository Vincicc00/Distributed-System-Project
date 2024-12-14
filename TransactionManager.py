import threading
import time
from datetime import datetime, timedelta
from LockCommit import LockManager

class TransactionManager:
    _instance = None  # Singleton instance
    _lock = threading.Lock()  # Lock for thread-safety in singleton

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TransactionManager, cls).__new__(cls)
                cls._instance.init_singleton()
            return cls._instance

    def init_singleton(self):
        """
        Initializes the singleton instance.
        """
        self.id = -1  # Unique ID for each transaction
        self.valid_trans = {}  # Dictionary to store transactions with expiry times
        self.increment_lock = threading.Lock()
        self.expiry_time = 3  # Expiry time in seconds for transactions
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_transactions, daemon=True)
        self.cleanup_thread.start()

    def nextId(self):
        """
        Generates the next transaction ID and assigns an expiry time.
        """
        with self.increment_lock:
            self.id += 1
            expiry_timestamp = datetime.now() + timedelta(seconds=self.expiry_time)
            self.valid_trans[self.id] = expiry_timestamp
            return self.id

    def closeTransaction(self, trans_id: int):
        """
        Closes a transaction by removing it from the valid transactions list.
        """
        with self.increment_lock:
            if trans_id in self.valid_trans:
                del self.valid_trans[trans_id]

    def isValid(self, trans_id: int):
        """
        Checks if a transaction is valid (exists and has not expired).
        """
        with self.increment_lock:
            return trans_id in self.valid_trans

    def _cleanup_expired_transactions(self):
        """
        Periodically cleans up expired transactions from the valid transactions list.
        """
        lock_manager = LockManager()
        while True:
            time.sleep(1)  # Check every second
            with self.increment_lock:
                current_time = datetime.now()
                expired_keys = [trans_id for trans_id, expiry in self.valid_trans.items() if expiry < current_time]
                for trans_id in expired_keys:
                    #quando cancello una transaazione dall lista delle transazioni valide
                    #faccio l'unlock con abort di tutti
                    del self.valid_trans[trans_id]
                    lock_manager.unlock(trans_id,commit=False)
                    print("The transaction is aborted.", trans_id)

