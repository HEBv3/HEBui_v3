#!/usr/bin/env python3

import bz2
import pickle
from pathlib import Path
import base64
import datetime
import io
import ast
import copy
import re
import sys

from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL
from dash import callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

px.defaults.template = 'simple_white'

app = Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css"],
    suppress_callback_exceptions=True)
app.title = 'pyHEB'

# load setups
setups_path = Path('data/setups.pickle')
default_setup_path = Path('data/setups.pickle.default')
if default_setup_path.exists():
    with default_setup_path.open(mode='rb') as setups_file:
        SETUPS = pickle.load(setups_file)
else:
    # if not file is present, create it
    SETUPS = {}

vin_path = Path('data/vintage.pickle')
if vin_path.exists():
    with vin_path.open(mode='rb') as vin_file:
        VINTAGE = pickle.load(vin_file)

def store_setups():
    with setups_path.open(mode='wb') as setups_file:
        pickle.dump(SETUPS, setups_file)

# SETUPS schema:
"""
SETUPS[setup_name]{
    'name': str,
    'start_year': int,
    'end_year': int,
    'input_csvs': [table_name]{
        'filename': str,
        'df_data': base64string,
        'date': str
    },
    'scenarios': [id]{
        'id': int
        'name': str,
        'pv': bool
    },
}
"""

RESULTS = {}

"""
RESULTS[setup_name]{
    'scenarios':
        [sid]: heb.Scenario
}
"""

# ICONS
chevron_right = html.I(className="bi bi-chevron-compact-right text-secondary")
spreadsheet_icon = html.I(className="bi bi-file-earmark-spreadsheet text-success h2")
spreadsheet_icon_disabled = html.I(className="bi bi-file-earmark-spreadsheet text-light h2")
delete_icon = html.I(className="bi bi-trash text-danger h2")
delete_icon_disabled = html.I(className="bi bi-trash text-light h2")
edit_icon = html.I(className="bi bi-pencil-square text-dark h2")
download_icon = html.I(className="bi bi-download text-dark h2")
upload_icon = html.I(className="bi bi-upload text-dark h2")
info_icon = html.I(className="bi bi-info-circle")
toggle_on_icon = html.I(className="bi bi-toggle-on")
toggle_off_icon = html.I(className="bi bi-toggle-off")

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Scenarios", href="/scenarios")),
        dbc.NavItem(dbc.NavLink("Calculate", href="/calculate")),
        dbc.NavItem(dbc.NavLink("Visualize", href="/visualize")),
        #dbc.NavItem(dbc.NavLink("Documentation", href="https://doi.org/10.1007/978-3-030-99177-7_7", target="_blank")) #, disabled=True)),
        dbc.NavItem(dbc.NavLink("Documentation", href="https://github.com/HEBv3/HEBui_v3/tree/main/documentation", target="_blank")) #, disabled=True)),
    ],
    brand="pyHEB",
    brand_href="/",
    color="primary",
    dark=True,
    sticky='top'
)


def render_header(actual):
    header_items = []

    for step in ['scenarios', 'calculate', 'visualize']:
        if actual == step:
            step_text = html.Span(step.title(), className="text-primary")
        else:
            step_text = html.A(html.Span(step.title(), className="text-secondary"), href="/{}".format(step))
        header_items.append(step_text)
        header_items.append(chevron_right)

    # remove last chevron
    del header_items[-1]

    return html.H1(
        html.Span(
            header_items,
            className="align-middle"
        ), className='mb-3'
    )

def render_welcome():
    disclaimer = """
    py3CSEP HEB is the python implementation of the 3CSEP HEB model developed by
    the Department of Environmental Sciences and Policy at the Central European University

    ### License & Credit
    Copyright (C) 2022 CEU

    This version of the py3CSEP HEB (HEBui v3.0) and the model data are released under the GNU Affero General Public License.

    This module was developed by Benedek Kiss and Zoltán Hajnal at the
    [Department of Environmental Sciences and Policy](https://envsci.ceu.edu/)
    of the [Central European University](https://www.ceu.edu/)
    within the research project [SENTINEL](https://sentinel.energy/).

    This software uses open-source packages.
    """
    content = [
        html.H1(
            html.Span(
                'Welcome to pyHEB user interface',
                className="align-middle"
            ), className='mb-3'
        ),
        html.Br(),
        dcc.Markdown(disclaimer),
        html.Br(),
        dbc.Button('Get Started', href="/scenarios", color='primary')
    ]
    return content

