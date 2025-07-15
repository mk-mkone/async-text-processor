from app.models.message_data import MessageData


def test_message_data_required_fields():
    raw = {"msg_id": "msg_123", "type": "update"}
    data = MessageData(raw)
    assert data.msg_id == "msg_123"
    assert data.type == "update"
    assert data.user_id is None
    assert data.text is None


def test_message_data_with_extra_fields():
    raw = {
        "msg_id": "msg_123",
        "type": "update",
        "user_id": "u_42",
        "text": "Hello",
        "lang": "fr",
        "source": "mobile",
    }
    data = MessageData(raw)
    assert "lang" in data._extra
    assert "source" in data._extra
