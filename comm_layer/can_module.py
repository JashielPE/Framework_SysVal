import can as canBus
import time
import threading
from cantools import database


class Can:
    def __init__(self, db_path: str) -> None:
        self.bus = canBus.Bus(interface='pcan',
                              fd=True,
                              f_clock_mhz=80,
                              nom_brp=1,
                              nom_tseg1=127,
                              nom_tseg2=32,
                              nom_sjw=32,
                              data_brp=1,
                              data_tseg1=31,
                              data_tseg2=8,
                              data_sjw=8)
        self.dbc = database.load_file(db_path)
        self.can_messages = {}
        self._periodic_tasks = {}
        self._crc_messages: set = set()
        self._message_counters: dict = {}
        self._crc_threads: dict = {}
        self._crc_stop_events: dict = {}
        self._obtaining_can_messages_from_dbc()

    def _obtaining_can_messages_from_dbc(self):
        for message in self.dbc.messages:
            self.can_messages[message.name] = self._signalvalues_to_dict(message)

    def send_message(self, arbitration_id, data):
        msg_dbc = self.dbc.get_message_by_frame_id(arbitration_id)
        msg = canBus.Message(arbitration_id=arbitration_id, data=data, is_extended_id=msg_dbc.is_extended_frame,
                             is_fd=msg_dbc.is_fd)
        print(msg)
        try:
            self.bus.send(msg)
            print(f"Message sent on {self.bus.channel_info}")
        except canBus.CanError:
            print('Message NOT sent')

    def raw_send_message(self, arbitration_id, data):
        msg = canBus.Message(arbitration_id=arbitration_id, data=data, is_extended_id=True, is_fd=True)
        try:
            self.bus.send(msg)
            print(f"Message sent on {self.bus.channel_info}")
        except canBus.CanError:
            print('Message NOT sent')

    def send_periodic_message(self, message: str):
        msg_db = self.dbc.get_message_by_name(message)
        period = msg_db.cycle_time / 1000
        if message in self._crc_messages:
            self._start_crc_task(message, msg_db, period)
            return
        data = msg_db.encode(self.can_messages[message])
        msg = canBus.Message(arbitration_id=msg_db.frame_id, data=data, is_extended_id=msg_db.is_extended_frame,
                             is_fd=msg_db.is_fd)
        existing = self._periodic_tasks.get(msg_db.frame_id)
        if existing is not None:
            if isinstance(existing, canBus.ModifiableCyclicTaskABC):
                existing.modify_data(msg)
                return
            existing.stop()
        self._periodic_tasks[msg_db.frame_id] = self.bus.send_periodic(msg, period)

    def _start_crc_task(self, message: str, msg_db, period: float):
        frame_id = msg_db.frame_id
        if frame_id in self._crc_stop_events:
            self._crc_stop_events.pop(frame_id).set()
            self._crc_threads.pop(frame_id, None)
        stop_event = threading.Event()
        self._crc_stop_events[frame_id] = stop_event

        def _send_loop():
            while True:
                data = bytearray(msg_db.encode(self.can_messages[message]))
                counter = self._message_counters[message]
                data[22] = (data[22] & 0xF0) | (counter & 0x0F)
                data[23] = self._crc8_j1850(bytes(data[:23]))
                self._message_counters[message] = (counter + 1) % 16
                try:
                    self.bus.send(canBus.Message(
                        arbitration_id=frame_id,
                        data=bytes(data),
                        is_extended_id=msg_db.is_extended_frame,
                        is_fd=msg_db.is_fd
                    ))
                except canBus.CanError:
                    pass
                if stop_event.wait(period):
                    break

        thread = threading.Thread(target=_send_loop, daemon=True)
        self._crc_threads[frame_id] = thread
        thread.start()

    def stop_periodic_message(self, message: str):
        msg_db = self.dbc.get_message_by_name(message)
        frame_id = msg_db.frame_id
        if frame_id in self._crc_stop_events:
            self._crc_stop_events.pop(frame_id).set()
            self._crc_threads.pop(frame_id, None)
            return
        task = self._periodic_tasks.pop(frame_id, None)
        if task is not None:
            task.stop()

    def send_periodic_signal(self, signal: str, value: int):
        for can_mes, sub_dict in self.can_messages.items():
            if signal in sub_dict:
                self.can_messages[can_mes][signal] = value
                self.send_periodic_message(can_mes)

    def get_signal(self, signal: str):
        for msg, signals in self.can_messages.items():
            if signal in signals:
                return self.can_messages[msg][signal]
        return None

    def send_signal(self, message: str, signal: str, value: int):
        self.can_messages[message][signal] = value
        msg_db = self.dbc.get_message_by_name(message)
        data = msg_db.encode(self.can_messages[message])
        self.send_message(msg_db.frame_id, data)

    def check_message(self, message_id, timeout=5):
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print('Message is not find in CAN bus')
                return False
            msg = self.bus.recv(timeout=0.1)
            if msg is None:
                continue
            if msg.arbitration_id == message_id:
                #print(msg)
                return msg

    def trace_timeout(self, timeout=3):
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print('Stop Trace')
                return True
            msg = self.bus.recv(timeout=0.1)
            if msg is not None:
                print(msg)

    def init_CAN_messages(self, can_messages: dict):
        for message, data in can_messages.items():
            self.can_messages[message] = self.dbc.decode_message(message, bytes(data))
            self.send_periodic_message(message)

    def build_crc_msgs(self, *messages: str):
        for message in messages:
            self._crc_messages.add(message)
            if message not in self._message_counters:
                self._message_counters[message] = 0
            msg_db = self.dbc.get_message_by_name(message)
            frame_id = msg_db.frame_id
            task = self._periodic_tasks.pop(frame_id, None)
            if task is not None:
                task.stop()
                self._start_crc_task(message, msg_db, msg_db.cycle_time / 1000)

    def stop_crc_mc(self, message: str):
        msg_db = self.dbc.get_message_by_name(message)
        frame_id = msg_db.frame_id
        if frame_id in self._crc_stop_events:
            self._crc_stop_events.pop(frame_id).set()
            self._crc_threads.pop(frame_id, None)
        self._crc_messages.discard(message)
        self.send_periodic_message(message)

    def resume_crc_mc(self, message: str):
        msg_db = self.dbc.get_message_by_name(message)
        frame_id = msg_db.frame_id
        task = self._periodic_tasks.pop(frame_id, None)
        if task is not None:
            task.stop()
        self._crc_messages.add(message)
        if message not in self._message_counters:
            self._message_counters[message] = 0
        self._start_crc_task(message, msg_db, msg_db.cycle_time / 1000)

    @staticmethod
    def _crc8_j1850(data: bytes) -> int:
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1D) if crc & 0x80 else (crc << 1)
                crc &= 0xFF
        return crc ^ 0xFF

    @staticmethod
    def _signalvalues_to_dict(msg):
        dict_sig_val = {}
        for signal in msg.signals:
            sig_initial = 0 if signal.initial is None else signal.initial
            dict_sig_val[signal.name] = sig_initial
        return dict_sig_val

    @staticmethod
    def convert_bytes2hex(data: bytes):
        hexstring = data.hex()
        return f"0x{hexstring}"

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        for stop_event in self._crc_stop_events.values():
            stop_event.set()
        self._crc_stop_events.clear()
        self._crc_threads.clear()
        self.bus.stop_all_periodic_tasks()
        self._periodic_tasks.clear()
        self.bus.shutdown()