def create_scenario_name_form_row(sid, name=None, pv=False):
    if pv:
        pv_toggle = [1]
    else:
        pv_toggle = []
    form_row = dbc.Row(
        [
            dbc.Label(html.H4(sid, className="text-center"),
                      html_for={'type': 'scenario-name', 'index': sid},
                      width=1,
                      align='center'),
            dbc.Col(
                dbc.Input(placeholder="Name of the scenario...", disabled = True, value=name,
                          id={'type': 'scenario-name', 'index': sid}, debounce=True),
                width=5,
                align='center'
            ),
            dbc.Col(
                dbc.Checklist(
                    options=[
                        {'label': '', 'value': 1},
                    ],
                    value=pv_toggle,
                    id={'type': 'scenario-pv-toggle', 'index': sid},
                    switch=True
                ),
                width=2,
                align='center'
            )
        ], className="p-2"
    )
    return form_row


def create_scenario_name_form(scenario_ids, scenario_names, pv_infos):
    content = [
        dbc.Row([
            dbc.Col(html.B('Scenario ID', className="text-align:center"), width=1),
            dbc.Col(html.B('Scenario Name'), width=5),
            dbc.Col([html.B('Subtract PV ', className="text-align:center"), info_icon], width=2, id='pv-info'),
            dbc.Tooltip('If toggled, onsite PV production will be subtracted from the energy consumption',
                        target='pv-info')
        ], className="p-3")
    ]
    for sid, name, pv in zip(scenario_ids, scenario_names, pv_infos):
        content.append(
            create_scenario_name_form_row(sid, name, pv)
        )
    content.append(
        dbc.Row([
            dbc.Col(dbc.Button("Save scenarios", id="scenario-save-button", className="mxy-2"), width=2),
        ])
    )
    return content


def render_scenarios():
    dropdown_value = None
    for setup_name in SETUPS:
        if 'scenarios' not in SETUPS[setup_name]:
            dropdown_value = setup_name
            break
        else:
            dropdown_value = setup_name

    content = [
        render_header('scenarios'),
        dbc.Row([
            dbc.Col(html.H5('Setup'), width=1),
            dbc.Col(dcc.Dropdown(
                id='scenario-setup-dropdown',
                options=[{'label': SETUPS[setup]['name'], 'value': setup} for setup in SETUPS],
                placeholder="Select a setup...",
                value=dropdown_value,
                disabled = True
            ), width=7),
        ], align='center'),
        dbc.Spinner(html.Div(id='scenario-name-form')),
        dbc.Row(
            dbc.Col(id='scenario-name-alert', width=8),
            className='mt-2'
        ),
        dbc.Row(
            dbc.Col(id='scenario-save-alert', width=8),
            className='mt-2'
        ),
    ]
    return content


def render_output_rows(setup_name):
    setup = SETUPS[setup_name]
    rows = [
        dbc.Row([
            dbc.Col(html.B(setup['scenarios'][sid]['name']), width=2),
            dbc.Col(['Floor area',
                     dbc.Button(spreadsheet_icon, color='link', size='md', className='m-1',
                                id={'type': 'result_download-button',
                                    'target': 'floor_area',
                                    'index': setup_name,
                                    'sid': sid}),
                     dcc.Download(id={'type': 'download-result-csv', 'target': 'floor_area',
                                      'index': setup_name, 'sid': sid}),
                     ], width=2),
            dbc.Col([html.Span('Energy'),
                     dbc.Button(spreadsheet_icon, color='link', size='md', className='m-1',
                                id={'type': 'result_download-button',
                                    'target': 'energy',
                                    'index': setup_name,
                                    'sid': sid}),
                     dcc.Download(id={'type': 'download-result-csv', 'target': 'energy',
                                      'index': setup_name, 'sid': sid}),
                     ], width=2),
            dbc.Col([html.Span('Emissions'),
                     dbc.Button(spreadsheet_icon, color='link', size='md', className='m-1',
                                id={'type': 'result_download-button',
                                    'target': 'emissions',
                                    'index': setup_name,
                                    'sid': sid}),
                     dcc.Download(id={'type': 'download-result-csv', 'target': 'emissions',
                                      'index': setup_name, 'sid': sid}),
                     ], width=2),
        ], align="center")
        for sid in setup['scenarios']
    ]
    return rows


