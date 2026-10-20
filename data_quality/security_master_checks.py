import pandas as pd
from data_quality.base import quality_result 

def validate_sm_numeric_ranges(df):

    failed = df[
        (df["price"] <= 0)   # price must be greater than 0 
        |
        (df["price"] > 100000)   # price must not exceed 100,000, this is a RANGE CHECK 
        |
        (df["duration"] < 0)   # duration must be non-negative    (for bonds, duration measures sensitivity to interest rate changes)
        |
        (df["convexity"] < 0)    #convexity measures how a bond's duration changes when interest rates move
        |
        (df["convexity"] > 1000)
    ]

    return quality_result(
        "Security Master Numeric Ranges",
        failed
    )


def check_duplicate_ssm_id(df):

    failed = df[
        df.duplicated(
            subset=["ssm_id"],
            keep=False
        )
    ]

    result = quality_result(
        "Duplicate SSM_ID Check",
        failed
    )

    if len(failed) > 0:             #checks whether any duplicate rows were found
        result["merge_key_suggestion"] = "ssm_id"  #if we're merging or cleaning duplicates, use ssm_id as the identifier

    return result


def check_duplicate_name_isin(df):
    """Skip as NOT APPLICABLE when either duplicate-detection key is absent."""
    missing_columns = [
        column
        for column in ("name", "isin")
        if column not in df.columns
    ]
    if missing_columns:
        return quality_result(
            "Duplicate Name ISIN Check "
            f"(NOT APPLICABLE: missing {', '.join(missing_columns)})",
            df.iloc[:0]
        )

    failed = df[
        df.duplicated(
            subset=[
                "name",
                "isin"   #ISIN = International Securities Identification Number
            ],
            keep=False
        )
    ]

    return quality_result(
        "Duplicate Name ISIN Check",
        failed
    )


def calculate_completeness(df):   # finds how much of the data is actually filled in   "How many values are present?"

    columns = [
        "isin",
        "ssm_id",
        "issuer_country"
    ]

    result = {}

    total_rows = len(df)

    for col in columns: # loops for all cols- isin, ssm_id, issuer_country

        populated = df[col].notna().sum()   # count non null values 

        result[col] = round(
            (populated / total_rows) * 100,  # calc percentage and rounds to 2 decimals for each col 
            2
        )

    return result




def check_identifier_uniqueness(df):    #"How many IDs are unique?"

    total_rows = len(df)

    distinct_ids = df["ssm_id"].nunique()   #  counts no of  unique values 

    percentage = round(
        (distinct_ids / total_rows) * 100,     #uniqueness percentage of the identifier
        2
    )

    return {
        "metric_name": "Identifier Uniqueness",
        "unique_ids": distinct_ids,
        "total_rows": total_rows,
        "uniqueness_percent": percentage
    }


def run_all_security_master_checks(df):

    return [
        validate_sm_numeric_ranges(df),
        check_duplicate_ssm_id(df),
        check_duplicate_name_isin(df)
    ]