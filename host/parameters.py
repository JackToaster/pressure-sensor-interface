import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree

from app_state import AppState

PRESSURE_CHANNELS_NAME = 'Pressure Channels'
def create_parameters(state: AppState):
    params = [
        {'name': PRESSURE_CHANNELS_NAME, 'type': 'checklist', 'limits':
            [
                f'{i}' for i in range(state.n_channels)
            ]
         },

    ]

    p = Parameter.create(name='Parameters', type='group', children=params)

    def update_graph_visibility(param, changes):
        for param, change, data in changes:

            if param.name() == PRESSURE_CHANNELS_NAME:  # Visible graph channels updated
                for i in range(state.n_channels):  # Remove all graphs
                    try:
                        state.graph_panel.removeItem(state.graphs[i])
                    except ValueError:
                        pass  # Item is already gone
                for row, channel in enumerate(data):  # Re-add graphs
                    state.graph_panel.addItem(state.graphs[int(channel)], row=row, col=0)



    p.sigTreeStateChanged.connect(update_graph_visibility)

    return p

