import pytest
from pprint import pprint
from dlms_cosem.protocol.acse import (ApplicationAssociationRequestApdu,
                                      ApplicationAssociationResponseApdu,
                                      ReleaseRequestApdu, AppContextName,
                                      UserInformation, MechanismName, AuthenticationMechanism, AuthFunctionalUnit)
from dlms_cosem.protocol.xdlms import InitiateRequestApdu
from dlms_cosem.protocol.xdlms.conformance import Conformance


def test_aarq():
    # __bytes = b'`\x1d\xa1\t\x06\x07`\x85t\x05\x08\x01\x01\xbe\x10\x04\x0e\x01\x00\x00\x00\x06_\x1f\x04\x00\x00~\x1f\x04\xb0'
    # __bytes = b'`6\xa1\t\x06\x07`\x85t\x05\x08\x01\x01\x8a\x02\x07\x80\x8b\x07`\x85t\x05\x08\x02\x01\xac\n\x80\x0812345678\xbe\x10\x04\x0e\x01\x00\x00\x00\x06_\x1f\x04\x00\x00~\x1f\x04\xb0'
    __bytes = b"`6\xa1\t\x06\x07`\x85t\x05\x08\x01\x01\x8a\x02\x07\x80\x8b\x07`\x85t\x05\x08\x02\x05\xac\n\x80\x08K56iVagY\xbe\x10\x04\x0e\x01\x00\x00\x00\x06_\x1f\x04\x00\x00~\x1f\x04\xb0"
    # __bytes = b'`f\xa1\t\x06\x07`\x85t\x05\x08\x01\x03\xa6\n\x04\x08MMM\x00\x00\xbcaN\x8a\x02\x07\x80\x8b\x07`\x85t\x05\x08\x02\x01\xac\n\x80\x0812345678\xbe4\x042!00\x01#Eg\x80\x13\x02\xff\x8axt\x13=AL\xed%\xb4%4\xd2\x8d\xb0\x04w `k\x17[\xd5"\x11\xbehA\xdb M9\xeeo\xdb\x8e5hU'

    aarq = ApplicationAssociationRequestApdu.from_bytes(__bytes)

    assert __bytes == aarq.to_bytes()
    # print(aarq.user_information.association_information.initiate_request)

    # LN Ref no ciphering, lowest security
    # b'`\x1d\xa1\t\x06\x07`\x85t\x05\x08\x01\x01\xbe\x10\x04\x0e\x01\x00\x00\x00\x06_\x1f\x04\x00\x00~\x1f\x04\xb0'

    # LN Ref, no ciphering, low level security
    # b'`6\xa1\t\x06\x07`\x85t\x05\x08\x01\x01\x8a\x02\x07\x80\x8b\x07`\x85t\x05\x08\x02\x01\xac\n\x80\x0812345678\xbe\x10\x04\x0e\x01\x00\x00\x00\x06_\x1f\x04\x00\x00~\x1f\x04\xb0'

    # LN Reg, no ciphering, high level security
    # b'`6\xa1\t\x06\x07`\x85t\x05\x08\x01\x01\x8a\x02\x07\x80\x8b\x07`\x85t\x05\x08\x02\x05\xac\n\x80\x08K56iVagY\xbe\x10\x04\x0e\x01\x00\x00\x00\x06_\x1f\x04\x00\x00~\x1f\x04\xb0'

    # LN ref, ciphering, low level security
    # b'`f\xa1\t\x06\x07`\x85t\x05\x08\x01\x03\xa6\n\x04\x08MMM\x00\x00\xbcaN\x8a\x02\x07\x80\x8b\x07`\x85t\x05\x08\x02\x01\xac\n\x80\x0812345678\xbe4\x042!00\x01#Eg\x80\x13\x02\xff\x8axt\x13=AL\xed%\xb4%4\xd2\x8d\xb0\x04w `k\x17[\xd5"\x11\xbehA\xdb M9\xeeo\xdb\x8e5hU'
    # TODO: calling-ap-title is used here. Need to investigate if it is used for anything.


def test_simple_aarq():
    data = bytes.fromhex(
        "601DA109060760857405080101BE10040E01000000065F1F0400001E1DFFFF"
    )
    aarq = ApplicationAssociationRequestApdu.from_bytes(data)
    pprint(aarq)
    print(data.hex())
    print(aarq.to_bytes().hex())

    assert data == aarq.to_bytes()

def test_using_authentication_aarq():
    data = bytes.fromhex(
        "601DA109060760857405080101BE10040E01000000065F1F0400001E1DFFFF")
    aarq1 = ApplicationAssociationRequestApdu.from_bytes(data)

    aarq2 = ApplicationAssociationRequestApdu(
        ciphered=False,
        calling_ap_title=None,
        calling_ae_qualifier=None,
        authentication=None,
        calling_authentication_value=None,
        user_information=UserInformation(
            content=InitiateRequestApdu(
                proposed_conformance=Conformance(
                    general_protection=False,
                    general_block_transfer=False,
                    delta_value_encoding=False,
                    attribute_0_supported_with_set=False,
                    priority_management_supported=False,
                    attribute_0_supported_with_get=False,
                    block_transfer_with_get_or_read=True,
                    block_transfer_with_set_or_write=True,
                    block_transfer_with_action=True,
                    multiple_references=True,
                    data_notification=False,
                    access=False,
                    get=True,
                    set=True,
                    selective_access=True,
                    event_notification=False,
                    action=True,
                ),
                proposed_quality_of_service=0,
                client_max_receive_pdu_size=65535,
                proposed_dlms_version_number=6,
                response_allowed=True,
                dedicated_key=None,
            )
        ),
    )
    assert aarq1 == aarq2



def test_conformance():
    c = Conformance(
        priority_management_supported=True,
        attribute_0_supported_with_get=True,
        block_transfer_with_action=True,
        block_transfer_with_get_or_read=True,
        block_transfer_with_set_or_write=True,
        multiple_references=True,
        get=True,
        set=True,
        selective_access=True,
        event_notification=True,
        action=True,
    )

    assert c.to_bytes() == b"\x00\x00\x7e\x1f"


def test_simple_aare():
    data = bytes.fromhex(
        "6129a109060760857405080101a203020100a305a103020100be10040e0800065f1f0400001e1d04c80007"
    )
    aare = ApplicationAssociationResponseApdu.from_bytes(data)
    pprint(aare)

    print(data.hex())
    print(aare.to_bytes().hex())

    assert data == aare.to_bytes()


def test_simple_rlrq():
    data = bytes.fromhex("6203800100")  # Normal no user-information
    rlrq = ReleaseRequestApdu.from_bytes(data)
    print(rlrq)
    print(rlrq.reason.value)
    print(data.hex())
    print(rlrq.to_bytes().hex())
    assert data == rlrq.to_bytes()


def test_simple_rlrq_with_ciphered_initiate_request():
    data = bytes.fromhex(
        "6239800100BE34043221303001234567801302FF8A7874133D414CED25B42534D28DB0047720606B175BD52211BE6841DB204D39EE6FDB8E356855"
    )
    # TODO: We don't have support for globaly ciphered initiate request
    with pytest.raises(ValueError):
        rlrq = ReleaseRequestApdu.from_bytes(data)
        print(rlrq)
        print(rlrq.reason.value)
        print(data.hex())
        print(rlrq.to_bytes().hex())
