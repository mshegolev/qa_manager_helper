# Import required libraries
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html

# Load data from a csv file
data = pd.read_csv("data.csv")
data["type_of_work"].unique()

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(
    [
        html.H1("QA Metrics Dashboard"),
        dcc.Dropdown(
            id="type_of_work_dropdown",
            options=[{"label": i, "value": i} for i in data["type_of_work"].unique()],
            value=data["type_of_work"].unique()[0],
        ),
        dcc.Graph(id="qa_metrics_plot"),
    ]
)


# Define the callback function to update the plot based on the selected dropdown value
@app.callback(
    dash.dependencies.Output("qa_metrics_plot", "figure"), [dash.dependencies.Input("type_of_work_dropdown", "value")]
)
def update_plot(selected_type_of_work):
    # Filter the data based on the selected dropdown value
    filtered_data = data[data["type_of_work"] == selected_type_of_work]

    # Group the data by type_of_work and date to get the total worktime for each day and type of work
    grouped_data = filtered_data.groupby(["type_of_work", "date"])["worktime"].sum().reset_index(name="total_worktime")

    # Create the plot using Plotly Express
    fig = px.line(
        grouped_data,
        x="date",
        y="total_worktime",
        color="type_of_work",
        title="QA Metrics for {}".format(selected_type_of_work),
    )
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
