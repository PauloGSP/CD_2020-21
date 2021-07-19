import pytest
from unittest.mock import patch
from mock import MagicMock
from mockselector.selector import MockSocket, ListenSocket, MockSelector

from src.server import Server


class CDProtoException(Exception):
    pass


def test_server():
    """Test that the server used CDProto methods."""
    c1 = MockSocket([b""])
    s = ListenSocket((c1,))
    s.setsockopt = MagicMock()
    sel = MockSelector([s, c1])

    def fail(s):
        raise CDProtoException()

    with patch("socket.socket") as socket, patch(
        "selectors.DefaultSelector"
    ) as selector, patch("src.protocol.CDProto.recv_msg", new=fail):
        socket.return_value = s
        selector.return_value = sel

        with sel:
            s = Server()

            with pytest.raises(CDProtoException):
                s.loop()