def render_calculate_row(setup_name):

    setup = SETUPS[setup_name]

    if setup_name in RESULTS:
        outputs = render_output_rows(setup_name)
        button_outline = True
        button_color = 'secondary'
        button_disabled = True
        del_icon = delete_icon
        del_disabled = False
    elif 'scenarios' in setup:
        outputs = None
        button_outline = False
        button_color = 'success'
        button_disabled = False
        del_icon = delete_icon_disabled
        del_disabled = True
    else:
        outputs = None
        button_outline = False
        button_color = 'warning'
        button_disabled = True
        del_icon = delete_icon_disabled
        del_disabled = True

    row = html.Div([
        html.H4('Setup: ' + setup['name']),
        dbc.Row([
            dbc.Col(dbc.Button("Calculation:", id={'type': 'calc-button', 'index': setup_name},
                               className="mxy-2", outline=button_outline, color=button_color,
                               disabled=button_disabled),
                    width=1),
            dbc.Col(dbc.Button(del_icon, disabled=del_disabled,
                               color='link', size='md', className='m-1',
                               id={'type': 'del-results-button', 'index': setup_name}))
        ], align='center'),
        dbc.Spinner(html.Div(id={'type': 'output-rows', 'index': setup_name},
                             children=outputs)),
        html.Hr()
    ])
    return row


def render_calculate():
    content = [render_header('calculate')] + [
        render_calculate_row(setup) for setup in SETUPS
    ]
    return content


def create_floor_area_figure(setup_name, sid):
    scenario = RESULTS[setup_name]['scenarios'][sid]
    floor_area = scenario['_floor_area']
    floor_area = floor_area.groupby('Year').sum() / 1e3
    plot_data = floor_area[['st', 'ret', 'aret', 'new', 'anew']]
    plot_data = plot_data.rename(columns=VINTAGE)
    figure = px.area(
        plot_data,
        title=scenario['name'],
        labels={
            "value": "billion m2",
            "Year": "Year",
            "variable": "Vintage types"
        },
    )
    return figure


def render_floor_area_figure(setup_name):
    if len(RESULTS) < 1:
        return None
    sids = [sid for sid in RESULTS[setup_name]['scenarios']]
    dropdown_value = sids[0]
    content = [
        html.H3('Floor area (EU-27 & UK)'),
        dbc.Row([
            dbc.Col(html.H5('Scenario'), width=1),
            dbc.Col(dcc.Dropdown(
                id='visualize_floor_area_scen-dropdown',
                options=[{'label': RESULTS[setup_name]['scenarios'][sid]['name'], 'value': sid}
                         for sid in sids],
                placeholder="Select a scenario...",
                value=dropdown_value
            ), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='floor_area_figure'), width=8),
        ]),
    ]
    return content


def create_energy_figure(setup_name, enduses):
    if len(RESULTS) < 1:
        return None
    scenarios = RESULTS[setup_name]['scenarios']
    energy_dfs = {scen['name']: scen['_energy'] for id, scen in scenarios.items()}
    energy = pd.concat(energy_dfs, axis='columns')
    energy = energy.groupby('Year').sum() / 1e6
    energy = energy.sum(axis='columns', level=[1, 0])
    energy = energy[enduses].sum(axis='columns', level=1)

    end_use_names = {'heating': 'space heating',
                     'cooling': 'space cooling',
                     'hot_water': 'hot water heating'}
    end_uses = [end_use_names[e] for e in enduses]

    plot_data = energy
    figure = px.line(
        plot_data,
        title='Energy demand for {}'.format(', '.join(end_uses)),
        labels={
            "value": "PWh",
            "Year": "Year",
            "variable": "Scenario"
        },
    )
    figure.update_yaxes(range=[0, plot_data.stack().max()])
    return figure


def render_energy_figure(setup_name):
    if len(RESULTS) < 1:
        return None
    content = [
        html.H3('Energy demand in different scenarios (EU-27 & UK)'),
        html.Div(
            [
                dbc.Label("End-use"),
                dbc.Checklist(
                    options=[
                        {"label": "Space heating", "value": 'heating'},
                        {"label": "Space cooling", "value": 'cooling'},
                        {"label": "Hot water heating", "value": 'hot_water'},
                    ],
                    value=['heating', 'cooling', 'hot_water'],
                    id='energy_enduse-checklist',
                ),
            ]
        ),
        dbc.Row([
            dbc.Col(dcc.Graph(id='energy_figure'), width=8),
        ]),
    ]
    return content


