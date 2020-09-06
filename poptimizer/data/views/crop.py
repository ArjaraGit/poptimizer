"""Запросы содержащие обрезку по первоначальной дате - для внутреннего использования."""
import functools
from typing import List, Tuple

import pandas as pd

from poptimizer.data.config import bootstrap
from poptimizer.data.ports import base, col


def conomy(ticker: str) -> pd.DataFrame:
    """Информация по дивидендам с conomy.ru."""
    table_name = base.TableName(base.CONOMY, ticker)
    requests_handler = bootstrap.get_handler()
    df = requests_handler.get_df(table_name)
    start_date = bootstrap.get_start_date()
    return df.loc[start_date:]  # type: ignore


def dohod(ticker: str) -> pd.DataFrame:
    """Информация по дивидендам с dohod.ru."""
    table_name = base.TableName(base.DOHOD, ticker)
    requests_handler = bootstrap.get_handler()
    df = requests_handler.get_df(table_name)
    start_date = bootstrap.get_start_date()
    return df.loc[start_date:]  # type: ignore


def dividends(ticker: str, force_update: bool = False) -> pd.DataFrame:
    """Дивиденды для данного тикера."""
    table_name = base.TableName(base.DIVIDENDS, ticker)
    requests_handler = bootstrap.get_handler()
    df = requests_handler.get_df(table_name, force_update)
    start_date = bootstrap.get_start_date()
    return df.loc[start_date:]  # type: ignore


def cpi() -> pd.Series:
    """Потребительская инфляция."""
    table_name = base.TableName(base.CPI, base.CPI)
    requests_handler = bootstrap.get_handler()
    df = requests_handler.get_df(table_name)
    start_date = bootstrap.get_start_date()
    return df.loc[start_date:, col.CPI]  # type: ignore


def index() -> pd.DataFrame:
    """Загрузка данных по индексу полной доходности с учетом российских налогов - MCFTRR."""
    table_name = base.TableName(base.INDEX, base.INDEX)
    requests_handler = bootstrap.get_handler()
    df = requests_handler.get_df(table_name)
    start_date = bootstrap.get_start_date()
    return df.loc[start_date:, col.CLOSE]  # type: ignore


@functools.lru_cache(maxsize=1)
def quotes(tickers: Tuple[str, ...]) -> List[pd.DataFrame]:
    """Информация о котировках для заданных тикеров.

    :param tickers:
        Перечень тикеров, для которых нужна информация.
    :return:
        Список с котировками.
    """
    group: base.GroupName = base.QUOTES
    requests_handler = bootstrap.get_handler()
    dfs = requests_handler.get_dfs(group, tickers)
    start_date = bootstrap.get_start_date()
    return [df.loc[start_date:] for df in dfs]  # type: ignore