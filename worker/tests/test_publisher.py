from unittest.mock import AsyncMock, patch

import pytest
from app.publisher import publish_result


@pytest.mark.asyncio
@patch("app.publisher.aio_pika.connect_robust")
async def test_publish_result_success(mock_connect):
    mock_channel = AsyncMock()
    mock_connection = AsyncMock()
    mock_connection.channel.return_value = mock_channel
    mock_connect.return_value = mock_connection

    payload = {"msg_id": "msg_001", "status": "done", "type": "update"}
    await publish_result(payload)

    mock_channel.default_exchange.publish.assert_called_once()
    mock_connect.assert_called_once()
