import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree

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


# Valve control channel
# [checkbox] Enabled # Disable input when in auto mode
# ___ time_ms {pulse low/high button} # pulse polarity changes based on enabled state
# Auto [checkbox]
    # [Source channel dropdown]
    # Open [above/below dropdown] ___ pressure threshold

# XY plot
    # X source [dropdown]
    # Y source [dropdown]

def create_parameters(state):
    update_rate_param = FrequencyParameter(initial_hz=INITIAL_UPDATE_RATE_HZ, name='Graph Update Rate')
    params = [
        {'name': PRESSURE_CHANNELS_NAME, 'type': 'checklist', 'limits':
            [
                f'{i}' for i in range(state.n_channels)
            ]
         },
        update_rate_param,
    ]

    p = Parameter.create(name='Parameters', type='group', children=params)


    # Connnect graph visibility change
    graph_vis = p.param(PRESSURE_CHANNELS_NAME)

    def update_graph_visibility():
        for i in range(state.n_channels):  # Remove all graphs
            try:
                state.graph_panel.removeItem(state.graphs[i])
            except ValueError:
                pass  # Item is already gone
        for row, channel in enumerate(graph_vis.value()):  # Re-add graphs
            state.graph_panel.addItem(state.graphs[int(channel)], row=row, col=0)

    graph_vis.sigValueChanged.connect(update_graph_visibility)

    # Connect update rate change
    state.set_graph_update_time(update_rate_param.t)
    update_rate_param.t.sigValueChanged.connect(state.set_graph_update_time)

    return p
