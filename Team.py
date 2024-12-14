import Player

class Team:
    def __init__(self, name: str, id: int):
        """
        Inizializza un team con un nome, un ID univoco e uno score iniziale di 0.
        """
        self.name = name
        self.id = id
        self.score = 0
        self.players = []  # Una lista di oggetti Player

    def add_player(self, player: Player):
        """
        Aggiunge un giocatore al team e aggiorna la sua relazione debole.
        """
        self.players.append(player)
        player.team_name = self.name

    def add_points(self, points: int):
        """
        Aggiunge punti al punteggio del team.
        """
        self.score += points

    def __repr__(self):
        return f"Team(name={self.name}, id={self.id}, score={self.score}, players={self.players})"
    
    
    # Getter e Setter per 'name'
    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    # Getter e Setter per 'id'
    def get_id(self):
        return self._id

    def set_id(self, id: int):
        self._id = id

    # Getter e Setter per 'score'
    def get_score(self):
        return self._score

    def set_score(self, score: int):
        self._score = score

    # Getter e Setter per 'players'
    def get_players(self):
        return self._players

    def set_players(self, players: list):
        self._players = players

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_id() == other.get_id()
        else:
            return False
        
    def __hash__(self):
        return hash(self.get_id())