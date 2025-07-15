import pytest
from app.models.message_data import MessageData
from app.processing import heavy_analysis


@pytest.fixture
def monkey_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)


def test_analysis_with_minimal_update(monkey_sleep):
    data = MessageData(
        {
            "msg_id": "msg_001",
            "type": "update",
            "text": "test",
        }
    )
    result = heavy_analysis(data)
    assert result["msg_id"] == "msg_001"
    assert result["status"] == "done"
    assert "score" in result and isinstance(result["score"], int)


def test_analysis_with_extra_fields(monkey_sleep):
    data = MessageData(
        {
            "msg_id": "msg_002",
            "type": "update",
            "text": "extra test",
            "lang": "fr",
            "meta": {"source": "test_gen"},
        }
    )
    result = heavy_analysis(data)
    assert result["msg_id"] == "msg_002"
    assert "lang" in result
    assert "meta" in result


def test_analysis_with_missing_text(monkey_sleep):
    data = MessageData({"msg_id": "msg_003", "type": "update"})
    result = heavy_analysis(data)
    assert result["msg_id"] == "msg_003"
    assert result["score"] is None
    assert "text" in result and result["text"] is None


def test_heavy_analysis_with_minimal_message(monkeypatch):
    data = MessageData(
        {
            "msg_id": "msg_004",
            "type": "update",
            "text": "hello world",
            "user_id": "u1",
            "timestamp": "2024-01-01T00:00:00",
            "custom_field": "xyz",
        }
    )

    result = heavy_analysis(data)
    assert result["msg_id"] == "msg_004"
    assert "score" in result
    assert "custom_field" in result
    assert result["status"] == "done"


def test_heavy_analysis_with_no_text(monkeypatch):
    data = MessageData({"msg_id": "no_text_id", "type": "update"})
    result = heavy_analysis(data)
    assert result["score"] is None
    assert result["text"] is None
    assert result["msg_id"] == "no_text_id"
