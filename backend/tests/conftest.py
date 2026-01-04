"""Test configuration and fixtures.

Sets up mocking for external dependencies before imports.
"""

import sys
from unittest.mock import MagicMock

# Mock the supabase module and its dependencies before any imports
mock_supabase = MagicMock()
mock_realtime = MagicMock()
mock_websockets = MagicMock()

sys.modules["supabase"] = mock_supabase
sys.modules["realtime"] = mock_realtime
sys.modules["websockets"] = mock_websockets
sys.modules["websockets.asyncio"] = mock_websockets
sys.modules["websockets.asyncio.client"] = mock_websockets

# Create mock Client class
mock_supabase.Client = MagicMock
mock_supabase.create_client = MagicMock(return_value=MagicMock())
