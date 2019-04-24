import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.colors import DEFAULT_PLOTLY_COLORS


import pandas as pd
import numpy as np

from textwrap import dedent

import config

################
# DATA LOADING #
################

kluby = pd.read_hdf(config.FILE_KLUBY)
sorted_kluby = sorted(kluby.unique())
sorted_names = {
    klub: ["Celý klub"] + sorted(kluby[kluby == klub].index,
                 key=lambda x: " ".join(x.split(" ")[::-1]))
    for klub in sorted_kluby}
hlasy = {vysledok: pd.read_hdf(config.FILE_STATS_HLASY_PIE, vysledok)
         for vysledok in config.HLASY_STATS_VYSLEDOK}
dg = pd.read_hdf(config.FILE_DEMAGOG_PIE)
dur = pd.read_pickle(config.FILE_ROZPRAVY_DURATION)
dur_kluby = pd.Series({
    klub: dur[np.intersect1d(sorted_names[klub], dur.index)].sum()
    for klub in sorted_kluby}).sort_values()

#####################
# APP SPECIFICATION #
#####################

app = dash.Dash()
server = app.server

app.layout = html.Div([
    html.Div([
        dcc.Markdown("## Výber klubu"),
        dcc.Dropdown(
            options=[{
                "label": "{}".format(klub),
                "value": klub
                } for klub in sorted_kluby],
                value=sorted_kluby[0],
                id="klub_selection",
                clearable=False
                ),
        dcc.Markdown("## Výber poslanca"),
        dcc.Dropdown(
            options=[{
                "label": "{}".format(name),
                "value": name
                } for name in sorted_names[sorted_kluby[0]]],
                value=sorted_names[sorted_kluby[0]][0],
                id="poslanec_selection",
                clearable=False
                )
        ]),
    html.Div([  # HLASOVANIA
        dcc.Markdown(dedent("""
                     ## Štatistiky z hlasovaní v parlamente
                     Nasledujúce grafy vznikli spracovaním dát zo stránky
                     [nrsr.sk](
                     https://www.nrsr.sk/web/default.aspx?SectionId=108).
                     """))], style={"align": "center"}),
    html.Div([
        html.Div([
            dcc.Graph(id="pie_positive")
            ], style={"width": "49%", "display": "inline-block"}),
            html.Div([
            dcc.Graph(id="pie_negative")
            ], style={"width": "49%", "display": "inline-block"})]),
    html.Div([  # ROZPRAVY
        dcc.Markdown(dedent("""
                     ## Štatistiky príspevkov do rozpráv v parlamente
                     Údaje v grafe sú prevzaté zo stránky [tv.nrsr.sk](
                     http://tv.nrsr.sk/).
                     """))], style={"align": "center"}),
    html.Div(id="rozpravy", children=[
        dcc.Graph(id="duration_graph"),
        ]),
    html.Div([  # DEMAGOG
        dcc.Markdown(dedent("""
                     ## Štatistiky pravdivosti výrokov v politických debatách
                     Údaje v grafoch sú prevzaté zo stránky [demagog.sk](
                     http://www.demagog.sk/).
                     """))], style={"align": "center"}),
    html.Div(id="graph_demagog", children=[
        dcc.Graph(id="pie_demagog"),
        ]),
    html.Div(id="replacement_text_demagog", children=[
        html.P("Nie sú registrované žiadne vystúpenia v debatách."),
    ])
])

######################
# GRAPHING FUNCTIONS #
######################


def pie_hlasy(name, klub, vysledok):
    """Output the hlasy data for a Plotly pie plot."""
    if name == "Celý klub":
        values = hlasy[vysledok][sorted_names[klub][1:]].sum(axis=1)
        values = values[config.HLASY_STATS_ORDER].values
    else:
        values = hlasy[vysledok][name][config.HLASY_STATS_ORDER].values
    labels = [config.HLASY_STATS_MEANING[s] for s in config.HLASY_STATS_ORDER]
    trace = go.Pie(labels=labels, values=values, sort=False, marker={
        "colors": [DEFAULT_PLOTLY_COLORS[i] for i in [2,3,0,4,1]]
    })
    layout = go.Layout(
        title="Hlasovanie v {} prípadoch keď návrh {}".format(
            int(np.sum(values)), vysledok)
    )
    return {"data": [trace], "layout": layout}


