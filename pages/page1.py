import dash
import pandas as pd
import dash_bootstrap_components as dbc
import dash_leaflet.express as dlx
from dash import dcc, html, Output, callback
import dash_leaflet as dl
from dash_extensions.javascript import arrow_function
from dash_extensions.javascript import assign
from dash import dash_table

dash.register_page(
    __name__, path="/page1", title="Exploratory Data Analysis", location="sidebar"
)
pd.set_option("float_format", "{:.2f}".format)


# input data
candidates = pd.read_csv("./data/2022/processed_weball.csv")
states = pd.read_csv("./data/states.csv")

# define page style
PAGE_STYLE = {
    "position": "relative",
    "margin": "4.5rem 4rem 0rem 20rem",
    "color": "#000",
    "text-shadow": "#000 0 0",
    "whiteSpace": "pre-wrap",
    "font-family": "system-ui",
}


# util functoins to create chloropleth
def get_info(feature=None):
    header = [
        html.H4(
            "PAC Money Spent and Raised by States\n",
            style={
                "color": "purple",
                "font-family": "system-ui",
                "font-weight": "bold",
            },
        )
    ]
    if not feature:
        return header + [
            html.B("Hover over a state", style={"font-family": "system-ui"})
        ]
    return [
        html.B(feature["properties"]["name"]),
        html.Br(),
        "Total Received: ${:.3f} \n\nTotal Spent: ${:.3f}".format(
            feature["properties"]["total_r"], feature["properties"]["total_s"]
        ),
    ]


def create_choropleth(id="geojson1", info_id="info1"):
    classes = [0, 5000000, 10000000, 50000000, 100000000, 200000000, 300000000]
    colorscale = [
        "#ffffed",
        "#fcecc4",
        "#ffd69f",
        "#ffbb84",
        "#ff9b78",
        "#ff757b",
        "#ff468e",
        "#ff00ac",
    ]
    style = dict(weight=1, opacity=1, color="white", dashArray="", fillOpacity=0.7)

    # Create colorbar.
    ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + [
        "{}+".format(classes[-1])
    ]
    colorbar = dlx.categorical_colorbar(
        categories=ctg,
        colorscale=colorscale,
        width=520,
        height=10,
        position="bottomleft",
        style={"opacity": "0.7"},
    )

    # Geojson rendering logic, must be JavaScript as it is executed in clientside.
    style_handle = assign(
        """function(feature, context){
        const {classes, colorscale, style, colorProp} = context.hideout;  // get props from hideout
        const value = feature.properties[colorProp];  // get value the determines the color
        for (let i = 0; i < classes.length; ++i) {
            if (value > classes[i]) {
                style.fillColor = colorscale[i];  // set the fill color according to the class
            }
        }
        return style;
    }"""
    )

    # Create geojson.
    geojson = dl.GeoJSON(
        url="/assets/us-states.json",  # url to geojson file
        style=style_handle,  # how to style each polygon
        zoomToBounds=False,  # when true, zooms to bounds when data changes (e.g. on load)
        zoomToBoundsOnClick=False,  # when true, zooms to bounds of feature (e.g. polygon) on click
        hoverStyle=arrow_function(
            dict(weight=3, color="purple", opacity=0.5, dashArray="")
        ),  # style applied on hover
        hideout=dict(
            colorscale=colorscale, classes=classes, style=style, colorProp="total_r"
        ),
        id=id,
    )

    # Create info control.
    info = html.Div(
        children=get_info(),
        id=info_id,
        className="info",
        style={
            "position": "absolute",
            "top": "300px",
            "left": "650px",
            "zIndex": "1000",
            "width": "100px",
        },
    )
    return geojson, colorbar, info


# creating chloropleth
choropleth1 = create_choropleth()
choropleth2 = create_choropleth(id="geojson2", info_id="info2")

map1 = dl.Map(
    children=[dl.TileLayer()],
    style={"height": "450px", "margin-top": "0rem"},
    center=[39, -98],
    zoom=4,
    id="candidates-stats-marker",
)
map2 = dl.Map(
    children=[dl.TileLayer()],
    style={"height": "450px", "margin-top": "0rem"},
    center=[
        states[states["state"] == "DC"]["latitude"].iloc[0],
        states[states["state"] == "DC"]["longitude"].iloc[0],
    ],
    zoom=7,
    id="candidates-individual-marker",
)

