import pandas as pd
import plotly.express as px
from dash import dash, dcc, html
from dash.dependencies import Input, Output

df = pd.read_csv("data.csv", date_parser="date")
df["date"] = pd.to_datetime(df["date"])

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
    Output("worktime-graph", "figure"),
    [
        Input("type-of-work-dropdown", "value"),
        Input("author-name-dropdown", "value"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    ],
)
def update_figure(selected_type_of_work, selected_author_name, start_date, end_date):
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    if selected_type_of_work:
        filtered_df = filtered_df[filtered_df["type_of_work"].isin(selected_type_of_work)]

    if selected_author_name:
        filtered_df = filtered_df[filtered_df["author_name"].isin(selected_author_name)]

    fig = px.line(
        filtered_df,
        x="date",
        y="worktime",
        color="type_of_work",
        line_group="type_of_work",
        hover_data=["type_of_work", "author_name", "worktime"],
        color_discrete_map={"QC": "red", "QA": "yellow", "LQA": "green", "meetings": "blue"},
    )

    fig.add_hline(y=120, line_dash="dash", line_color="black")

    for i in range(len(filtered_df) - 1):
        if (filtered_df.iloc[i + 1]["date"] - filtered_df.iloc[i]["date"]).days > 1:
            fig.add_vrect(
                x0=filtered_df.iloc[i]["date"],
                x1=filtered_df.iloc[i + 1]["date"],
                fillcolor="gray",
                opacity=0.3,
                line_width=0,
            )

    fig.update_layout(
        title={
            "text": "Worktime for {}".format(
                ", ".join(selected_type_of_work) if selected_type_of_work else "all types of work"
            ),
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Date",
        yaxis_title="Worktime (hours)",
        yaxis_range=[0, 140],
        legend_title="Work type",
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
