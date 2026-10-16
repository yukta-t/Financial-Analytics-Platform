from dotenv import load_dotenv

from snowflake_connector.connector import (
    SnowflakeConnector
)

load_dotenv()


def load_table(datatype):

    table_mapping = {

        "stock": "FINANCIAL_DB.PUBLIC.STOCK",
        "bonds": "FINANCIAL_DB.PUBLIC.BONDS",
        "security_master": "FINANCIAL_DB.PUBLIC.SECURITY_MASTER"


    }

    if datatype not in table_mapping:

        raise ValueError(
            "Invalid datatype"
        )

    connector = SnowflakeConnector()

    try:

        connector.connect()

        df = connector.fetch_table(
            table_mapping[datatype]
        )

        # normalize columns
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        return df

    finally:

        connector.disconnect()