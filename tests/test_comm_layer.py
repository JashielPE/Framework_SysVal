import pytest
import can
from unittest.mock import MagicMock, patch
from comm_layer.can_module import Can
from can import ModifiableCyclicTaskABC


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_signal(name, initial=0):
    sig = MagicMock()
    sig.name = name
    sig.initial = initial
    return sig


def _make_msg(name, frame_id, signals, cycle_time=100, is_extended=False, is_fd=True):
    msg = MagicMock()
    msg.name = name
    msg.frame_id = frame_id
    msg.signals = signals
    msg.cycle_time = cycle_time
    msg.is_extended_frame = is_extended
    msg.is_fd = is_fd
    msg.encode.return_value = b'\x00' * 8
    return msg


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_bus():
    bus = MagicMock()
    bus._periodic_tasks = []
    bus.channel_info = 'PCAN_USBBUS1'
    return bus


@pytest.fixture
def msg1():
    return _make_msg('TEST_MSG_1', 0x100, [_make_signal('SIGNAL_A', 0)], cycle_time=100)


@pytest.fixture
def msg2():
    return _make_msg('TEST_MSG_2', 0x200, [_make_signal('SIGNAL_B', 5)], cycle_time=200)


@pytest.fixture
def mock_dbc(msg1, msg2):
    dbc = MagicMock()
    dbc.messages = [msg1, msg2]
    dbc.get_message_by_name.side_effect = {'TEST_MSG_1': msg1, 'TEST_MSG_2': msg2}.get
    dbc.get_message_by_frame_id.side_effect = {0x100: msg1, 0x200: msg2}.get
    dbc.decode_message.return_value = {'SIGNAL_A': 0}
    return dbc


@pytest.fixture
def can_instance(mock_bus, mock_dbc):
    with patch('comm_layer.can_module.canBus.Bus', return_value=mock_bus), \
         patch('comm_layer.can_module.database.load_file', return_value=mock_dbc):
        instance = Can('fake_path.dbc')
    return instance


# ─── __init__ ────────────────────────────────────────────────────────────────

class TestInit:
    def test_opens_pcan_fd_bus(self, mock_bus, mock_dbc):
        with patch('comm_layer.can_module.canBus.Bus', return_value=mock_bus) as mock_cls, \
             patch('comm_layer.can_module.database.load_file', return_value=mock_dbc):
            Can('fake_path.dbc')
        kwargs = mock_cls.call_args.kwargs
        assert kwargs['interface'] == 'pcan'
        assert kwargs['fd'] is True

    def test_loads_dbc_file_with_given_path(self, mock_bus, mock_dbc):
        with patch('comm_layer.can_module.canBus.Bus', return_value=mock_bus), \
             patch('comm_layer.can_module.database.load_file', return_value=mock_dbc) as mock_load:
            Can('fake_path.dbc')
        mock_load.assert_called_once_with('fake_path.dbc')

    def test_can_messages_keys_match_dbc_message_names(self, can_instance):
        assert 'TEST_MSG_1' in can_instance.can_messages
        assert 'TEST_MSG_2' in can_instance.can_messages

    def test_signal_initial_values_are_loaded(self, can_instance):
        assert can_instance.can_messages['TEST_MSG_1']['SIGNAL_A'] == 0
        assert can_instance.can_messages['TEST_MSG_2']['SIGNAL_B'] == 5


# ─── _signalvalues_to_dict ───────────────────────────────────────────────────

class TestSignalvaluesToDict:
    def test_uses_defined_initial_value(self):
        msg = MagicMock()
        msg.signals = [_make_signal('SIG', initial=42)]
        assert Can._signalvalues_to_dict(msg) == {'SIG': 42}

    def test_defaults_to_zero_when_initial_is_none(self):
        msg = MagicMock()
        msg.signals = [_make_signal('SIG', initial=None)]
        assert Can._signalvalues_to_dict(msg) == {'SIG': 0}

    def test_handles_multiple_signals(self):
        msg = MagicMock()
        msg.signals = [
            _make_signal('A', initial=1),
            _make_signal('B', initial=None),
            _make_signal('C', initial=3),
        ]
        assert Can._signalvalues_to_dict(msg) == {'A': 1, 'B': 0, 'C': 3}


