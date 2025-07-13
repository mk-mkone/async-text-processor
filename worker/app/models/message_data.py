class MessageData:
    """
    Représente un message structuré à traiter dans le worker.

    Attributs :
        msg_id (str) : ID unique du message.
        user_id (str) : ID utilisateur émetteur.
        text (str) : Contenu textuel à analyser.
        type (str) : Type d’action (update / delete).
        timestamp (str) : Date ISO du message.
    """
    __slots__ = ("msg_id", "user_id", "text", "type", "timestamp")

    def __init__(self, raw_dict: dict):
        """
        Initialise un objet MessageData à partir d’un dictionnaire brut.

        Args:
            raw_dict (dict): Dictionnaire contenant les données du message.
        """
        self.msg_id = raw_dict.get("msg_id")
        self.user_id = raw_dict.get("user_id")
        self.text = raw_dict.get("text", "")
        self.type = raw_dict.get("type", "unknown")
        self.timestamp = raw_dict.get("timestamp")

    def to_dict(self) -> dict:
        """
        Convertit l’objet en dictionnaire natif.

        Returns:
            dict: Représentation standard du message.
        """
        return {
            "msg_id": self.msg_id,
            "user_id": self.user_id,
            "text": self.text,
            "type": self.type,
            "timestamp": self.timestamp,
        }
