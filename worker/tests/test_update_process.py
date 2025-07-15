import asyncio
from unittest.mock import patch

import pytest
from app.models.message_data import MessageData
from app.processing import process_message


@pytest.mark.asyncio
@patch("app.processing.publish_result")
@patch("app.processing.store_result")
@patch("app.processing.heavy_analysis")
async def test_process_message_update(mock_analysis, mock_store, mock_publish):
    mock_analysis.return_value = {
        "msg_id": "msg_123",
        "user_id": "user_x",
        "text": "Hello",
        "type": "update",
        "timestamp": "2024-01-01",
        "status": "done",
        "duration": 3,
        "score": 87,
        "lang": "fr",
    }

    data = MessageData(
        {
            "msg_id": "msg_123",
            "type": "update",
            "text": "Hello",
            "timestamp": "2024-01-01",
        }
    )

    loop = asyncio.get_running_loop()

    async def fake_executor(executor, func, *args):
        return func(*args)

    with patch.object(loop, "run_in_executor", side_effect=fake_executor):
        await process_message(data)

    mock_store.assert_called_once()
    stored = mock_store.call_args[0][0]
    assert "type" not in stored
    assert "duration" not in stored
    assert "status" not in stored

    mock_publish.assert_called_once()
    published = mock_publish.call_args[0][0]
    assert published["msg_id"] == "msg_123"
    assert published["status"] == "done"
    assert "text" not in published
