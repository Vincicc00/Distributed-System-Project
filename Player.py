class Player:
    def __init__(self, name: str, u_id: str, team_name: str = None):
        """
        Inizializza un giocatore con un nome, un identificativo unico e, opzionalmente, il nome di un team.
        """
        self.name = name
        self.u_id = u_id
        self.team_name = team_name  # Relazione debole con il Team

    def __repr__(self):
        return f"Player(name={self.name}, u_id={self.u_id}, team_name={self.team_name})"
    
    # Getter e Setter per 'name'
    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    # Getter e Setter per 'u_id'
    def get_u_id(self):
        return self._u_id

    def set_u_id(self, u_id: str):
        self._u_id = u_id

    # Getter e Setter per 'team_name'
    def get_team_name(self):
        return self._team_name

    def set_team_name(self, team_name: str):
        self._team_name = team_name

    def __repr__(self):
        return f"Player(name={self._name}, u_id={self._u_id}, team_name={self._team_name})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_u_id() == other.get_u_id()
        else:
            return False
        
    def __hash__(self):
        return hash(self.get_u_id())