import pandas as pd

def calculate_completeness(
    df,
    critical_columns
):

    total_rows = len(df)

    result = {}

    for column in critical_columns:

        null_count = df[column].isna().sum()

        completeness = (
            1 - (
                null_count / total_rows
            )
        ) * 100

        result[column] = round(
            completeness,
            2
        )

    return result




def calculate_uniqueness(
    df,
    identifier_column
):

    total_rows = len(df)

    unique_ids = df[
        identifier_column
    ].nunique()

    percentage = (
        unique_ids
        /
        total_rows
    ) * 100

    return {
        "unique_ids": unique_ids,
        "total_rows": total_rows,
        "uniqueness_percent": round(
            percentage,
            2
        )
    }




def get_currency_distribution(df):

    counts = (
        df["currency_issue"]
        .value_counts()
    )

    percentages = (
        df["currency_issue"]
        .value_counts(normalize=True)
        * 100
    )

    result = pd.DataFrame({

        "currency":
            counts.index,

        "count":
            counts.values,

        "percentage":
            percentages.values.round(2)
    })

    return result



def get_average_price_by_sector(df):

    result = (
        df.groupby("security_sector")["price"]
        .mean()
        .reset_index()
    )

    result.rename(
        columns={
            "price": "average_price"
        },
        inplace=True
    )

    return result