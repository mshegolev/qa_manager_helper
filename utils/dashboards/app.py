# app.py
# ignore

import sqlite3

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

colors = {"background": "#111111", "text": "#7FDBFF"}

db_path = "230318_raw_jira.db"
db_table = "MYPROJECT1_qa_velocity"
query = (
    "select json_each.value as type_of_work,"
    "substr(started,0,5)||'-'||substr(started,6,2)||'-'||substr(started,9,2) as date,"
    "author_name as author_name,"
    "sum(timeSpentSeconds)/3600 as worktime "
    "from MYPROJECT1_qa_velocity, json_each(MYPROJECT1_qa_velocity.labels) "
    "where json_each.value in ('QC','QA', 'LQA', 'meetings') and date not null "
    "group by json_each.value, substr(started,0,5)||'-'||substr(started,6,2)||'-'||substr(started,9,2),author_name;"
)

con = sqlite3.connect(db_path)
data = pd.read_sql(sql=query, con=con)
data.to_csv("data.csv", index=False)
data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d")
data.sort_values("date", inplace=True)
#  value       date  worktime

fig = px.area(data, x="date", y="worktime", color="value", line_group="value", line_shape="spline")

fig.update_layout(plot_bgcolor=colors["background"], paper_bgcolor=colors["background"], font_color=colors["text"])
# fig.update_xaxes(
#     dtick="W1",
#     tickformat="%d\n%m\n%y"
# )

app = Dash(__name__)
app.title = "Отчеты качества проектов"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Таблица 1. Таблица производительности команды тестирования", className="header-title"
                ),
                html.P(
                    """Как читать отчет?
                На этой таблице нужно следить за балансом QA и QC, если на протяжении продолжительного
                времени задачи QC преобладают, это означает что на проекте есть проблемы с тестами/автотестами
                и при продолжительном росте от 3-х недель приведет к тому что не будет тест кейсов по которым
                                                можно провести тестирования.
                Рекомендация:

                1. Разобраться почему на проекте идет дедлайн и тестировщики не успевают создавать обязательные
                тестовые артефакты.
                2. Внедрить автоматизацию на проекте рутинных задач, если ручные тестировщика проводят
                регресс который отнимает много
                   времени.
                3. TBD.""",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        dcc.Graph(id="example-graph-2", figure=fig),
        # dcc.Graph(
        #     id="price-chart",
        #     config={"displayModeBar": False},
        #     figure={
        #         "data": [
        #             {
        #                 "x": data["date"],
        #                 "y": data["worktime"],
        #                 # "type": "lines",
        #                 'type': 'bar',
        #                 "hovertemplate": "%{y:.d}h"
        #                                  "<extra></extra>",
        #             },
        #             {
        #                 "x": data["date"],
        #                 "y": data["worktime"],
        #                 "type": "bar",
        #                 "hovertemplate": "%{y:.d}h"
        #                                  "<extra></extra>",
        #             },
        #         ],
        #         "layout": {
        #             "title": {"text": "worktime это время которое списали на задачу",
        #                       "x": 0.05,
        #                       "xanchor": "left"},
        #             "xaxis": {"fixedrange": True},
        #             "yaxis": {"fixedrange": True},
        #             "colorway": ["#123123", "#00FF00"],
        #         },
        #     },
        # ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