# ─── convert_bytes2hex ───────────────────────────────────────────────────────

class TestConvertBytes2Hex:
    def test_basic_conversion(self):
        assert Can.convert_bytes2hex(b'\x03\xe8') == '0x03e8'

    def test_single_zero_byte(self):
        assert Can.convert_bytes2hex(b'\x00') == '0x00'

    def test_all_ff_bytes(self):
        assert Can.convert_bytes2hex(b'\xff\xff') == '0xffff'


# ─── send_message ────────────────────────────────────────────────────────────

class TestSendMessage:
    def test_calls_bus_send(self, can_instance, mock_bus):
        can_instance.send_message(0x100, b'\x00' * 8)
        mock_bus.send.assert_called_once()

    def test_sent_message_has_correct_arbitration_id(self, can_instance, mock_bus):
        can_instance.send_message(0x100, b'\x00' * 8)
        sent = mock_bus.send.call_args.args[0]
        assert sent.arbitration_id == 0x100

    def test_catches_can_error_without_raising(self, can_instance, mock_bus):
        mock_bus.send.side_effect = can.CanError('hw error')
        can_instance.send_message(0x100, b'\x00' * 8)


# ─── raw_send_message ────────────────────────────────────────────────────────

class TestRawSendMessage:
    def test_calls_bus_send(self, can_instance, mock_bus):
        can_instance.raw_send_message(0x100, b'\x00' * 8)
        mock_bus.send.assert_called_once()

    def test_always_uses_extended_id_and_fd_regardless_of_dbc(self, can_instance, mock_bus):
        can_instance.raw_send_message(0x999, b'\x00' * 8)
        sent = mock_bus.send.call_args.args[0]
        assert sent.is_extended_id is True
        assert sent.is_fd is True

    def test_catches_can_error_without_raising(self, can_instance, mock_bus):
        mock_bus.send.side_effect = can.CanError('hw error')
        can_instance.raw_send_message(0x100, b'\x00' * 8)


# ─── send_periodic_message ───────────────────────────────────────────────────

class TestSendPeriodicMessage:
    def test_creates_task_via_send_periodic_on_first_call(self, can_instance, mock_bus):
        can_instance.send_periodic_message('TEST_MSG_1')
        mock_bus.send_periodic.assert_called_once()

    def test_stores_task_in_internal_dict(self, can_instance, mock_bus):
        task = MagicMock()
        mock_bus.send_periodic.return_value = task
        can_instance.send_periodic_message('TEST_MSG_1')
        assert can_instance._periodic_tasks[0x100] is task

    def test_period_is_cycle_time_divided_by_1000(self, can_instance, mock_bus):
        can_instance.send_periodic_message('TEST_MSG_1')  # cycle_time = 100 ms
        period = mock_bus.send_periodic.call_args.args[1]
        assert period == pytest.approx(0.1)

    def test_uses_modify_data_when_task_is_modifiable(self, can_instance):
        modifiable_task = MagicMock(spec=ModifiableCyclicTaskABC)
        can_instance._periodic_tasks[0x100] = modifiable_task
        can_instance.send_periodic_message('TEST_MSG_1')
        modifiable_task.modify_data.assert_called_once()

    def test_does_not_restart_task_when_modifiable(self, can_instance, mock_bus):
        modifiable_task = MagicMock(spec=ModifiableCyclicTaskABC)
        can_instance._periodic_tasks[0x100] = modifiable_task
        can_instance.send_periodic_message('TEST_MSG_1')
        modifiable_task.stop.assert_not_called()
        mock_bus.send_periodic.assert_not_called()

    def test_falls_back_to_stop_restart_when_not_modifiable(self, can_instance, mock_bus):
        non_modifiable_task = MagicMock()
        can_instance._periodic_tasks[0x100] = non_modifiable_task
        can_instance.send_periodic_message('TEST_MSG_1')
        non_modifiable_task.stop.assert_called_once()
        mock_bus.send_periodic.assert_called_once()


