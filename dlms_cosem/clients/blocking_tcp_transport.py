import attr
from typing import *
import socket
import logging
from dlms_cosem.protocol.wrappers import WrapperProtocolDataUnit, WrapperHeader

LOG = logging.getLogger(__name__)


@attr.s(auto_attribs=True)
class BlockingTcpTransport:

    host: str
    port: int
    client_logical_address: int
    server_logical_address: int
    tcp_socket: Optional[socket.socket] = attr.ib(init=False, default=None)

    @property
    def address(self) -> Tuple[str, int]:
        return self.host, self.port

    def wrap(self, bytes_to_wrap: bytes) -> bytes:
        """
        When sending data over TCP or UDP it is necessary to wrap the data in the in
        the DLMS IP wrapper. This is so the server (meter) knows where the data is
        intended and how long the message is since there is no "final/poll" bit like
        in HDLC.
        """
        header = WrapperHeader(
            source_wport=self.client_logical_address,
            destination_wport=self.server_logical_address,
            length=len(bytes_to_wrap),
        )
        return WrapperProtocolDataUnit(bytes_to_wrap, header).to_bytes()

    def connect(self):
        """Create a new socket and set it on the transport"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket = sock
        self.tcp_socket.connect(self.address)
        LOG.info(f"Connected to ()")

    def disconnect(self):
        """Close socket and remove it from the transport"""
        self.tcp_socket.close()
        self.tcp_socket = None

    def send(self, bytes_to_send: bytes) -> bytes:
        if not self.tcp_socket:
            raise RuntimeError("TCP transport not connected.")

        self.tcp_socket.sendall(self.wrap(bytes_to_send))
        return self.recv()

    def recv(self) -> bytes:
        if not self.tcp_socket:
            raise RuntimeError("TCP transport not connected.")
        header = WrapperHeader.from_bytes(self.tcp_socket.recv(8))
        data = self.tcp_socket.recv(header.length)
        return data
