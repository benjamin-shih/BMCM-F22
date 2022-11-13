import math
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from . import constants as cnst


def read_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def geo_mean(x: np.ndarray) -> float:
    """
    Geometric mean with overflow protection
    """
    return np.exp(np.log(x).mean())


def green_cost(green_percent: float) -> float:
    """
    Calculate cost of planting based on green percentage
    """
    return 500 * (1 - (green_percent * 0.01))


def green_change(funds: int, prev_green: float, area: int) -> float:
    """
    Calculate change in green percentage given funds
    """
    return ((funds / green_cost(prev_green)) + (prev_green * area)) / area


def temp_change(curr_green: float, prev_green: float, model: LinearRegression) -> float:
    """
    Calculate temperature change resulting from additional green coverage
    """
    return model.predict([[curr_green]]) - model.predict([[prev_green]])


def util(
    population: int,
    prev_green: float,
    curr_green: float,
    poverty_pct: float,
    model: LinearRegression,
) -> float:
    """
    Calculate utility for a tract
    """
    return population * np.log(1 + temp_change(curr_green, prev_green, model)) * np.exp(poverty_pct * 0.01)


def regressor(df: pd.DataFrame) -> LinearRegression:
    X = df["green_percent"].to_numpy().reshape(-1, 1)
    y = df["avg_temp_red"].to_numpy()
    reg = LinearRegression().fit(X, y)
    return reg


def opt(
    x: np.ndarray,
    green_pct: np.ndarray,
    ar: np.ndarray,
    pop: np.ndarray,
    pvty_pct: np.ndarray,
    funds: int,
    injection: int,
    reg: LinearRegression,
) -> Tuple[np.ndarray, float, List]:
    """
    Optimize the utility function for geographic tracts
    Returns geometric mean
    """
    util_delta = []
    util_array = x
    while funds > 0:
        total_util = geo_mean(util_array)
        max_util_delta, max_util_idx = 0, -1
        for idx, u in enumerate(util_array):
            temp = util_array.copy()
            new_green = green_change(injection, green_pct[idx], ar[idx])
            if new_green > 95:
                continue
            else:
                temp[idx] += util(pop[idx], green_pct[idx], new_green, pvty_pct[idx], reg)
                curr_util = geo_mean(temp)
                delta = curr_util - total_util
                if delta >= max_util_delta:
                    max_util_delta = delta
                    max_util_idx = idx
        util_delta.append(total_util)
        ng = green_change(injection, green_pct[max_util_idx], ar[max_util_idx])
        util_array[max_util_idx] += util(pop[max_util_idx], green_pct[max_util_idx], ng, pvty_pct[max_util_idx], reg)
        green_pct[max_util_idx] = ng
        funds -= injection
    return util_array, geo_mean(util_array), util_delta


if __name__ == "__main__":
    x = np.ones(193)  # x is an array of utilities
    df = read_df(cnst.DATA_PATH + cnst.all_col_path)
    green_pcts = df["green_percent"].to_numpy()
    poverty_pcts = df["perc_below_2pov"].to_numpy()
    area = df.area  # array of areas
    population = df.population  # array of populations
    funds = 2000
    reg = regressor(df)
