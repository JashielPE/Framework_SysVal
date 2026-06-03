import time
import pytest


@pytest.fixture(scope='module', autouse=True)
def clear_dtc(can_bus):
    can_bus.clear_all_dtc()
    time.sleep(2)