# ─── stop_periodic_message ───────────────────────────────────────────────────

class TestStopPeriodicMessage:
    def test_stops_existing_task(self, can_instance):
        task = MagicMock()
        can_instance._periodic_tasks[0x100] = task
        can_instance.stop_periodic_message('TEST_MSG_1')
        task.stop.assert_called_once()

    def test_removes_task_from_internal_dict(self, can_instance):
        can_instance._periodic_tasks[0x100] = MagicMock()
        can_instance.stop_periodic_message('TEST_MSG_1')
        assert 0x100 not in can_instance._periodic_tasks

    def test_does_nothing_when_message_was_not_periodic(self, can_instance):
        can_instance.stop_periodic_message('TEST_MSG_1')  # no task registered


# ─── send_periodic_signal ────────────────────────────────────────────────────

class TestSendPeriodicSignal:
    def test_updates_signal_value_in_state(self, can_instance):
        can_instance.send_periodic_signal('SIGNAL_A', 10)
        assert can_instance.can_messages['TEST_MSG_1']['SIGNAL_A'] == 10

    def test_creates_new_task_when_none_exists(self, can_instance, mock_bus):
        can_instance.send_periodic_signal('SIGNAL_A', 10)
        mock_bus.send_periodic.assert_called_once()

    def test_uses_modify_data_when_task_already_exists(self, can_instance, mock_bus):
        modifiable_task = MagicMock(spec=ModifiableCyclicTaskABC)
        can_instance._periodic_tasks[0x100] = modifiable_task
        can_instance.send_periodic_signal('SIGNAL_A', 10)
        modifiable_task.modify_data.assert_called_once()
        mock_bus.send_periodic.assert_not_called()

    def test_unknown_signal_does_not_send_anything(self, can_instance, mock_bus):
        can_instance.send_periodic_signal('NON_EXISTENT', 99)
        mock_bus.send_periodic.assert_not_called()


# ─── send_signal ─────────────────────────────────────────────────────────────

class TestSendSignal:
    def test_updates_signal_in_state(self, can_instance):
        can_instance.send_signal('TEST_MSG_1', 'SIGNAL_A', 7)
        assert can_instance.can_messages['TEST_MSG_1']['SIGNAL_A'] == 7

    def test_sends_message_exactly_once(self, can_instance, mock_bus):
        can_instance.send_signal('TEST_MSG_1', 'SIGNAL_A', 7)
        mock_bus.send.assert_called_once()

    def test_does_not_trigger_periodic_send(self, can_instance, mock_bus):
        can_instance.send_signal('TEST_MSG_1', 'SIGNAL_A', 7)
        mock_bus.send_periodic.assert_not_called()


# ─── check_message ───────────────────────────────────────────────────────────

class TestCheckMessage:
    def test_returns_message_when_id_matches(self, can_instance, mock_bus):
        incoming = MagicMock()
        incoming.arbitration_id = 0x100
        mock_bus.recv.return_value = incoming
        assert can_instance.check_message(0x100) is incoming

    def test_returns_false_when_timeout_expires(self, can_instance, mock_bus):
        mock_bus.recv.return_value = None
        assert can_instance.check_message(0x100, timeout=0.15) is False

    def test_skips_messages_with_wrong_arbitration_id(self, can_instance, mock_bus):
        wrong = MagicMock(); wrong.arbitration_id = 0x999
        right = MagicMock(); right.arbitration_id = 0x100
        mock_bus.recv.side_effect = [wrong, right]
        assert can_instance.check_message(0x100) is right

    def test_continues_after_recv_returns_none(self, can_instance, mock_bus):
        right = MagicMock(); right.arbitration_id = 0x100
        mock_bus.recv.side_effect = [None, None, right]
        assert can_instance.check_message(0x100) is right


# ─── trace_timeout ───────────────────────────────────────────────────────────

