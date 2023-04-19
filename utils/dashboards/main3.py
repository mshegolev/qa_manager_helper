import dash
import pandas as pd
from dash import dcc, html

# data = {
#     'type_of_work': ['LQA', 'QA', 'LQA', 'LQA', 'LQA'],
#     'date': ['2022-07-14', '2022-09-21', '2022-07-20', '2022-07-21', '2022-08-08'],
#     'worktime': [8, 6, 4, 6, 4]
# }

df = pd.read_csv("data.csv")
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="worktime-graph"),
        dcc.Dropdown(
            id="type-of-work-dropdown",
            options=[{"label": i, "value": i} for i in df["type_of_work"].unique()],
            value=[],
            multi=True,
        ),
        dcc.Dropdown(
            id="author-name-dropdown",
            options=[{"label": i, "value": i} for i in df["author_name"].unique()],
            value=[],
            multi=True,
        ),
        dcc.DatePickerRange(
            id="date-picker-range",
            min_date_allowed=df["date"].min(),
            max_date_allowed=df["date"].max(),
            start_date=df["date"].min(),
            end_date=df["date"].max(),
        ),
    ]
)


@app.callback(
    dash.dependencies.Output("worktime-graph", "figure"),
    [
        dash.dependencies.Input("type-of-work-dropdown", "value"),
        dash.dependencies.Input("author-name-dropdown", "value"),
        dash.dependencies.Input("date-picker-range", "start_date"),
        dash.dependencies.Input("date-picker-range", "end_date"),
    ],
)
def update_figure(selected_type_of_work, selected_author_name, start_date, end_date):
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    if selected_type_of_work:
        filtered_df = filtered_df[filtered_df["type_of_work"].isin(selected_type_of_work)]

    if selected_author_name:
        filtered_df = filtered_df[filtered_df["author_name"].isin(selected_author_name)]

    data = []

    for type_of_work in filtered_df["type_of_work"].unique():
        df_subset = filtered_df[filtered_df["type_of_work"] == type_of_work]
        fillcolor = None
        stackgroup = None
        if type_of_work == "QC":
            fillcolor = "red"
            stackgroup = "one"
        elif type_of_work == "LQA":
            fillcolor = "green"
            stackgroup = "one"
        elif type_of_work == "QA":
            fillcolor = "yellow"
            stackgroup = "one"
        elif type_of_work == "meetings":
            fillcolor = "blue"
            stackgroup = "one"
        data.append(
            {
                "x": df_subset["date"],
                "y": df_subset["worktime"],
                "type": "scatter",
                "mode": "lines",
                "name": type_of_work,
                "fill": "tonexty",
                "fillcolor": fillcolor,
                "line": {"shape": "spline", "smoothing": 1.3},
                "stackgroup": stackgroup,
                "line_group": type_of_work,
            }
        )
    data.append(
        {
            "x": filtered_df["date"].unique(),
            "y": [120] * len(filtered_df["date"].unique()),
            "type": "scatter",
            "mode": "lines",
            "name": "Max worktime per week",
            "line": {"color": "black", "dash": "dash"},
        }
    )

    fig = {
        "data": data,
        "layout": {
            "title": "Worktime for {}".format(
                ", ".join(selected_type_of_work) if selected_type_of_work else "all types of work"
            ),
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Worktime (hours)", "range": [0, 140]},
            "barmode": "stack",
        },
    }
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
