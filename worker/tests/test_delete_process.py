from unittest.mock import patch

import pytest
from app.models.message_data import MessageData
from app.processing import process_message


@pytest.mark.asyncio
@patch("app.processing.publish_result")
@patch("app.processing.delete_result")
async def test_process_message_delete_type(mock_delete, mock_publish):
    data = MessageData({"msg_id": "msg_001", "type": "delete"})

    await process_message(data)

    mock_delete.assert_called_once_with("msg_001")
    mock_publish.assert_called_once()
    payload = mock_publish.call_args[0][0]
    assert payload["msg_id"] == "msg_001"
    assert payload["status"] == "deleted"
    assert payload["type"] == "delete"