class TestTraceTimeout:
    def test_returns_true_after_timeout(self, can_instance, mock_bus):
        mock_bus.recv.return_value = None
        assert can_instance.trace_timeout(timeout=0.15) is True

    def test_prints_received_messages(self, can_instance, mock_bus, capsys):
        incoming = MagicMock()
        incoming.arbitration_id = 0x100
        incoming.__str__ = lambda self: 'Frame(0x100)'
        mock_bus.recv.side_effect = [incoming, None, None, None, None, None]
        can_instance.trace_timeout(timeout=0.15)
        captured = capsys.readouterr()
        assert 'Frame(0x100)' in captured.out


# ─── init_CAN_messages ───────────────────────────────────────────────────────

class TestInitCANMessages:
    def test_decodes_each_message_using_dbc(self, can_instance, mock_dbc):
        can_instance.init_CAN_messages({'TEST_MSG_1': [0x00] * 8})
        mock_dbc.decode_message.assert_called_with('TEST_MSG_1', bytes([0x00] * 8))

    def test_updates_internal_state_with_decoded_values(self, can_instance, mock_dbc):
        mock_dbc.decode_message.return_value = {'SIGNAL_A': 42}
        can_instance.init_CAN_messages({'TEST_MSG_1': [0x00] * 8})
        assert can_instance.can_messages['TEST_MSG_1'] == {'SIGNAL_A': 42}

    def test_starts_periodic_send_for_each_message(self, can_instance, mock_bus):
        can_instance.init_CAN_messages({
            'TEST_MSG_1': [0x00] * 8,
            'TEST_MSG_2': [0x00] * 8,
        })
        assert mock_bus.send_periodic.call_count == 2


# ─── Context manager ─────────────────────────────────────────────────────────

class TestContextManager:
    def test_enter_returns_self(self, can_instance):
        assert can_instance.__enter__() is can_instance

    def test_exit_stops_all_periodic_tasks(self, can_instance, mock_bus):
        can_instance.__exit__(None, None, None)
        mock_bus.stop_all_periodic_tasks.assert_called_once()

    def test_exit_clears_internal_task_dict(self, can_instance):
        can_instance._periodic_tasks[0x100] = MagicMock()
        can_instance.__exit__(None, None, None)
        assert len(can_instance._periodic_tasks) == 0

    def test_exit_shuts_down_bus(self, can_instance, mock_bus):
        can_instance.__exit__(None, None, None)
        mock_bus.shutdown.assert_called_once()

    def test_shutdown_called_even_when_test_raises_exception(self, mock_bus, mock_dbc):
        with patch('comm_layer.can_module.canBus.Bus', return_value=mock_bus), \
             patch('comm_layer.can_module.database.load_file', return_value=mock_dbc):
            try:
                with Can('fake_path.dbc'):
                    raise ValueError('simulated failure')
            except ValueError:
                pass
        mock_bus.shutdown.assert_called_once()


# ─── _crc8_j1850 ─────────────────────────────────────────────────────────────

class TestCrc8J1850:
    def test_returns_integer(self):
        result = Can._crc8_j1850(b'\x00' * 8)
        assert isinstance(result, int)

    def test_same_input_gives_same_output(self):
        data = b'\x01\x02\x03\x04'
        assert Can._crc8_j1850(data) == Can._crc8_j1850(data)

    def test_different_input_gives_different_output(self):
        assert Can._crc8_j1850(b'\x00' * 8) != Can._crc8_j1850(b'\xFF' * 8)

    def test_result_is_single_byte(self):
        result = Can._crc8_j1850(b'\xAB\xCD\xEF')
        assert 0x00 <= result <= 0xFF

    def test_known_value(self):
        # CRC-8 J1850: data=0x00, expected=0x2F (poly=0x1D, init=0xFF, xorout=0xFF)
        assert Can._crc8_j1850(b'\x00') == 0x2F


# ─── build_crc_msgs ──────────────────────────────────────────────────────────

