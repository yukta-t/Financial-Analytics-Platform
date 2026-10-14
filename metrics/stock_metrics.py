import numpy as np
import pandas as pd 


def calculate_daily_return(df):     # (Close[t]​/Close[t−1]​)−1    ie (todays close/ yesterdays close) - 1

    temp = df.copy()

    temp = temp.sort_values(
        ["ticker", "date"]
    )

    temp["daily_return"] = (
        temp.groupby("ticker")["close"]
        .pct_change()
    )

    return temp



def calculate_log_return(df):      # ln(Close[t]​/Close[t−1]​)

    temp = df.copy()         # 
    temp = temp.sort_values(
        ["ticker","date"]
    )

    temp["log_return"] = np.log(                
        temp["close"] /
        temp.groupby("ticker")["close"].shift(1)    # previous close 
    )

    return temp


def calculate_sma(df, window=20):      # sum of closing prices/ no of days 

    temp = df.copy()

    temp = temp.sort_values(
        ["ticker","date"]
    )

    temp["sma"] = (
        temp.groupby("ticker")["close"]
        .transform(           #transform() keeps the original number of rows
            lambda x:
            x.rolling(
                window=window,
                min_periods=1
            ).mean()
        )
    )

    return temp


def calculate_ema(df, window=20):   #EMAt​=αCloset​+(1−α)EMAt−1​   ie (alpha * todays close + (1-alpha) * yesterdays ema)  

    temp = df.copy()                       # alpha is the smoothing factor for the EMA, calculated as 2 / (window + 1)

    temp = temp.sort_values(
        ["ticker","date"]
    )

    temp["ema"] = (
        temp.groupby("ticker")["close"]
        .transform(
            lambda x:
            x.ewm(            #Pandas automatically computes EMA- exponentially weighted moving average
                span=window,   # default: window=20 
                adjust=False                 # α = 2/(span+1) pandas internally computes 
            ).mean()
        )                                  # if u get alpha= 0.0952 ie 9.5% this means Today's Price gets about 9.5% influence. 
                                            # The remaining 90.5% comes from previous EMA.
    )

    return temp

def calculate_volatility(    # std(returns) × root(252)​                      Daily volatility * root(252)
    df,
    window=30
):

    temp = calculate_daily_return(df)

    temp["volatility"] = (
        temp.groupby("ticker")["daily_return"]
        .transform(
            lambda x:
            x.rolling(
                window,
                min_periods=2
            ).std()             # calculate standard deviation of daily returns over the rolling window
            * np.sqrt(252)           #252 trading days per year in a stock mkt 
        )
    )

    return temp


def calculate_vwap(df):      #    ∑( price × volume) ​/ ∑ volume

    temp = df.copy()

    temp["price_volume"] = (
        temp["close"] *
        temp["volume"]
    )

    vwap = (
        temp["price_volume"].sum()
        /
        temp["volume"].sum()
    )

    return {
        "vwap": round(vwap, 4)
    }



def calculate_dividend_yield(df):    # Dividend/Close

    temp = df.copy()

    temp["dividend_yield"] = (
        temp["dividends"]
        /
        temp["close"]
    )

    return temp



def run_all_stock_metrics(df):

    return {
        "daily_return":
            calculate_daily_return(df),

        "log_return":
            calculate_log_return(df),

        "sma":
            calculate_sma(df),

        "ema":
            calculate_ema(df),

        "volatility":
            calculate_volatility(df),

        "vwap":
            calculate_vwap(df),

        "dividend_yield":
            calculate_dividend_yield(df)
    }