table1 = (
    candidates[["Party affiliation", "Total receipts"]]
    .groupby("Party affiliation")
    .agg("sum")
    .sort_values("Total receipts")[::-1][:5]
    .reset_index()
    .round(2)
)
table2 = (
    candidates[["Candidate state", "Party affiliation", "Affiliated Committee Name"]]
    .groupby(["Candidate state", "Party affiliation"])
    .agg("count")
    .sort_values("Affiliated Committee Name")
    .fillna("None")[::-1][:5]
    .reset_index()
    .rename(
        columns={
            "Candidate state": "State",
            "Affiliated Committee Name": "# Affiliated cmtes",
        }
    )
    .round(2)
)
table3 = (
    candidates[["Candidate state", "Party affiliation", "Total receipts"]]
    .groupby(["Candidate state", "Party affiliation"])
    .agg("sum")
    .sort_values("Total receipts")[::-1][:5]
    .reset_index()
    .rename(columns={"Candidate state": "State"})
    .round(2)
)


placeholder_options = [
    {"label": " ", "value": " "},
    {"label": " ", "value": " "},
    {"label": " ", "value": " "},
]



layout = html.Div(
    [
        html.H5("Exploratory Data Analysis of Federal Election Candidacy"),
        html.Hr(),
        html.P(
            """In socio-politics, quantified approaches and modeling techniques are applied in supporting and facilitating political analyses. Individuals, parties, committees and other political entities come together and try to push forward campaigns in hope to receive appropriate patrionization and support for their political agenda. """
        ),
        html.P(
            """The Political Action Committees (PACs or Super PACs) amass funding resources that could benefit the elections. These type of fundings could be from other individuals, or political entities. For the sole of purpose of understanding what the processes of fundraising activities like these really are, this part of the project explores the 2021-2022 PACs financial data."""
        ),
        html.P(
            """This part of the project will first present the receipts, disbursements, and other expenditures in terms of propagating political actions in visualization format grounded in states; for example, how many different political action committees there are by US states. This part of the project will also break down all the candidates of 2022 their basic information as mentioned above including their basic demographics, political party affiliation, election cycle, and incumbency."""
        ),
        html.P(
            """All info is retrievable through the Federal Election Commission's directory."""
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Row(
                        children=[
                            html.Label(
                                ["Select State"],
                                style={
                                    "font-size": "13px",
                                    "text-align": "left",
                                    "off-set": 4,
                                    "color": "#808080",
                                },
                            ),
                            dcc.Dropdown(
                                pd.DataFrame(pd.read_csv("./data/states.csv"))[
                                    "name"
                                ].tolist(),
                                id="state-dropdown",
                            ),
                        ],
                        id="states-row",
                    )
                ),
                dbc.Col(
                    dbc.Row(
                        children=[
                            html.Label(
                                ["Select Candidate"],
                                style={
                                    "font-size": "13px",
                                    "text-align": "left",
                                    "off-set": 4,
                                    "color": "#808080",
                                },
                            ),
                            dcc.Dropdown(id="names-dropdown"),
                        ],
                        id="cand-names-row",
                    )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Row(
                        children=[
                            html.Div(
                                children=[
                                    html.Label(
                                        ["PAC Money Raised and Spent"],
                                        style={
                                            "font-size": "13px",
                                            "text-align": "left",
                                            "off-set": 4,
                                            "color": "#808080",
                                            "margin": "1.5rem 0rem 0rem 0rem",
                                        },
                                    ),
                                    html.Div(
                                        dcc.Slider(
                                            7000,
                                            27500000,
                                            2500000,
                                            value=0,
                                            id="pac-exp-filter",
                                        ),
                                        style={"margin": "0.5rem -1.3rem 0rem -1.3rem"},
                                    ),
                                ],
                                id="slider-1",
                            )
                        ],
                        id="states-row",
                    )
                ),
                dbc.Col(
                    dbc.Row(
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                ["# PACs in Selected Range"],
                                                style={
                                                    "font-size": "13px",
                                                    "text-align": "left",
                                                    "off-set": 4,
                                                    "color": "#808080",
                                                    "margin": "1.5rem 0rem 0rem 0rem",
                                                },
                                            ),
                                            dcc.Dropdown(
                                                id="group1-dropdown", options=placeholder_options, value=" "
                                            ),
                                            html.Div(
                                                id="group1-value",
                                                style={
                                                    "font-size": "13px",
                                                    "text-align": "left",
                                                    "off-set": 4,
                                                    "color": "#808080",
                                                },
                                            ),
                                        ],
                                        style={
                                            "width": "33.3%",
                                            "display": "inline-block",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                ["Average Raised"],
                                                style={
                                                    "font-size": "13px",
                                                    "text-align": "left",
                                                    "off-set": 4,
                                                    "color": "#808080",
                                                    "margin": "1.5rem 0rem 0rem 0rem",
                                                },
                                            ),
                                            dcc.Dropdown(
                                                id="group2-dropdown", options=placeholder_options, value=" "
                                            ),
                                            html.Div(
                                                id="group2-value",
                                                style={
                                                    "font-size": "13px",
                                                    "text-align": "left",
                                                    "off-set": 4,
                                                    "color": "#808080",
                                                },
                                            ),
                                        ],
                                        style={
                                            "width": "33.3%",
                                            "display": "inline-block",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                ["Average Spent"],
                                                style={
                                                    "font-size": "13px",
                                                    "text-align": "left",
                                                    "off-set": 4,
                                                    "color": "#808080",
                                                    "margin": "1.5rem 0rem 0rem 0rem",
                                                },
                                            ),
                                            dcc.Dropdown(
                                                id="group3-dropdown", options=placeholder_options, value=" "
                                            ),
                                            html.Div(
                                                id="group3-value",
                                                style={
                                                    "font-size": "13px",
                                                    "text-align": "left",
                                                    "off-set": 4,
                                                    "color": "#808080",
                                                },
                                            ),
                                        ],
                                        style={
                                            "width": "33.4%",
                                            "display": "inline-block",
                                        },
                                    ),
                                ]
                            )
                        ],
                        id="dynamic-1",
                    )
                ),
            ]
        ),
        html.P(),
        html.Div(
            id="mapmessage",
            style={"color": "#FFFFFF", "fontSize": "20px", "marginTop": "-25px"},
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(dbc.Row(dbc.Col(children=[map1])), id="map1-col"),
                dbc.Col(dbc.Row(dbc.Col(children=[map2])), id="map2-col"),
            ]
        ),
        html.Br(),
        html.Br(),
        html.H5("What's On The Map?"),
        html.Hr(),
        html.P(
            """To understand this these two maps more thoroughly, a few things that are important to note are:"""
        ),
        dcc.Markdown(
            """
                                  1. There are three layers to the map that divide up the committees by party affiliation (on the top right corner of the map the results could be filtered through checking or unchecking each box).

                                  2. The backdrop layer displays the sum amount of money raised for each state and the data could be displayed by hovering over each state boundary.
                                  
                                  3. The slider manipulates the committees to display by how much money they havg raised and the amount is indicated by the size of the colored dot (the more the bigger).

                                  4. The color of the dots/circles indicates the party affiliation of each committee. 

                                  5. The stats that are right next to the slider indicate # PACs, avgrage raised and spent for all the committees that fall into the sliding range. 
                                 
                                 """
        ),
        html.Br(),
        html.H5("Some Other Important Info Stats"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown(f""" - Total Raised by Party (Top 5): """),
                        dash_table.DataTable(
                            table1.to_dict("records"),
                            [{"name": i, "id": i} for i in table1.columns],
                            id="descriptive_table",
                            is_focused=True,
                            style_cell={
                                "textAlign": "left",
                                "border": "1px solid gray",
                                "fontSize": 15,
                            },
                            style_header={
                                "backgroundColor": "#cfd8dc",
                                "color": "black",
                                "fontWeight": "bold",
                            },
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Markdown(f""" - Total Cmtes by State and Party (Top 5):"""),
                        dash_table.DataTable(
                            table2.to_dict("records"),
                            [{"name": i, "id": i} for i in table2.columns],
                            id="descriptive_table",
                            is_focused=True,
                            style_cell={
                                "textAlign": "left",
                                "border": "1px solid gray",
                                "fontSize": 15,
                            },
                            style_header={
                                "backgroundColor": "#cfd8dc",
                                "color": "black",
                                "fontWeight": "bold",
                            },
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Markdown(
                            f""" - Total Raised by State and Party (Top 5): """
                        ),
                        dash_table.DataTable(
                            table3.to_dict("records"),
                            [{"name": i, "id": i} for i in table3.columns],
                            id="descriptive_table",
                            is_focused=True,
                            style_cell={
                                "textAlign": "left",
                                "border": "1px solid gray",
                                "fontSize": 15,
                            },
                            style_header={
                                "backgroundColor": "#cfd8dc",
                                "color": "black",
                                "fontWeight": "bold",
                            },
                        ),
                    ]
                ),
            ]
        ),
        html.Br(),
        html.Br(),
    ],
    className="page1",
    id="page1-content",
    style=PAGE_STYLE,
)


