import math
from numbers import Real

import pandas as pd

from metrics.stock_metrics import (
    calculate_daily_return,
    calculate_volatility
)


class PortfolioInputError(ValueError):
    pass


def get_available_tickers(stock_df):
    if "ticker" not in stock_df.columns:
        raise ValueError("The STOCK dataset does not contain a ticker column")

    tickers = (
        stock_df["ticker"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
    )
    return sorted(ticker for ticker in set(tickers) if ticker)


def _validate_holdings(holdings, available_tickers):
    if not isinstance(holdings, list) or not holdings:
        raise PortfolioInputError("At least one portfolio holding is required")

    normalized_holdings = []
    selected_tickers = set()
    total_weight = 0.0

    for holding in holdings:
        if not isinstance(holding, dict):
            raise PortfolioInputError("Each holding must be an object")

        ticker = holding.get("ticker")
        weight = holding.get("weight")
        if not isinstance(ticker, str) or not ticker.strip():
            raise PortfolioInputError("Each holding must include a ticker")
        if isinstance(weight, bool) or not isinstance(weight, Real):
            raise PortfolioInputError("Each holding weight must be a number")

        ticker = ticker.strip().upper()
        weight = float(weight)
        if not math.isfinite(weight) or weight <= 0 or weight > 100:
            raise PortfolioInputError("Holding weights must be greater than 0 and at most 100")
        if ticker in selected_tickers:
            raise PortfolioInputError(f"Duplicate holding: {ticker}")
        if ticker not in available_tickers:
            raise PortfolioInputError(f"Security is not available in STOCK: {ticker}")

        selected_tickers.add(ticker)
        total_weight += weight
        normalized_holdings.append({
            "ticker": ticker,
            "weight": weight
        })

    if not math.isclose(total_weight, 100.0, rel_tol=0.0, abs_tol=1e-6):
        raise PortfolioInputError("Portfolio allocations must sum to 100%")

    return normalized_holdings


def simulate_portfolio(stock_df, holdings):
    available_tickers = set(get_available_tickers(stock_df))
    normalized_holdings = _validate_holdings(holdings, available_tickers)

    metrics_df = stock_df.copy()
    metrics_df["ticker"] = (
        metrics_df["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    daily_returns = calculate_daily_return(metrics_df)
    rolling_volatility = calculate_volatility(metrics_df)

    expected_return = 0.0
    portfolio_volatility = 0.0
    for holding in normalized_holdings:
        ticker = holding["ticker"]
        weight = holding["weight"] / 100.0
        ticker_returns = pd.to_numeric(
            daily_returns.loc[
                daily_returns["ticker"] == ticker,
                "daily_return"
            ],
            errors="coerce"
        ).dropna()
        ticker_volatility = pd.to_numeric(
            rolling_volatility.loc[
                rolling_volatility["ticker"] == ticker,
                "volatility"
            ],
            errors="coerce"
        ).dropna()

        if ticker_returns.empty or ticker_volatility.empty:
            raise ValueError(
                f"Insufficient historical price data to calculate metrics for {ticker}"
            )

        expected_return += weight * float(ticker_returns.mean())
        portfolio_volatility += weight * float(ticker_volatility.iloc[-1])

    expected_return_percent = expected_return * 100
    volatility_percent = portfolio_volatility * 100
    if volatility_percent < 10:
        risk_score = "Low"
    elif volatility_percent <= 20:
        risk_score = "Medium"
    else:
        risk_score = "High"

    return {
        "expected_return": round(expected_return_percent, 4),
        "volatility": round(volatility_percent, 4),
        "risk_score": risk_score,
        "chart": {
            "labels": [holding["ticker"] for holding in normalized_holdings],
            "values": [holding["weight"] for holding in normalized_holdings]
        }
    }
