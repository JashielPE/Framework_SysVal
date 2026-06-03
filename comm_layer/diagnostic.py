import time
from comm_layer.can_module import Can
from config.config import diag_messages


class Diagnostics(Can):

    def _wait_for_response(self, msg_id: int, max_pending: int = 10):
        for _ in range(max_pending):
            response = self.check_message(msg_id)
            if response is False:
                return False
            if response.data[1] == 0x7F and len(response.data) > 3 and response.data[3] == 0x78:
                continue
            return response
        return False

    def _send_session_request(self, sub_function: int) -> str:
        self.send_message(diag_messages['diag_req_ipc'], [0x2, 0x10, sub_function])
        response = self._wait_for_response(diag_messages['diag_res_ipc'])
        if response is False:
            print('Session 0x{:X} — No response'.format(sub_function))
            return 'No response'
        result = 'Positive response' if response.data[1] == 0x50 else 'Negative response'
        print('Session 0x{:X} — {} | data: {}'.format(sub_function, result, response.data.hex()))
        return result

    def default_session(self) -> str:
        return self._send_session_request(0x01)

    def extended_session(self) -> str:
        return self._send_session_request(0x03)

    def check_dtc_by_status_mask(self, mask=0x9):
        self.send_message(diag_messages['diag_req_ipc'], [0x3, 0x19, 0x02, mask, 0x00, 0x00, 0x00, 0x00])
        msg_resp = self._wait_for_response(diag_messages['diag_res_ipc'])
        if msg_resp is False:
            return None

        if msg_resp.data[0] == 0x10:
            self.send_message(diag_messages['diag_req_ipc'], [0x30, 0x0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            data_length = ((msg_resp.data[0] & 0x0F) << 8) | msg_resp.data[1]
            payload = bytearray(msg_resp.data[2:])
            num_frames = data_length // 7
            for _ in range(num_frames):
                cf = self.check_message(diag_messages['diag_res_ipc'])
                if cf:
                    payload += bytearray(cf.data[1:])
            payload = bytes(payload[:data_length])
        elif msg_resp.data[0] == 0x00:
            length = msg_resp.data[1]
            payload = bytes(msg_resp.data[2:2 + length])
        else:
            length = msg_resp.data[0] & 0x0F
            payload = bytes(msg_resp.data[1:1 + length])

        if len(payload) < 3 or payload[0] != 0x59:
            return None

        dtcs = {}
        dtc_data = payload[3:]
        for i in range(0, len(dtc_data) - 3, 4):
            dtc = (dtc_data[i] << 16) | (dtc_data[i + 1] << 8) | dtc_data[i + 2]
            status = dtc_data[i + 3]
            dtcs[dtc] = status
            print('DTC: {:06X} | Status: {:02X}'.format(dtc, status))

        return dtcs

    def clear_all_dtc(self) -> str:
        self.send_message(diag_messages['diag_req_ipc'], [0x4, 0x14, 0xFF, 0xFF, 0xFF])
        msg_resp = self._wait_for_response(diag_messages['diag_res_ipc'])
        if msg_resp is False:
            print('Clear DTC — No response')
            return 'No response'
        result = 'Positive response' if msg_resp.data[1] == 0x54 else 'Negative response'
        print('Clear DTC — {} | data: {}'.format(result, msg_resp.data.hex()))
        return result

    def wait_for_dtc_bit(self, dtc: int, bit: int, timeout: float = 30, interval: float = 0.5) -> float | None:
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                return None
            dtcs = self.check_dtc_by_status_mask()
            if dtcs and dtc in dtcs and dtcs[dtc] & bit:
                return elapsed
            time.sleep(interval)

    @staticmethod
    def to_hex_str(value: int) -> str:
        return format(value, 'X')

    @staticmethod
    def from_hex_str(hex_str: str) -> int:
        return int(hex_str, 16)