class TestBuildCrcMsgs:
    def test_registers_message_in_crc_set(self, can_instance):
        can_instance.build_crc_msgs('TEST_MSG_1')
        assert 'TEST_MSG_1' in can_instance._crc_messages

    def test_initializes_counter_to_zero(self, can_instance):
        can_instance.build_crc_msgs('TEST_MSG_1')
        assert can_instance._message_counters['TEST_MSG_1'] == 0

    def test_does_not_reset_existing_counter(self, can_instance):
        can_instance._message_counters['TEST_MSG_1'] = 7
        can_instance.build_crc_msgs('TEST_MSG_1')
        assert can_instance._message_counters['TEST_MSG_1'] == 7

    def test_registers_multiple_messages(self, can_instance):
        can_instance.build_crc_msgs('TEST_MSG_1', 'TEST_MSG_2')
        assert 'TEST_MSG_1' in can_instance._crc_messages
        assert 'TEST_MSG_2' in can_instance._crc_messages

    def test_transitions_already_transmitting_message(self, can_instance):
        existing_task = MagicMock()
        can_instance._periodic_tasks[0x100] = existing_task
        can_instance.build_crc_msgs('TEST_MSG_1')
        existing_task.stop.assert_called_once()
        assert 0x100 not in can_instance._periodic_tasks

    def test_starts_crc_thread_when_message_was_transmitting(self, can_instance):
        can_instance._periodic_tasks[0x100] = MagicMock()
        can_instance.build_crc_msgs('TEST_MSG_1')
        assert 0x100 in can_instance._crc_stop_events


# ─── stop_crc_mc ─────────────────────────────────────────────────────────────

class TestStopCrcMc:
    def test_stops_crc_thread(self, can_instance):
        stop_event = MagicMock()
        can_instance._crc_stop_events[0x100] = stop_event
        can_instance._crc_threads[0x100] = MagicMock()
        can_instance._crc_messages.add('TEST_MSG_1')
        can_instance._message_counters['TEST_MSG_1'] = 0
        can_instance.stop_crc_mc('TEST_MSG_1')
        stop_event.set.assert_called_once()

    def test_removes_message_from_crc_set(self, can_instance):
        can_instance._crc_messages.add('TEST_MSG_1')
        can_instance._message_counters['TEST_MSG_1'] = 0
        can_instance.stop_crc_mc('TEST_MSG_1')
        assert 'TEST_MSG_1' not in can_instance._crc_messages

    def test_starts_normal_periodic_after_stopping(self, can_instance, mock_bus):
        can_instance._crc_messages.add('TEST_MSG_1')
        can_instance._message_counters['TEST_MSG_1'] = 0
        can_instance.stop_crc_mc('TEST_MSG_1')
        mock_bus.send_periodic.assert_called_once()

    def test_safe_when_no_crc_thread_running(self, can_instance):
        can_instance._message_counters['TEST_MSG_1'] = 0
        can_instance.stop_crc_mc('TEST_MSG_1')  # must not raise


# ─── resume_crc_mc ───────────────────────────────────────────────────────────

class TestResumeCrcMc:
    def test_adds_message_back_to_crc_set(self, can_instance):
        can_instance._message_counters['TEST_MSG_1'] = 3
        can_instance.resume_crc_mc('TEST_MSG_1')
        assert 'TEST_MSG_1' in can_instance._crc_messages

    def test_stops_existing_periodic_task(self, can_instance):
        existing_task = MagicMock()
        can_instance._periodic_tasks[0x100] = existing_task
        can_instance._message_counters['TEST_MSG_1'] = 0
        can_instance.resume_crc_mc('TEST_MSG_1')
        existing_task.stop.assert_called_once()

    def test_starts_crc_thread(self, can_instance):
        can_instance._message_counters['TEST_MSG_1'] = 0
        can_instance.resume_crc_mc('TEST_MSG_1')
        assert 0x100 in can_instance._crc_stop_events

    def test_preserves_existing_counter_value(self, can_instance):
        can_instance._message_counters['TEST_MSG_1'] = 9
        can_instance.resume_crc_mc('TEST_MSG_1')
        assert can_instance._message_counters['TEST_MSG_1'] == 9

    def test_initializes_counter_if_not_present(self, can_instance):
        can_instance.resume_crc_mc('TEST_MSG_1')
        assert can_instance._message_counters.get('TEST_MSG_1') == 0