@callback(
    Output("cand-names-row", "children"),
    [dash.dependencies.Input("state-dropdown", "value")],
)
def update_output(value):
    a = states.loc[states["name"] == value, "state"]
    if value:
        res = candidates.loc[
            candidates["State"] == a.iloc[0], "Candidate name"
        ].tolist()
    else:
        res = candidates["Candidate name"].tolist()
    return html.Label(
        ["Select Candidate"],
        style={
            "font-size": "13px",
            "text-align": "left",
            "off-set": 4,
            "color": "#808080",
        },
    ), dcc.Dropdown(res, id="names-dropdown", searchable=True, multi=True)


@callback(
    Output("candidates-stats-marker", "children"),
    Output("candidates-individual-marker", "viewport"),
    Output("candidates-individual-marker", "children"),
    Output("group1-dropdown", "options"),
    Output("group2-dropdown", "options"),
    Output("group3-dropdown", "options"),
    [
        dash.dependencies.Input("pac-exp-filter", "value"),
        dash.dependencies.Input("state-dropdown", "value"),
        dash.dependencies.Input("names-dropdown", "value"),
    ],
)
def update_output(slider, state, cands):
    latLon = candidates[
        [
            "Party code",
            "Party affiliation",
            "Affiliated Committee Name",
            "Total receipts",
            "Total disbursements",
            "lat",
            "lon",
        ]
    ]
    latLon = [tuple(i[1:]) for i in latLon.itertuples()]
    colors = ["blue", "red", "grey"]
    s_latlon = [
        states[states["state"] == "DC"]["latitude"].iloc[0],
        states[states["state"] == "DC"]["longitude"].iloc[0],
    ]
    groups = {"DEM": ("blue", []), "REP": ("red", []), "OTH": ("grey", [])}
    n_rep = 0
    n_dem = 0
    n_3rd = 0

    raised_rep = 0
    raised_dem = 0
    raised_3rd = 0

    spent_rep = 0
    spent_dem = 0
    spent_3rd = 0

    for code, pty, name, r, s, lat, lng in latLon:

        # number of PACs divided by party

        if 28000000 < r <= 30000000:
            radius = 53
            opacity = 0.8
        elif 24000000 < r <= 28000000:
            radius = 50
            opacity = 0.6
        elif 21000000 < r <= 24000000:
            radius = 45
            opacity = 0.5
        elif 18000000 < r <= 21000000:
            radius = 40
            opacity = 0.4
        elif 15000000 < r <= 18000000:
            radius = 35
            opacity = 0.3
        elif 12000000 < r <= 15000000:
            radius = 30
            opacity = 0.3
        elif 9000000 < r <= 12000000:
            radius = 20
            opacity = 0.3
        elif 6000000 < r <= 9000000:
            radius = 15
            opacity = 0.3
        elif 3000000 < r <= 6000000:
            radius = 10
            opacity = 0.3
        else:
            radius = 5
            opacity = 0.2

        if r > slider and r < slider + 2500000:
            cm = dl.CircleMarker(
                center=[lat, lng],
                color=colors[int(code) - 1],
                opacity=opacity,
                weight=1,
                fillColor=colors[int(code) - 1],
                fillOpacity=opacity,
                radius=radius,
                children=[
                    dl.Popup(
                        f"Committee Name: \n {name} \n Election cycle: 2022 \n Total Raised (YTD2022): {r} \n Total Spent (YTD2022): {s}"
                    )
                ],
            )

            if pty != "REP" and pty != "DEM":
                n_3rd += 1
                raised_3rd += r
                spent_3rd += s
                groups["OTH"][1].append(cm)
            else:
                if pty == "REP":
                    n_rep += 1
                    raised_rep += r
                    spent_rep += s
                else:
                    n_dem += 1
                    raised_dem += r
                    spent_dem += s
                groups[pty][1].append(cm)

    avg_r_rep = round(raised_rep / n_rep, 2) if n_rep != 0 else 0
    avg_r_dem = round(raised_dem / n_dem, 2) if n_dem != 0 else 0
    avg_r_3rd = round(raised_3rd / n_3rd, 2) if n_3rd != 0 else 0

    avg_s_rep = round(spent_rep / n_rep, 2) if n_rep != 0 else 0
    avg_s_dem = round(spent_dem / n_dem, 2) if n_dem != 0 else 0
    avg_s_3rd = round(spent_3rd / n_3rd, 2) if n_3rd != 0 else 0

    data = [
        dl.TileLayer(),
        dl.LayersControl(
            [
                dl.Pane(
                    name="US-Boundaries",
                    children=[
                        dl.BaseLayer(
                            name="US-Boundaries", children=choropleth1, checked=True
                        )
                    ],
                ),
                dl.Pane(
                    name="PAC-Data",
                    children=[
                        dl.Overlay(
                            dl.LayerGroup(groups["DEM"][1]), name="DEM", checked=True
                        ),
                        dl.Overlay(
                            dl.LayerGroup(groups["REP"][1]), name="REP", checked=True
                        ),
                        dl.Overlay(
                            dl.LayerGroup(groups["OTH"][1]), name="3RD", checked=True
                        ),
                    ],
                ),
            ]
        ),
    ]

    second_map = data.copy()
    second_map.remove(second_map[1])
    second_map.insert(
        1,
        dl.LayersControl(
            [
                dl.Pane(
                    name="US-Boundaries",
                    children=[
                        dl.BaseLayer(
                            name="US-Boundaries", children=choropleth2, checked=True
                        )
                    ],
                ),
                dl.Pane(
                    name="PAC-Data",
                    children=[
                        dl.Overlay(
                            dl.LayerGroup(groups["DEM"][1]), name="DEM", checked=True
                        ),
                        dl.Overlay(
                            dl.LayerGroup(groups["REP"][1]), name="REP", checked=True
                        ),
                        dl.Overlay(
                            dl.LayerGroup(groups["OTH"][1]), name="3RD", checked=True
                        ),
                    ],
                ),
            ]
        ),
    )
    if state:
        if states[states["name"] == state]["capital"].iloc[0]:
            s_latlon = [
                states[states["name"] == state]["latitude_c"].iloc[0],
                states[states["name"] == state]["longitude_c"].iloc[0],
            ]
        else:
            s_latlon = [
                states[states["name"] == state]["latitude"].iloc[0],
                states[states["name"] == state]["longitude"].iloc[0],
            ]
        if cands:
            pins = []
            for cand in cands:
                row = candidates[candidates["Candidate name"] == cand]
                latlng = [row["lat"].iloc[0], row["lon"].iloc[0]]
                m = dl.Marker(
                    position=latlng,
                    children=[
                        dl.Popup(
                            f'Committee Name: \n {row["Affiliated Committee Name"].iloc[0]} \n Election cycle: 2022 \n Total Raised (YTD2022): {row["Total receipts"].iloc[0]} \n Total Spent (YTD2022): {row["Total disbursements"].iloc[0]}'
                        )
                    ],
                )
                pins.append(m)
            second_map.append(dl.Pane(name="Individual-pin", children=pins))
            s_latlon = [row["lat"].iloc[0], row["lon"].iloc[0]]
    else:
        if cands:
            pins = []
            for cand in cands:
                row = candidates[candidates["Candidate name"] == cand]
                latlng = [row["lat"].iloc[0], row["lon"].iloc[0]]
                m = dl.Marker(
                    position=latlng,
                    children=[
                        dl.Popup(
                            f'Committee Name: \n {row["Affiliated Committee Name"].iloc[0]} \n Election cycle: 2022 \n Total Raised (YTD2022): {row["Total receipts"].iloc[0]} \n Total Spent (YTD2022): {row["Total disbursements"].iloc[0]}'
                        )
                    ],
                )
                pins.append(m)
            second_map.append(dl.Pane(name="Individual-pin", children=pins))
            s_latlon = [row["lat"].iloc[0], row["lon"].iloc[0]]

    return (
        data,
        dict(center=s_latlon, zoom=7, transition="flyTo"),
        second_map,
        [
            {"label": "REP", "value": n_rep},
            {"label": "DEM", "value": n_dem},
            {"label": "3RD", "value": n_3rd},
        ],
        [
            {"label": "REP", "value": avg_r_rep},
            {"label": "DEM", "value": avg_r_dem},
            {"label": "3RD", "value": avg_r_3rd},
        ],
        [
            {"label": "REP", "value": avg_s_rep},
            {"label": "DEM", "value": avg_s_dem},
            {"label": "3RD", "value": avg_s_3rd},
        ],
    )


@callback(
    [
        Output("group1-value", "children"),
        Output("group2-value", "children"),
        Output("group3-value", "children"),
    ],
    [
        dash.dependencies.Input("group1-dropdown", "value"),
        dash.dependencies.Input("group2-dropdown", "value"),
        dash.dependencies.Input("group3-dropdown", "value"),
    ],
)
def display_selected_value(group1_value, group2_value, group3_value):
    return group1_value, group2_value, group3_value


@callback(Output("info1", "children"), dash.dependencies.Input("geojson1", "hoverData"))
def info_hover(feature):
    return get_info(feature)


@callback(Output("info2", "children"), dash.dependencies.Input("geojson2", "hoverData"))
def info_hover(feature):
    return get_info(feature)
