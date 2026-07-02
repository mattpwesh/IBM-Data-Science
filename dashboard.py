# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
)

max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a Dash application
app = dash.Dash(__name__)

# Build the list of dropdown options: one entry per unique site + "All Sites"
launch_sites = spacex_df["Launch Site"].unique().tolist()
dropdown_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site, "value": site} for site in launch_sites
]

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),

        # TASK 1: Add a dropdown to select a launch site
        dcc.Dropdown(
            id="site-dropdown",
            options=dropdown_options,
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),

        # TASK 2: Pie chart showing total launch success count (or per-site)
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),

        html.P("Payload range (Kg):"),

        # TASK 3: Range slider for payload mass
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={i: str(i) for i in range(0, 10001, 2500)},
            value=[min_payload, max_payload],
        ),
        html.Br(),

        # TASK 4: Scatter chart for Payload vs. Launch Outcome
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2: Callback for the pie chart
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        # Show total successful launches for all sites
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Site",
        )
    else:
        # Show success vs failure count for the selected site
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        outcome_counts = filtered_df["class"].value_counts().reset_index()
        outcome_counts.columns = ["class", "count"]
        outcome_counts["outcome"] = outcome_counts["class"].map(
            {1: "Success", 0: "Failure"}
        )
        fig = px.pie(
            outcome_counts,
            values="count",
            names="outcome",
            title=f"Total Launch Outcomes for site {entered_site}",
            color="outcome",
            color_discrete_map={"Success": "#00CC96", "Failure": "#EF553B"},
        )
    return fig


# TASK 4: Callback for the scatter chart
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low)
        & (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if entered_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        title = f"Payload vs. Launch Outcome for {entered_site}"
    else:
        title = "Payload vs. Launch Outcome for All Sites"

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title,
        labels={"class": "Launch Outcome (1 = Success, 0 = Failure)"},
    )
    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
