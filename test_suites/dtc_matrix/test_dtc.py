import time


def test_read_dtc(can_bus):
    can_bus.clear_all_dtc()
    time.sleep(4)
    can_bus.check_dtc_by_status_mask()
    time.sleep(2)
    can_bus.send_periodic_signal('CmdIgnSta', 0x1)
    time.sleep(4)
    can_bus.send_periodic_signal('CmdIgnSta', 0x4)
    time.sleep(4)

    assert True
