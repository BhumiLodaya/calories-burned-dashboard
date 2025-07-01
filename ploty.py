import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Load and clean dataset
df = pd.read_csv("C:/Users/bhumi/OneDrive/Desktop/professional/internship/calories/calories_cleaned.csv")
df.columns = df.columns.str.strip()

# Categorize Age, Distance, BMI
df["Age Category"] = pd.cut(
    df["Age"], bins=[0, 19, 35, 55, 100],
    labels=["Teen (13–19)", "Young Adult (20–35)", "Middle-Aged (36–55)", "Senior (56+)"],
    right=False
)

df["Distance Category"] = pd.cut(
    df["Distance(km)"], bins=[0, 5, 10, float("inf")],
    labels=["<5 km", "5–10 km", ">10 km"],
    right=False
)

df["BMI Category"] = pd.cut(
    df["BMI"], bins=[0, 18.5, 24.9, 29.9, float("inf")],
    labels=["Underweight", "Normal", "Overweight", "Obese"],
    right=False
)

# Dash app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Health Report Dashboard"

DROPDOWN_STYLE = {
    "backgroundColor": "#ffffff",
    "color": "black",
    "border": "1px solid #333",
    "fontWeight": "bold"
}
LABEL_STYLE = {"color": "white"}

# Layout
app.layout = dbc.Container([
    html.H2("Calories Burned by Running Analysis", className="text-center text-light my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Age Category", style=LABEL_STYLE),
            dcc.Dropdown(
                id="age-filter",
                options=[{"label": str(cat), "value": cat} for cat in df["Age Category"].dropna().unique()],
                value="Middle-Aged (36–55)",
                clearable=False,
                style=DROPDOWN_STYLE
            ),
            html.Br(),

            html.Label("Select Distance Category", style=LABEL_STYLE),
            dcc.Dropdown(
                id="distance-filter",
                options=[{"label": str(cat), "value": cat} for cat in df["Distance Category"].dropna().unique()],
                value="5–10 km",
                clearable=False,
                style=DROPDOWN_STYLE
            ),
            html.Br(),

            html.Label("Select BMI Category", style=LABEL_STYLE),
            dcc.Dropdown(
                id="bmi-filter",
                options=[{"label": str(cat), "value": cat} for cat in df["BMI Category"].dropna().unique()],
                value="Normal",
                clearable=False,
                style=DROPDOWN_STYLE
            ),
        ], width=3),

        dbc.Col([
            dcc.Graph(id="age-gender-distribution"),
            dcc.Graph(id="calories-distance-graph"),

            # Wrapped donut chart with readable explanation
            dbc.Card([
                dbc.CardBody([
                    html.H4("Calories Burned by Zone", className="card-title text-white"),
                    dcc.Graph(id="calories-distribution"),
                    html.P(
                        "This chart provides a detailed analysis of calories burned through running workouts, "
                        "categorized by Age, Distance, BMI, and Gender. Workouts are grouped into calorie burn zones "
                        "based on the calories burned: Very Low (0–150), Low (151–300), Moderate (301–450), "
                        "High (451–600), and Extreme (601+).",
                        className="card-text", style={"color": "white", "fontSize": "14px", "marginTop": "15px"}
                    )
                ])
            ], style={"marginBottom": "30px", "backgroundColor": "#1a1a1a", "padding": "10px"}),

            dcc.Graph(id="bmi-calories-graph"),
            dcc.Graph(id="heart-rate-graph"),
        ], width=9)
    ])
], fluid=True)

# Callback
@app.callback(
    Output("calories-distance-graph", "figure"),
    Output("bmi-calories-graph", "figure"),
    Output("heart-rate-graph", "figure"),
    Output("calories-distribution", "figure"),
    Output("age-gender-distribution", "figure"),
    Input("age-filter", "value"),
    Input("distance-filter", "value"),
    Input("bmi-filter", "value")
)
def update_charts(age_cat, dist_cat, bmi_cat):
    filtered_df = df[
        (df["Age Category"] == age_cat) &
        (df["Distance Category"] == dist_cat) &
        (df["BMI Category"] == bmi_cat)
    ]

    # Chart 1: Gender count in selected age group
    chart1 = filtered_df["Gender"].value_counts().reset_index()
    chart1.columns = ["Gender", "Count"]
    fig1 = px.bar(chart1, x="Gender", y="Count", color="Gender",
                  title="Gender Distribution in Selected Age Group")

    # Chart 2: Calories by Distance (Gender)
    chart2 = filtered_df.groupby(["Distance Category", "Gender"])["Calories Burned"].mean().reset_index()
    fig2 = px.bar(chart2, x="Distance Category", y="Calories Burned", color="Gender",
                  barmode="group", title="Avg Calories Burned by Distance (Gender-wise)")

    # Chart 3: Donut Chart of Burn Zones
    bins = [0, 150, 300, 450, 600, float('inf')]
    labels = ['Very Low', 'Low', 'Moderate', 'High', 'Extreme']
    filtered_df["Burn Zone"] = pd.cut(filtered_df["Calories Burned"], bins=bins, labels=labels)
    chart3 = filtered_df["Burn Zone"].value_counts().reset_index()
    chart3.columns = ["Burn Zone", "Count"]
    fig3 = px.pie(chart3, names="Burn Zone", values="Count", hole=0.5,
                  color_discrete_sequence=px.colors.sequential.thermal)

    # Chart 4: Calories by BMI (Gender)
    chart4 = filtered_df.groupby(["BMI Category", "Gender"])["Calories Burned"].mean().reset_index()
    fig4 = px.bar(chart4, x="BMI Category", y="Calories Burned", color="Gender",
                  barmode="group", title="Calories Burned by BMI (Gender-wise)")

    # Chart 5: Average Heart Rate by Age Category & Gender
    chart5 = filtered_df.groupby(["Age Category", "Gender"])["Average Heart Rate"].mean().reset_index()
    fig5 = px.bar(chart5, x="Age Category", y="Average Heart Rate", color="Gender",
                  barmode="group", title="Average Heart Rate by Age Category (Gender-wise)")

    # Dark theme for all graphs
    for fig in [fig1, fig2, fig3, fig4, fig5]:
        fig.update_layout(paper_bgcolor="#111", plot_bgcolor="#111", font=dict(color="white"))

    return fig2, fig4, fig5, fig3, fig1

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
