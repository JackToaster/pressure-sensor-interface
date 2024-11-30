import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree
import serial

import serial_comms
from serial_comms import create_tx_autoctl_packet, create_tx_set_packet

# from monitor_GUI import Application

PRESSURE_CHANNELS_NAME = 'Pressure Channels'
INITIAL_UPDATE_RATE_HZ = 10


class FrequencyParameter(pTypes.GroupParameter):
    def __init__(self, initial_hz=1, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        self.addChild({'name': 'Frequency', 'type': 'float', 'value': initial_hz, 'suffix': 'Hz', 'siPrefix': True})
        self.addChild({'name': 'Time', 'type': 'float', 'value': 1 / initial_hz, 'suffix': 's', 'siPrefix': True})
        self.freq = self.param('Frequency')
        self.t = self.param('Time')
        self.freq.sigValueChanged.connect(self.freq_changed)
        self.t.sigValueChanged.connect(self.t_changed)

    def freq_changed(self):
        self.t.setValue(1.0 / self.freq.value(), blockSignal=self.t_changed)

    def t_changed(self):
        self.freq.setValue(1.0 / self.t.value(), blockSignal=self.freq_changed)


class ChannelCtlParameter(pTypes.GroupParameter):
    def __init__(self, parent_app, channel=0, **opts):
        self.channel = channel
        opts['name'] = f'Channel {channel}'
        opts['type'] = 'bool'
        opts['value'] = True
        opts['expanded'] = False
        pTypes.GroupParameter.__init__(self, **opts)
        self.parent_app = parent_app

        self.state_param = self.addChild({'name': 'State', 'type': 'bool', 'value': False})
        self.auto_param = self.addChild({'name': 'Auto', 'type': 'bool', 'value': False})
        self.source_channel_param = self.auto_param.addChild(
            {'name': 'Source Channel', 'type': 'list', 'limits': ['None'] + list(range(8))})
        self.above_below_param = self.auto_param.addChild(
            {'name': 'Open', 'type': 'list', 'limits': ['Above', 'Below']})
        self.pressure_param = self.auto_param.addChild(
            {'name': 'Pressure', 'type': 'float', 'value': 0, 'suffix': 'Pa', 'siPrefix': True})
        self.hyst_param = self.auto_param.addChild(
            {'name': 'Hysteresis', 'type': 'float', 'value': 0, 'suffix': 'Pa', 'siPrefix': True})

        auto_param_list = [
            self.auto_param, self.source_channel_param, self.above_below_param, self.pressure_param, self.hyst_param
        ]

        self.auto_param.sigValueChanged.connect(self.toggle_auto)

        # Connect all auto params to send update
        for p in auto_param_list:
            p.sigValueChanged.connect(self.send_auto_cmd)

        self.state_param.sigValueChanged.connect(self.send_manual_cmd)

    def toggle_auto(self):
        is_auto = self.auto_param.value()

        if is_auto:
            self.state_param.setWritable(False)
        else:
            self.state_param.setWritable(True)

    def send_auto_cmd(self):
        if self.parent_app.serial_connection is None:
            print('Cannot set auto state while disconnected')
            return

        auto_mode = self.auto_param.value()
        source_channel = self.source_channel_param.value()
        if source_channel == 'None':
            print('Source set to none, disabling auto mode')
            source_channel = 0
            auto_mode = False
        open_above = self.above_below_param.value() == 'Above'
        tx_packet = create_tx_autoctl_packet(self.channel, auto_mode, open_above,
                                             source_channel, self.pressure_param.value(),
                                             self.hyst_param.value())
        print(f'Setting auto state for channel {self.channel}')
        self.parent_app.serial_connection.write(tx_packet)

    def send_manual_cmd(self):
        if self.parent_app.serial_connection is None:
            print('Cannot set auto state while disconnected')
            return
        tx_packet = create_tx_set_packet(
            {self.channel:
                 serial_comms.CHANNEL_SET if self.state_param.value() else serial_comms.CHANNEL_RESET
             })
        print(f'Setting valve channel {self.channel} state')
        self.parent_app.serial_connection.write(tx_packet)

# Valve control channel
# [checkbox] Enabled # Disable input when in auto mode
# ___ time_ms {pulse low/high button} # pulse polarity changes based on enabled state
# Auto [checkbox]
# [Source channel dropdown]
# Open [above/below dropdown] ___ pressure threshold

# XY plot
# X source [dropdown]
# Y source [dropdown]
# color by [valve channel dropdown] # color points based on state of a valve?

class GuiParameters(pTypes.GroupParameter):
    def __init__(self, parent, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        opts['name'] = 'test'
        pTypes.GroupParameter.__init__(self, **opts)

        self.parent = parent

        self.update_rate_param = FrequencyParameter(initial_hz=INITIAL_UPDATE_RATE_HZ, name='Graph Update Rate')
        test_button_param = pTypes.ActionParameter(name='test123')

        self.channel_ctls = [ChannelCtlParameter(parent, i) for i in range(8)]

        self.graph_vis = self.addChild(
            {'name': PRESSURE_CHANNELS_NAME, 'type': 'checklist', 'limits':
                [
                    f'{i}' for i in range(parent.n_channels)
                ]
             })
        self.addChild(self.update_rate_param)

        self.addChild({'name': 'Device Controls', 'type': 'group', 'children': self.channel_ctls})

        self.graph_vis.sigValueChanged.connect(self.update_graph_visibility)

        # Connect update rate change
        parent.set_graph_update_time(self.update_rate_param.t)
        self.update_rate_param.t.sigValueChanged.connect(parent.set_graph_update_time)

        def button_pressed():
            if parent.serial_connection is not None:
                ser: serial.Serial = parent.serial_connection
                try:
                    ser.write(b'test123\n')
                except Exception as e:
                    print(e)

        test_button_param.sigActivated.connect(button_pressed)

    def update_graph_visibility(self):
        for i in range(self.parent.n_channels):  # Remove all graphs
            try:
                self.parent.graph_panel.removeItem(self.parent.graphs[i])
            except ValueError:
                pass  # Item is already gone
        for row, channel in enumerate(self.graph_vis.value()):  # Re-add graphs
            self.parent.graph_panel.addItem(self.parent.graphs[int(channel)], row=row, col=0)

    def set_valve_states(self, states):
        for ctl, state in zip(self.channel_ctls, states):
            ctl.state_param.setValue(state, blockSignal=ctl.send_manual_cmd)
