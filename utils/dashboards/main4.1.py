import dash
import pandas as pd
import plotly.graph_objs as go
from dash import dash, dcc, html
from dash.dependencies import Input, Output

# Read in the data
df = pd.read_csv("data.csv")
df["date"] = pd.to_datetime(df["date"])

# Define the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(
    [
        html.Label("Date Range"),
        dcc.DatePickerRange(id="date-range", start_date=df["date"].min(), end_date=df["date"].max()),
        html.Label("Author"),
        dcc.Dropdown(
            id="author-dropdown",
            options=[{"label": i, "value": i} for i in df["author_name"].unique()],
            multi=True,
            value=[i for i in df["author_name"].unique()],
        ),
        dcc.Graph(id="worktime-graph"),
    ]
)


# Define the callback
@app.callback(
    Output("worktime-graph", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("author-dropdown", "value"),
)
def update_figure(start_date, end_date, author_list):
    # Filter the data
    filtered_df = df[df["author_name"].isin(author_list)]
    filtered_df = filtered_df[(filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)]

    # Calculate the weekly hours for each author
    weekly_hours = (
        filtered_df.groupby(["author_name", pd.Grouper(key="date", freq="W-MON")])["worktime"].sum().reset_index()
    )

    # Define the bar colors
    colors = {"LQA": "red", "QA": "yellow", "QC": "red", "meetings": "blue"}

    # Create the traces
    traces = []
    for work_type, color in colors.items():
        work_type_df = weekly_hours[weekly_hours["type_of_work"] == work_type]
        traces.append(
            go.Bar(
                x=work_type_df["date"],
                y=work_type_df["worktime"],
                name=work_type,
                marker=dict(color=color, opacity=0.7),
            )
        )

    # Set the layout
    layout = go.Layout(
        barmode="overlay", xaxis=dict(title="Week Ending"), yaxis=dict(title="Hours"), hovermode="closest"
    )

    # Create the figure
    figure = go.Figure(data=traces, layout=layout)

    return figure


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
