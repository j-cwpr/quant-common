import numpy as np


def sharpe_ratio(returns, periods_per_year=252):
    returns = np.asarray(returns, dtype=float)

    if returns.size == 0:
        return np.nan

    volatility = returns.std(ddof=1)

    if volatility == 0:
        return np.nan

    return np.sqrt(periods_per_year) * returns.mean() / volatility