# Majority of setup code omitted for brevity


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
