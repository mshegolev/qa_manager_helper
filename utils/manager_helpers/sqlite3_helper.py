import datetime
import json
import logging
import pathlib
import sqlite3
import uuid

import jira.resources


class Sqlite3Helper:
    db_name: str
    db_path: str

    def __init__(self, db_path=None, db_name=None):
        if db_path is None and db_name:
            self.db_path = pathlib.Path(pathlib.Path.cwd(), "utils", "jira", "data", str(db_name) + ".db").as_posix()
        elif db_path is None:
            self.db_path = pathlib.Path(
                pathlib.Path.cwd(), "utils", "jira", "data", datetime.datetime.now().strftime("%y%m%d_%H%M%S") + ".db"
            ).as_posix()
        else:
            self.db_path = db_path
        self.connection = self.create_connection(db_path)
        self.cursor = self.create_cursor(db_path)
        if db_name is None:
            self.db_name = "jira_" + datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        else:
            self.db_name = db_name

    def is_table_exist(self, db_name=None):
        if db_name is None:
            db_name = self.db_name
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{db_name}'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return len(result) > 0

    def create_table(self, columns, db_path=None, table_name=None):
        if db_path:
            self.cursor = self.create_cursor(db_path)
        if table_name is None:
            table_name = self.db_name
        if self.is_table_exist(table_name):
            return table_name
        columns = "pk INTEGER PRIMARY KEY,uuid," + ",".join([str("'" + _ + "'") for _ in columns])
        query = f"CREATE TABLE '{table_name}' ({columns})"
        self.cursor.execute(query)
        self.connection.commit()
        return table_name

    def create_cursor(self, db_path):
        if self.connection is None:
            self.connection = self.create_connection(db_path)
        cursor = self.connection.cursor()
        return cursor

    def create_connection(self, db_path):
        if db_path is None:
            db_path = self.db_path
        conn = sqlite3.connect(db_path)
        return conn

    def select(self, query):
        self.cursor.execute(query)
        response = self.cursor.fetchall()
        return response

    def insert(self, query, values):
        self.cursor.execute(query, values)
        self.connection.commit()
        return self

    def insert_issue(self, issue, table_name=None, columns=None):
        if table_name is None:
            table_name = self.db_name
        if columns is None:
            columns = self.get_columns()
        query, values = self.generate_insert_issue_query(columns=columns, table_name=table_name, issue=issue)
        self.cursor.execute(query, values)
        self.connection.commit()
        return self

    def generate_insert_issue_query(self, columns, table_name, issue):
        columns = {column: None for column in columns}

        for column in columns.keys():
            try:
                if column == "pk":
                    row_string = None
                elif column in ["uuid"]:
                    row_string = str(uuid.uuid4())
                elif column == "raw":
                    row_string = json.dumps(issue.raw)
                else:
                    row_string = self.generate_property_to_json(issue.get_field(column))
                columns[column] = row_string
            except AttributeError as e:
                logging.error(e.args[0])
                try:
                    if any([isinstance(issue, jira.Issue), isinstance(issue, classmethod)]):
                        row_string = self.generate_property_to_json(getattr(issue, column))
                    elif isinstance(issue, dict):
                        row_string = issue.get(column)
                    columns[column] = row_string
                except Exception:
                    pass
            except UnboundLocalError as e:
                logging.error(e.args[0])
                logging.error(f"Атрибута {column} нет в jira таске.")
        cols = ",".join(["'" + _ + "'" for _ in columns.keys()])
        vals = str("?," * len(columns.keys())).removesuffix(",")
        query = f"INSERT INTO '{table_name}' ({cols}) VALUES ({vals})"
        values = tuple(
            columns.values(),
        )
        return query, values

    def get_columns(self, db_name=None):
        columns = []
        if db_name is None:
            db_name = self.db_name
        q = f"PRAGMA table_info('{db_name}')"
        self.cursor.execute(q)
        response = self.cursor.fetchall()
        for column in response:
            columns.append(column[1])
        return columns

    def generate_property_to_json(self, param, key=None):
        result = {}
        if isinstance(param, jira.resources.PropertyHolder):
            properties = [prop for prop in dir(param) if not prop.startswith("_")]
            for prop in properties:
                result[prop] = param.__getattribute__(prop)
        elif isinstance(param, str):
            return param
        elif isinstance(param, int):
            return str(param)
        elif isinstance(param, list):
            result = str(param)
        elif not param:
            return None
        else:
            return str(param)
        try:
            result = json.dumps(result)
        except Exception as e:
            logging.error(e.args[0])
            result = str(result)
            print(result)
        return result
