import sqlite3

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (DashProxy, MultiplexerTransform,
                                    ServersideOutputTransform)


conn = sqlite3.connect('testDB.db')
df = pd.read_sql_query("SELECT * FROM sources", conn)

conn.close()


UNIQUE_STATE = df.state.unique()

DATA = {
    'State': 1,
    'Group': df.state,
    'Start': df.state_begin,
    'End': df.state_end,
    'Состояние - ': df.state,
    'Причина - ': df.reason,
    'Начало - ': df.state_begin,
    'Длительность - ': df.duration_min,
    'Сменный день - ': df.shift_day,
    'Смена - ': df.shift_name,
    'Оператор - ': df.operator
}

HOVER_DATA = {
    'Состояние - ': True,
    'Причина - ': True,
    'Начало - ': True,
    'Длительность - ': ':.2f',
    'Сменный день - ': True,
    'Смена - ': True,
    'Оператор - ': True,
    'State': False,
    'Group': False,
    'Start': False,
    'End': False,
}

CARD_STYLE = dict(withBorder=True,
                  shadow="sm",
                  radius="md",
                  style={'height': '100%'})


def fig_ganta(data):
    dff = pd.DataFrame(data)

    fig = px.timeline(dff, x_start="Start", x_end="End",
                      y="State", color="Group", title=df.client_name[0],
                      hover_data=HOVER_DATA
                      )
    fig.update_yaxes(visible=False)
    return fig


def fig_pie():
    fig = go.Figure(data=[go.Pie(labels=df.state, values=df.duration_min)])
    fig.update_layout(
        title='Диаграмма состояния оборудования', title_font_size=30)
    return fig


class EncostDash(DashProxy):
    def __init__(self, **kwargs):
        self.app_container = None
        super().__init__(transforms=[ServersideOutputTransform(),
                                     MultiplexerTransform()], **kwargs)


app = EncostDash(name=__name__)


def get_layout():
    return html.Div([
        dmc.Paper([
            dmc.Grid([
                dmc.Col([
                    dmc.Card([
                        html.H1(f'Клиент: {df.client_name[0]}'),
                        html.P(f'Сменный день: {df.shift_day[0]}'),
                        html.P(
                            f'Точка учета: {df.endpoint_name[0]}'),
                        html.P(
                            f'Начало периода: {df.operator_auth_start[0]}'),
                        html.P(
                            f'Конец периода: {df.operator_auth_end[::-1][0]}'),

                        dcc.Dropdown(id='filter-state',
                                     options=[{'label': i, 'value': i}
                                              for i in UNIQUE_STATE],
                                     value='all',
                                     multi=True,
                                     ),
                        dmc.Button(
                            'Фильровать',
                            id='button1'),
                    ],
                        **CARD_STYLE)
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        html.Div(
                            'Верхняя правая карточка'),
                        dcc.Graph(figure=fig_pie())],
                        **CARD_STYLE)
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        html.Div('Нижняя карточка'),
                        dcc.Graph(id='ganta',
                                  figure=fig_ganta(DATA))],
                             **CARD_STYLE)
                ], span=12),
            ], gutter="xl",)
        ])
    ])


app.layout = get_layout()


@app.callback(
    Output('ganta', 'figure'),
    [State('filter-state', 'value'),
     Input('button1', 'n_clicks')],
    prevent_initial_call=True,
)
def update_div1(value, click):

    if click is None:
        raise PreventUpdate

    if value:
        df_filtered = df.loc[df['state'].isin(value)]

        data = {'State': 1,
                'Group': df_filtered.state,
                'Start': df_filtered.state_begin,
                'End': df_filtered.state_end,
                'Состояние - ': df_filtered.state,
                'Причина - ': df_filtered.reason,
                'Начало - ': df_filtered.state_begin,
                'Длительность - ': df_filtered.duration_min,
                'Сменный день - ': df_filtered.shift_day,
                'Смена - ': df_filtered.shift_name,
                'Оператор - ': df_filtered.operator
                }

        return fig_ganta(data)
    else:
        return fig_ganta(DATA)


if __name__ == '__main__':
    app.run_server(debug=True)
