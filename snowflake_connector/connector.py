import os
import logging
from snowflake.connector import connect
import pandas as pd

logger = logging.getLogger(__name__)

class SnowflakeConnector:
    """
    Manages connection to Snowflake database.
    Credentials sourced from environment variables.
    """
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """
        Establish connection to Snowflake.
        Credentials from: SNOW_USER, SNOW_PWD, SNOW_ACCOUNT, SNOW_WAREHOUSE, SNOW_DATABASE, SNOW_SCHEMA
        """
        try:
            self.connection = connect(
                user=os.getenv('SNOW_USER'),
                password=os.getenv('SNOW_PWD'),
                account=os.getenv('SNOW_ACCOUNT'),
                warehouse=os.getenv('SNOW_WAREHOUSE'),
                database=os.getenv('SNOW_DATABASE'),
                schema=os.getenv('SNOW_SCHEMA')
            )

            cursor = self.connection.cursor()

            cursor.execute("""
            SELECT
            CURRENT_DATABASE(),
            CURRENT_SCHEMA(),
            CURRENT_ROLE()
            """)

            print("SNOWFLAKE CONTEXT:", cursor.fetchall())


            logger.info("Successfully connected to Snowflake")
            return self.connection
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            raise
    
    def disconnect(self):
        """Close Snowflake connection."""
        if self.connection:
            self.connection.close()
            logger.info("Snowflake connection closed")
    
    def fetch_table(self, table_name: str, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch data from a table.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows to fetch
        
        Returns:
            pandas DataFrame
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=columns)
            return df
        except Exception as e:
            logger.error(f"Error fetching {table_name}: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute custom SQL query.
        
        Args:
            query: SQL query string
        
        Returns:
            pandas DataFrame
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=columns)
            return df
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise


# Example usage (for testing)
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    # Load environment variables from .env
    load_dotenv()
    
    connector = SnowflakeConnector()
    try:
        connector.connect()
        print("✅ Connection successful!")
        
        # Try fetching a simple query
        result = connector.execute_query("SELECT CURRENT_DATE()")
        print(f"Current date from Snowflake: {result}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        connector.disconnect()



# Example usage (for testing)
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    # Load environment variables from .env
    load_dotenv()
    
    connector = SnowflakeConnector()
    try:
        connector.connect()
        print("✅ Connection successful!")
        
        # Try fetching a simple query
        result = connector.execute_query(
    "SHOW TABLES"
)

        print(f"Tables in Snowflake: {result}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        connector.disconnect()