def render_visualize():
    dropdown_value = None
    for setup_name in RESULTS:
        if 'scenarios' in RESULTS[setup_name]:
            dropdown_value = setup_name
            break

    content = [
        render_header('visualize'),
        html.Div(
            dbc.Row([
                dbc.Col(html.H5('Setup'), width=1),
                dbc.Col(dcc.Dropdown(
                    id='visualize-setup-dropdown',
                    options=[{'label': setup, 'value': setup} for setup in RESULTS],
                    placeholder="Select a setup...",
                    disabled = True, 
                    value=dropdown_value
                ), width=6),
            ], align='center')
        ),
        html.Br(),
        html.Div(id='floor_area_figure_layout'),
        html.Div(id='energy_figure_layout'),
    ]
    return content


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    dbc.Container(id='page-content')
])


app.validation_layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    dbc.Container(id='page-content'),
    render_welcome(),
    render_scenarios(),
    render_calculate(),
    render_visualize(),
])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return render_welcome()
    elif pathname == "/scenarios":
        return render_scenarios()
    elif pathname == "/calculate":
        return render_calculate()
    elif pathname == "/visualize":
        return render_visualize()
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ]
    )

@app.callback(
    Output('edit-button', 'disabled'),
    Output('delete-button', 'disabled'),
    Output('setup-download-button', 'disabled'),
    Input("setup-tabs", "children"),
)
def check_buttons(tabs):
    if len(tabs) == 0:
        return True, True, True
    else:
        return False, False, False


# Scenario Callbacks
@app.callback(
    Output('scenario-name-form', 'children'),
    Output('scenario-name-alert', 'children'),
    Input('scenario-setup-dropdown', 'value')
)
def render_scenario_name_form(setup_name):
    if setup_name is None:
        return None, None

    ids = [int(i) for i in SETUPS['default']['scenarios'].keys()]
    setup = SETUPS[setup_name]
    if 'scenarios' in setup:
        names = [setup['scenarios'][i]['name'] for i in ids]
        pvs = [setup['scenarios'][i]['pv'] for i in ids]
    else:
        names = [None for _ in ids]
        pvs = [None for _ in ids]
    name_form = create_scenario_name_form(ids, names, pvs)

    return name_form, None


@app.callback(
    Output('scenario-save-alert', 'children'),
    Input('scenario-save-button', 'n_clicks'),
    State({'type': 'scenario-name', 'index': ALL}, 'value'),
    State({'type': 'scenario-pv-toggle', 'index': ALL}, 'value'),
    State('scenario-setup-dropdown', 'value'),
    prevent_initial_call=True
)
def save_scenario_names(n_save, names, pvs, setup_name):
    ctx = callback_context

    if None in names:
        return dbc.Alert('Please specify the scenario names', color='info', dismissable=True)
    else:
        scen_indices = [sn['id']['index'] for sn in ctx.states_list[0]]
        pv_bools = [True if len(pv) == 1 else False for pv in pvs]
        scen_dict = {sid: {'id': sid, 'name': name, 'pv': pv} for sid, name, pv in zip(scen_indices, names, pv_bools)}
        if 'scenarios' in SETUPS[setup_name]:
            if SETUPS[setup_name]['scenarios'] == scen_dict:
                return None
        SETUPS[setup_name]['scenarios'] = scen_dict
        store_setups()
        rk = list(RESULTS.keys())
        for r in rk:
            del RESULTS[r]
        return dbc.Alert('Scenarios saved', color='success', dismissable=True, duration=3000)


