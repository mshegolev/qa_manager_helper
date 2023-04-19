import datetime

from dateutil.parser import parse as parse_date
from jsonpath_rw_ext import parse as parse_json


def search(json, jsonpath):
    match = parse_json(jsonpath).find(json)
    if not match:
        raise KeyError(f'Указанный jsonpath не найден: "{jsonpath}"')
    return match[0].value


def search_all(json, jsonpath):
    match = parse_json(jsonpath).find(json)
    if not match:
        raise KeyError(f'Указанный jsonpath не найден: "{jsonpath}"')
    return list(item.value for item in match)


def convert_null_dict(value: dict):
    """Преобразование к None словаря, полученного из XML-ответа и означающего отсутствие значения"""
    if value == {"@i:nil": "true"}:
        return None
    return value


def convert_currency_code(value: str):
    """Преобразование кода валюты, получаемого из MYSUBPROJECT1 и означающего рубли"""
    if value == "810":
        return "RUB"
    return value


def convert_keyword(value: str):
    """Преобразование строкового представления true/false к булевому типу"""
    mapping = {"true": True, "false": False, "None": None}
    if value in mapping:
        return mapping[value]
    return value


def convert_datetime(value: str, ignoretz=False):
    """Преобразование строкового представления даты к объекту datetime"""
    if isinstance(value, str):
        return parse_date(value, ignoretz=ignoretz)
    return value


def convert_float(value: str):
    """Округление числа с плавающей точкой до 2-х знаков после запятой"""
    if value.replace(".", "").isdigit():
        return f"{float(value):.2f}"
    return value


def convert_name(value: str):
    """Преобразование строк к единообразному виду"""
    if isinstance(value, str):
        return value.replace("\n", "").lower()
    return value


def convert_pm_currency(pm_currency: str) -> str:
    if pm_currency == "643":
        return "RUB"
    if pm_currency == "840":
        return "USD"
    if pm_currency == "978":
        return "EUR"
    if pm_currency == "980":
        return "UAH"
    if pm_currency == "398":
        return "KZT"
    if pm_currency == "933":
        return "BYN"


def convert_pm_period_quant(pm_period_quant: str) -> str:
    if pm_period_quant == "day":
        return "DAY"
    if pm_period_quant == "week":
        return "WEEK"
    if pm_period_quant == "month":
        return "MONTH"


def convert_date(date: str, timedelta: int = None, only_date: bool = False) -> str:
    if timedelta:
        c_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(days=timedelta)
    else:
        c_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    if only_date is True:
        return c_date.strftime("%Y-%m-%d")
    else:
        return c_date.strftime("%Y-%m-%dT%H:%M:%SZ")
