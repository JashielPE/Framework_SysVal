from comm_layer.uds import TEST_FAILED, WARNING_INDICATOR_REQUESTED
import time


def test_dtc_maturation_condition_0xC0800(can_bus):
    DTC = 0xC08000
    dtcs = can_bus.check_dtc_by_status_mask(0x9)
    dtc_status = dtcs.get(DTC, 0)
    assert dtc_status & TEST_FAILED


class TestDTC_C15100:
    DTC = 0xC15100

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('ORC_FD_1')
        print('Removed ORC_FD_1')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('ORC_FD_1')
        print('Send ORC_FD_1')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C13100:
    DTC = 0xC13100

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('EPS_FD_2')
        print('Removed EPS_FD_2')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('EPS_FD_2')
        print('Send EPS_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C13200:
    DTC = 0xC13200

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('ASCM_FD_2')
        print('Removed ASCM_FD_2')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('ASCM_FD_2')
        print('Send ASCM_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C15C00:
    DTC = 0xC15C00

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('ADAS_FD_INFO')
        print('Removed ADAS_FD_INFO')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('ADAS_FD_INFO')
        print('Send ADAS_FD_INFO')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C14000:
    DTC = 0xC14000

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('BCM_FD_2')
        print('Removed BCM_FD_2')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('BCM_FD_2')
        print('Send BCM_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

    def test_maturation_time(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('BCM_FD_2')
        print('Removed BCM_FD_2')
        maturation_time = can_bus.wait_for_dtc_bit(self.DTC, TEST_FAILED)
        print('DTC {:06X} maturation time is: {:.2f}s'.format(self.DTC, maturation_time))
        assert maturation_time > 5.0

        #De-maturation
        can_bus.send_periodic_message('BCM_FD_2')
        print('Send BCM_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C10100:
    DTC = 0xC10100

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('TRANSM_FD_2')
        print('Removed TRANSM_FD_2')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('TRANSM_FD_2')
        print('Send TRANSM_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C10000:
    DTC = 0xC10000

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('ENGINE_FD_2')
        print('Removed ENGINE_FD_2')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('ENGINE_FD_2')
        print('Send ENGINE_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C10200:
    DTC = 0xC10200

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('DRIVETRAIN_FD_1')
        print('Removed DRIVETRAIN_FD_1')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('DRIVETRAIN_FD_1')
        print('Send DRIVETRAIN_FD_1')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_D1B900:
    DTC = 0xD1B900

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('RFHUB_FD_1')
        print('Removed RFHUB_FD_1')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('RFHUB_FD_1')
        print('Send RFHUB_FD_1')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_D17600:
    DTC = 0xD17600

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('TBM_FD_1')
        print('Removed TBM_FD_1')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('TBM_FD_1')
        print('Send TBM_FD_1')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C12100:
    DTC = 0xC12100

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('BRAKE_FD_2')
        print('Removed BRAKE_FD_2')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('BRAKE_FD_2')
        print('Send BRAKE_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C29100:
    DTC = 0xC29100

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('AGSM_FD_2')
        print('Removed AGSM_FD_2')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('AGSM_FD_2')
        print('Send AGSM_FD_2')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C13900:
    DTC = 0xC13900

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('ADCM_FD_A3')
        print('Removed ADCM_FD_A3')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('ADCM_FD_A3')
        print('Send ADCM_FD_A3')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C15900:
    DTC = 0xC15900

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('CVPAM_FD_Info')
        print('Removed CVPAM_FD_Info')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('CVPAM_FD_Info')
        print('Send CVPAM_FD_Info')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_D16B00:
    DTC = 0xD16B00

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps - Maturation
        can_bus.stop_periodic_message('BCM_FD_29')
        print('Removed BCM_FD_29')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        can_bus.send_periodic_message('BCM_FD_29')
        print('Send BCM_FD_29')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED


class TestDTC_C40200:
    DTC = 0xC40200

    def test_maturation_condition(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps
        print('TRANSM_FD_4.GearDisplayForCluster = SNA')
        can_bus.send_periodic_signal('GearDisplayForCluster', 15)
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        print('TRANSM_FD_4.GearDisplayForCluster = 10')
        can_bus.send_periodic_signal('GearDisplayForCluster', 10)
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

    def test_maturation_condition_crc(self, can_bus):
        #Preconditions
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED

        #Test Steps
        print('Stopping CRC_MC computation')
        can_bus.stop_crc_mc('TRANSM_FD_4')
        time.sleep(6)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert dtc_status & TEST_FAILED

        #De-maturation
        print('Resuming CRC_MC computation')
        can_bus.resume_crc_mc('TRANSM_FD_4')
        time.sleep(1.5)
        dtcs = can_bus.check_dtc_by_status_mask(0x9)
        dtc_status = dtcs.get(self.DTC, 0)
        assert not dtc_status & TEST_FAILED
