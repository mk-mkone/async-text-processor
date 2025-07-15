import pytest
from app.models.message_data import MessageData


def test_message_data_missing_required_fields():
    with pytest.raises(KeyError):
        MessageData({})


def test_message_data_invalid_type_is_allowed():
    raw = {"msg_id": "xx", "type": "unknown"}
    data = MessageData(raw)
    assert data.type == "unknown"
