import attr
from typing import *
from dlms_cosem.clients.serial_hdlc import SerialHdlcClient
from dlms_cosem.protocol.connection import DlmsConnection
from dlms_cosem.protocol import xdlms, cosem, exceptions, enumerations, dlms_data
from dlms_cosem.protocol import acse, state
import logging
import contextlib

from dlms_cosem.protocol.xdlms import ConfirmedServiceErrorApdu

LOG = logging.getLogger(__name__)


class DataResultError(Exception):
    """ Error retrieveing data"""


class HLSError(Exception):
    """error in HLS procedure"""


@attr.s(auto_attribs=True)
class SerialDlmsClient:
    client_logical_address: int
    server_logical_address: int
    serial_port: str
    serial_baud_rate: int = attr.ib(default=9600)
    server_physical_address: Optional[int] = attr.ib(default=None)
    client_physical_address: Optional[int] = attr.ib(default=None)
    authentication_method: Optional[enumerations.AuthenticationMechanism] = attr.ib(
        default=None
    )
    password: Optional[bytes] = attr.ib(default=None)
    encryption_key: Optional[bytes] = attr.ib(default=None)
    authentication_key: Optional[bytes] = attr.ib(default=None)
    security_suite: Optional[bytes] = attr.ib(default=0)
    dedicated_ciphering: bool = attr.ib(default=False)
    block_transfer: bool = attr.ib(default=False)
    max_pdu_size: int = attr.ib(default=65535)
    client_system_title: Optional[bytes] = attr.ib(default=None)
    client_initial_invocation_counter: int = attr.ib(default=0)
    meter_initial_invocation_counter: int = attr.ib(default=0)

    dlms_connection: DlmsConnection = attr.ib(
        default=attr.Factory(
            lambda self: DlmsConnection(
                client_system_title=self.client_system_title,
                authentication_method=self.authentication_method,
                password=self.password,
                global_encryption_key=self.encryption_key,
                global_authentication_key=self.authentication_key,
                use_dedicated_ciphering=self.dedicated_ciphering,
                use_block_transfer=self.block_transfer,
                security_suite=self.security_suite,
                max_pdu_size=self.max_pdu_size,
                client_invocation_counter=self.client_initial_invocation_counter,
                meter_invocation_counter=self.meter_initial_invocation_counter,
            ),
            takes_self=True,
        )
    )
    io_interface: SerialHdlcClient = attr.ib(
        default=attr.Factory(
            lambda self: SerialHdlcClient(
                client_logical_address=self.client_logical_address,
                client_physical_address=self.client_physical_address,
                server_logical_address=self.server_logical_address,
                server_physical_address=self.server_physical_address,
                serial_port=self.serial_port,
                serial_baud_rate=self.serial_baud_rate,
            ),
            takes_self=True,
        )
    )

    @contextlib.contextmanager
    def session(self):
        self.associate()
        yield self
        self.release_association()

    # TODO: ensure association with decorator
    def get(
        self, ic: enumerations.CosemInterface, instance: cosem.Obis, attribute: int
    ):
        # Just a random get request.
        self.send(
            xdlms.GetRequest(
                cosem_attribute=cosem.CosemAttribute(
                    interface=ic, instance=instance, attribute=attribute
                )
            )
        )
        get_response = self.next_event()
        if isinstance(get_response.result, enumerations.DataAccessResult):
            raise DataResultError(
                f"Could not perform GET request: {get_response.result!r}"
            )
        return get_response.result

    def set(self):
        pass

    def action(self):
        pass

    def associate(
        self,
        association_request: Optional[acse.ApplicationAssociationRequestApdu] = None,
    ) -> acse.ApplicationAssociationResponseApdu:
        # set up hdlc
        self.io_interface.connect()
        aarq = association_request or self.dlms_connection.get_aarq()
        self.send(aarq)
        aare = self.next_event()
        if isinstance(aare, xdlms.ExceptionResponseApdu):
            raise Exception(
                f"DLMS Exception: {aare.state_error!r}:{aare.service_error!r}:{aare.invocation_counter_data}"
            )
        if aare.result is not enumerations.AssociationResult.ACCEPTED:
            raise exceptions.ApplicationAssociationError(
                f"Unable to perform Association: {aare.result!r} and "
                f"{aare.result_source_diagnostics!r}"
            )
        if aare.user_information:
            if isinstance(aare.user_information.content, ConfirmedServiceErrorApdu):
                raise exceptions.ApplicationAssociationError(
                    f"Unable to perform Association: {aare.user_information.content.error}"
                )

        if (
            self.dlms_connection.state.current_state
            == state.SHOULD_SEND_HLS_SEVER_CHALLENGE_RESULT
        ):
            action_request = xdlms.ActionRequest(
                cosem_method=cosem.CosemMethod(
                    enumerations.CosemInterface.ASSOCIATION_LN,
                    cosem.Obis(0, 0, 40, 0, 0),
                    1,
                ),
                action_type=enumerations.ActionType.NORMAL,
                parameters=dlms_data.OctetStringData(
                    self.dlms_connection.get_hls_reply()
                ).to_bytes(),
            )
            self.send(action_request)
            action_response = self.next_event()
            if action_response.result != enumerations.ActionResult.SUCCESS:
                raise HLSError(f"HLS authentication failed: {action_response.result!r}")

            if not self.dlms_connection.hls_response_valid(action_response.result_data):
                raise HLSError(
                    f"Meter did not respond with correct challenge calculation"
                )
        return aare

    def release_association(self) -> acse.ReleaseResponseApdu:

        rlrq = self.dlms_connection.get_rlrq()
        self.send(rlrq)
        rlre = self.next_event()
        self.io_interface.disconnect()
        return rlre

    def send(self, *events):
        for event in events:
            data = self.dlms_connection.send(event)
            response_bytes = self.io_interface.send(data)

            self.dlms_connection.receive_data(response_bytes)

    def next_event(self):
        event = self.dlms_connection.next_event()
        LOG.info(f"Received {event}")
        return event
