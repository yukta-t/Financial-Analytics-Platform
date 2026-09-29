import pandas as pd
from data_quality.base import quality_result

def validate_maturity_date(df):

    temp = df.copy() # so original dataset isnt modified 

    temp["date"] = pd.to_datetime(temp["date"]) # convert date col to actual datetime values 
    temp["date_of_maturity"] = pd.to_datetime(     
        temp["date_of_maturity"]                # convert maturity date to datetime values also 
    )

    failed = temp[
        temp["date_of_maturity"] < temp["date"]
    ]

    return quality_result(
        "Maturity Date Validation",
        failed
    )



def validate_bond_numerics(df):

    failed = df[
        (df["volume"] < 0)  #Number of bonds traded cant be negative 
        |
        (df["value"] < 0)  #Total monetary value of the trades cant be negative  (value = 500000 ie ₹500,000 worth of bonds were traded)
        |
        (df["trades"] < 0) #Number of transactions executed cant be negative 
    ]

    return quality_result(
        "Bond Numeric Validation",
        failed
    )


def validate_bond_vwap(df):

    failed = df[
        (df["vwap"] < df["low"])
        |
        (df["vwap"] > df["high"])
    ]

    return quality_result(
        "Bond VWAP Validation",
        failed
    )


def check_unique_trades(df):

    failed = df[
        df.duplicated(
            subset=[
                "date",
                "ticker",
                "series"
            ],
            keep=False
        )
    ]

    return quality_result(
        "Duplicate Trade Check",
        failed
    )


def validate_prev_close_consistency(df):          # The prev_close value stored for today should closely match yesterday's actual close price.
  
    temp = df.copy()

    temp = temp.sort_values(    # sorts in chronological order 
        ["ticker","date"]
    )

    temp["previous_day_close"] = (
        temp.groupby("ticker")["close"]    # groups records ticker-wise 
        .shift(1)                           #moves values down by one row (previous row's close becomes today's previous_day_close(new col apart from 'close'))
    )

    temp["pct_diff"] = (                        #this calculates how far apart the values are (prev_close-prev_day_close)/prev_day_close
        abs(                                      #use abs so that negative change also gives us the discrepancy 
            temp["prev_close"] -
            temp["previous_day_close"]
        )
        /
        temp["previous_day_close"]
    )

    failed = temp[
        temp["pct_diff"] > 0.05           # discrepancy greater than 5% means failure doe
    ]

    return quality_result(
        "Prev Close Consistency",
        failed
    )


def run_all_bond_checks(df):

    return [
        validate_maturity_date(df),
        validate_bond_numerics(df),
        validate_bond_vwap(df),
        check_unique_trades(df),
        validate_prev_close_consistency(df)
    ]