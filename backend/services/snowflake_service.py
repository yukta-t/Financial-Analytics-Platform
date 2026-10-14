import pandas as pd


def load_table(datatype):

    if datatype == "stock":

        return pd.DataFrame({
            "ticker": ["AAPL", "AAPL"],
            "date": ["2025-01-01", "2025-01-02"],
            "close": [100, 110],
            "volume": [1000, 1200]
        })

    elif datatype == "bonds":

        return pd.DataFrame({
            "ticker": ["BOND1"],
            "price": [1000]
        })

    elif datatype == "security_master":

        return pd.DataFrame({
            "ssm_id": ["SSM001"],
            "price": [100]
        })

    raise ValueError(
        "Invalid datatype"
    )