# Calculate callbacks
@app.callback(
    Output({'type': 'output-rows', 'index': MATCH}, 'children'),
    Output({'type': 'calc-button', 'index': MATCH}, 'outline'),
    Output({'type': 'calc-button', 'index': MATCH}, 'color'),
    Output({'type': 'calc-button', 'index': MATCH}, 'disabled'),
    Output({'type': 'del-results-button', 'index': MATCH}, 'children'),
    Output({'type': 'del-results-button', 'index': MATCH}, 'disabled'),
    Input({'type': 'calc-button', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'del-results-button', 'index': MATCH}, 'n_clicks')
)
def calculate_outputs(n_calc, c_del):
    ctx = callback_context

    # check trigger
    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        trigger = ast.literal_eval(trigger)
    trigger_setup = trigger['index']
    trigger_type = trigger['type']

    if trigger_type == 'calc-button':
        try:
            setup = SETUPS[trigger_setup]
            results = {'scenarios': {}}

            for sid in setup['scenarios']:
                scen_name = setup['scenarios'][sid]['name']
                pvint = 0
                pv = setup['scenarios'][sid]['pv']
                if pv:
                    pvint = 1
                start_year = setup['start_year']
                end_year = setup['end_year']

                scen_path = Path('data/scen_{s}_{yb}_{ye}_{pv}.pbz2'.format(s = sid, yb = start_year, ye = end_year, pv = pvint))

                if scen_path.is_file():
                    with bz2.BZ2File(scen_path,'rb') as scen_file:
                        scenario = pickle.load(scen_file)

                results['scenarios'][sid] = scenario

            RESULTS[trigger_setup] = results
            success = True
            output = render_output_rows(trigger_setup)
        except Exception as error:
            import traceback
            success = False
            output = dbc.Alert(
                [
                    html.P('Error in the calculation'),
                    html.Hr(),
                    html.P(str(error)),
                    html.P(traceback.print_exc())
                ],
                color='danger', dismissable=True)

    elif trigger_type == 'del-results-button':
        del RESULTS[trigger_setup]
        success = False
        output = dbc.Alert('Results have been deleted', color='danger', dismissable=True)

    if success:
        button_outline = True
        button_color = 'secondary'
        button_disabled = True
        del_icon = delete_icon
        del_disabled = False
    else:
        button_outline = False
        button_color = 'success'
        button_disabled = False
        del_icon = delete_icon_disabled
        del_disabled = True

    return output, button_outline, button_color, button_disabled, del_icon, del_disabled


@app.callback(
    Output({'type': 'download-result-csv', 'target': MATCH, 'index': MATCH, 'sid': MATCH}, 'data'),
    Input({'type': 'result_download-button', 'target': MATCH, 'index': MATCH, 'sid': MATCH}, 'n_clicks'),
    State({'type': 'result_download-button', 'target': MATCH, 'index': MATCH, 'sid': MATCH}, 'id'),
    prevent_initial_call=True
)
def download_result_table(n_download, trigger_id):
    target = trigger_id['target']
    setup_name = trigger_id['index']
    sid = trigger_id['sid']
    scenario = RESULTS[setup_name]['scenarios'][sid]
    this_pv = ''
    if SETUPS['default']['scenarios'][sid]['pv']:
        this_pv = '-pv'
    scen_name = re.sub(r'[^\w\-_\.]', '_', str(scenario['name']))

    if target == 'floor_area':
        data_frame = scenario['_floor_area']
        this_pv = ''
    elif target == 'energy':
        data_frame = scenario['_energy']
    elif target == 'emissions':
        data_frame = scenario['_emissions']
    else:
        return None

    filename = 'HEB_{stp}_{t}{pv}_{scen}.csv'.format(stp = setup_name, t = target, pv = this_pv, scen = scen_name)

    return dcc.send_data_frame(data_frame.to_csv, filename)


# Visualize callbacks
@app.callback(
    Output('floor_area_figure_layout', 'children'),
    Output('energy_figure_layout', 'children'),
    Input('visualize-setup-dropdown', 'value')
)
def floor_area_layout(setup_name):
    floor_area_fig = render_floor_area_figure(setup_name)
    energy_fig = render_energy_figure(setup_name)
    return floor_area_fig, energy_fig


@app.callback(
    Output('floor_area_figure', 'figure'),
    Input('visualize_floor_area_scen-dropdown', 'value'),
    State('visualize-setup-dropdown', 'value')
)
def floor_area_figure(sid, setup_name):
    return create_floor_area_figure(setup_name, sid)


@app.callback(
    Output('energy_figure', 'figure'),
    Input('energy_enduse-checklist', 'value'),
    State('visualize-setup-dropdown', 'value')
)
def energy_figure(enduses, setup_name):
    return create_energy_figure(setup_name, enduses)


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
