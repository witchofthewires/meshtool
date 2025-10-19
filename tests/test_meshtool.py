import pytest
from meshtool.meshtool import get_interface

def test_always_pass():
    assert True

# TODO add proper label for 'radio tests'
def test_radio_attached(capsys):
    # fails when radio is not connected to serial port
    interface = get_interface()
    cap = capsys.readouterr()
    # TODO better way to check than reading error message directly
    # TODO cleaner pytest output
    returned_radio_not_connected_error = (cap.out == 
                                          "No Serial Meshtastic device detected, attempting TCP connection on localhost.\n")
    assert not returned_radio_not_connected_error
    assert interface is not None