def pie_demagog(values):
    """Output the demagog data for a Plotly pie plot."""
    labels = dg.index.values
    trace = go.Pie(labels=labels, values=values, sort=False, marker={
        "colors": [DEFAULT_PLOTLY_COLORS[i] for i in [2, 3, 1, 0]]
    })
    layout = go.Layout(
        title="Pravdivosť z {} diskusných výrokov.".format(
            int(np.sum(values))
        )
    )
    return {"data": [trace], "layout": layout}

def bar_rozpravy_duration(name, klub):
    """Output the rozpravy data for a Plotly bar chart."""
    if name == "Celý klub":
        df = dur_kluby
        name = klub
        y = df.apply(lambda x: x.total_seconds()) / 3600
        title = "Celková dĺžka vystúpení v rozpravách v hodinách"
    else:
        df = dur
        y = df.apply(lambda x: x.total_seconds()) / 60
        title = "Celková dĺžka vystúpení v rozpravách v minutách"
    n = len(df)
    name_ind = np.arange(n)[df.index == name][0]
    colors = [DEFAULT_PLOTLY_COLORS[0]] * n
    colors[name_ind] = DEFAULT_PLOTLY_COLORS[3]
    ss = n * [""]
    ss[name_ind] = name
    data = [
        go.Bar(
            x=df.index,
            y=y,
            text=df.index,
            marker={"color": colors})]
    layout = go.Layout(
        xaxis={"ticktext": ss, "tickvals": np.arange(n), "tickangle": 22},
        title=title)
    return {"data": data, "layout": layout}

#################
# APP CALLBACKS #
#################

@app.callback(
    Output("poslanec_selection", "options"),
    [Input("klub_selection", "value")]
)
def poslanec_selection_options(klub):
    return [{
        "label": "{}".format(name),
        "value": name
        } for name in sorted_names[klub]]

@app.callback(
    Output("poslanec_selection", "value"),
    [Input("klub_selection", "value")]
)
def klub_selection_options(klub):
    return sorted_names[klub][0]

@app.callback(
    Output("pie_positive", "figure"),
    [Input("poslanec_selection", "value")],
    [State("klub_selection", "value")]
)
def plot_positives(name, klub):
    return pie_hlasy(name, klub, config.HLASY_STATS_VYSLEDOK[0])


@app.callback(
    Output("pie_negative", "figure"),
    [Input("poslanec_selection", "value")],
    [State("klub_selection", "value")]
)
def plot_negatives(name, klub):
    return pie_hlasy(name, klub, config.HLASY_STATS_VYSLEDOK[1])


@app.callback(
    Output("replacement_text_demagog", "style"),
    [Input("poslanec_selection", "value")]
)
def toggle_demagog_text(name):
    if name in dg.columns or name == "Celý klub":
        return {"display": "none"}
    else:
        return {"display": "block"}


@app.callback(
    Output("graph_demagog", "style"),
    [Input("poslanec_selection", "value")]
)
def toggle_demagog_graph(name):
    if name in dg.columns or name == "Celý klub":
        return {"display": "block"}
    else:
        return {"display": "none"}


@app.callback(
    Output("pie_demagog", "figure"),
    [Input("poslanec_selection", "value")],
    [State("klub_selection", "value")]
)
def plot_demagog(name, klub):
    if name in dg.columns:
        return pie_demagog(dg[name].values)
    elif name == "Celý klub":
        common_poslanci = np.intersect1d(dg.columns, sorted_names[klub][1:])
        return pie_demagog(dg[common_poslanci].sum(axis=1).values)
    else:
        return {"data": []}

@app.callback(
    Output("duration_graph", "figure"),
    [Input("poslanec_selection", "value")],
    [State("klub_selection", "value")]
)
def plot_duration(name, klub):
    return bar_rozpravy_duration(name, klub)

if __name__ == '__main__':
    app.run_server(debug=True)
