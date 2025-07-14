class MessageData:
    """
    Représente un message structuré à traiter dans le worker.

    Attributs :
        msg_id (str) : ID unique du message.
        user_id (str) : ID utilisateur émetteur.
        text (str) : Contenu textuel à analyser.
        type (str) : Type d’action (update / delete).
        timestamp (str) : Date ISO du message.
        _extra (dict) : Champs supplémentaires.

    Raises:
        KeyError: si 'msg_id' ou 'type' sont manquant.
    """
    __slots__ = ("msg_id", "user_id", "text", "type", "timestamp", "_extra")

    def __init__(self, raw_dict: dict):
        """
        Initialise un objet MessageData à partir d’un dictionnaire brut.

        Args:
            raw_dict (dict): Dictionnaire contenant les données du message.
        """
        self.msg_id = raw_dict["msg_id"]
        self.user_id = raw_dict.get("user_id")
        self.text = raw_dict.get("text")
        self.type = raw_dict["type"]
        self.timestamp = raw_dict.get("timestamp")

        # Capture des champs non attendus
        known_keys = {"msg_id", "user_id", "text", "type", "timestamp"}
        self._extra = {k: v for k, v in raw_dict.items() if k not in known_keys}

    def to_dict(self, include_extra: bool = True) -> dict:
        """
        Convertit l’objet en dictionnaire natif.

        Args:
            include_extra (bool): Si False, n'inclut pas les champs `_extra`.

        Returns:
            dict: Représentation standard du message.
        """
        base = {
            "msg_id": self.msg_id,
            "user_id": self.user_id,
            "text": self.text,
            "type": self.type,
            "timestamp": self.timestamp,
        }

        if include_extra:
            base.update(self._extra)
        return base

    def get_extra(self) -> dict:
        """
        Retourne les champs supplémentaires non attendus.

        Returns:
            dict: Champs inconnus.
        """
        return self._extra