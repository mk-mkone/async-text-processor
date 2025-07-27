class MessageData:
    """
    Represents a structured message to be processed by the worker.

    Attributes:
        msg_id (str): Unique message ID.
        user_id (str): ID of the emitting user.
        text (str): Text content to analyze.
        type (str): Action type (update / delete).
        timestamp (str): ISO timestamp of the message.
        _extra (dict): Additional unexpected fields.

    Raises:
        KeyError: If 'msg_id' or 'type' are missing from the input.
    """

    __slots__ = ("msg_id", "user_id", "text", "type", "timestamp", "_extra")

    def __init__(self, raw_dict: dict):
        """
        Initializes a MessageData object from a raw dictionary.

        Args:
            raw_dict (dict): Dictionary containing the message data.
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
        Converts the object into a native dictionary.

        Args:
            include_extra (bool): If False, excludes `_extra` fields.

        Returns:
            dict: Standard dictionary representation of the message.
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
        Returns any additional unexpected fields.

        Returns:
            dict: Extra/unexpected fields.
        """
        return self._extra
