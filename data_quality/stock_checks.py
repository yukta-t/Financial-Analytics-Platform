import pandas as pd
from datetime import datetime
from data_quality.base import quality_result

def validate_date_fields(df):
    temp = df.copy()

    temp["parsed_date"] = pd.to_datetime(
        temp["date"],
        errors="coerce"
    )

    failed = temp[
        temp["parsed_date"].isna()
    ]

    future_dates = temp[
        temp["parsed_date"] > pd.Timestamp.today()
    ]

    failed = pd.concat(
        [failed, future_dates]
    ).drop_duplicates()

    return quality_result(
        "Date Validity",
        failed
    )


def validate_price_ranges(df):

    failed = df[
        (df["high"] < df["low"]) |
        (df["open"] < df["low"]) |
        (df["open"] > df["high"]) |
        (df["close"] < df["low"]) |
        (df["close"] > df["high"]) |
        (df["close"] < 0)
    ]

    return quality_result(
        "Price Sanity",
        failed
    )


def validate_volume(df):

    failed = df[
        df["volume"].isna()  #checks missing null nan values 
        |                       # or 
        (df["volume"] < 0)         # if the volume is negative 
    ]

    return quality_result(
        "Volume Validation",
        failed
    )


def check_duplicate_records(df):

    failed = df[
        df.duplicated(
            subset=["date","ticker"],
            keep=False
        )
    ]

    return quality_result(
        "Duplicate Records",
        failed
    )



def validate_vwap(df):

    failed = df[
        (df["vwap"] < df["low"])
        |
        (df["vwap"] > df["high"])
    ]

    return quality_result(
        "VWAP Validation",
        failed
    )


def run_all_stock_checks(df):

    return [
        validate_date_fields(df),
        validate_price_ranges(df),
        validate_volume(df),
        check_duplicate_records(df),
        validate_vwap(df)
    ]