class MessageData:
    __slots__ = ("msg_id", "user_id", "text", "type", "timestamp")

    def __init__(self, raw_dict: dict):
        self.msg_id = raw_dict.get("msg_id")
        self.user_id = raw_dict.get("user_id")
        self.text = raw_dict.get("text", "")
        self.type = raw_dict.get("type", "unknown")
        self.timestamp = raw_dict.get("timestamp")

    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "user_id": self.user_id,
            "text": self.text,
            "type": self.type,
            "timestamp": self.timestamp,
        }
