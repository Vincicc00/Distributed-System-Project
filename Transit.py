class Transit:
    def __init__(self, team_name: str, ip_station: str, timestamp: int):
        """
        Inizializza un transito con il nome del team, l'indirizzo IP della stazione e un timestamp.
        """
        self.team_name = team_name
        self.ip_station = ip_station
        self.timestamp = timestamp

    def __repr__(self):
        return f"Transit(team_name={self.team_name}, ip_station={self.ip_station}, timestamp={self.timestamp})"

        # Getter e Setter per 'team_name'
    def get_team_name(self):
        return self._team_name

    def set_team_name(self, team_name: str):
        self._team_name = team_name

    # Getter e Setter per 'ip_station'
    def get_ip_station(self):
        return self._ip_station

    def set_ip_station(self, ip_station: str):
        self._ip_station = ip_station

    # Getter e Setter per 'timestamp'
    def get_timestamp(self):
        return self._timestamp

    def set_timestamp(self, timestamp: int):
        self._timestamp = timestamp

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_ip_station() == other.get_ip_station() and self.get_team_name() == other.get_team_name()
        else:
            return False
    
    def __hash__(self):
        return hash(self.get_team_name(),self.get_ip_station())