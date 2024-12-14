class Station:
    def __init__(self, ip_address: str, score_station: int):
        """
        Inizializza una stazione con un indirizzo IP e un punteggio.
        """
        self.ip_address = ip_address
        self.score_station = score_station

    def __repr__(self):
        return f"Station(ip_address={self.ip_address}, score_station={self.score_station})"
    
    # Getter e Setter per 'ip_address'
    def get_ip_address(self):
        return self._ip_address

    def set_ip_address(self, ip_address: str):
        self._ip_address = ip_address

    # Getter e Setter per 'score_station'
    def get_score_station(self):
        return self._score_station

    def set_score_station(self, score_station: int):
        self._score_station = score_station

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_ip_address() == other.get_ip_address()
        else:
            return False
        
    def __hash__(self):
        return hash(self.get_ip_address())