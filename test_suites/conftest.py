import time
import pytest
from comm_layer.diagnostic import Diagnostics
from config.config import db_path, can_messages, crc_messages


@pytest.fixture(scope='session')
def can_bus():
    with Diagnostics(db_path) as can:
        can.build_crc_msgs(*crc_messages)
        can.init_CAN_messages(can_messages)
        time.sleep(5)
        yield can
