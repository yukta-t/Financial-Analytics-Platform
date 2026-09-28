import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestSnowflakeConnection:
    """Test Snowflake connectivity."""
    
    def test_env_variables_loaded(self):
        """Verify environment variables are set."""
        assert os.getenv('SNOW_USER') is not None, "SNOW_USER not set"
        assert os.getenv('SNOW_PWD') is not None, "SNOW_PWD not set"
        assert os.getenv('SNOW_ACCOUNT') is not None, "SNOW_ACCOUNT not set"
    
    def test_snowflake_connection(self):
        """Test actual Snowflake connection."""
        from snowflake_connector.connector import SnowflakeConnector
        
        connector = SnowflakeConnector()
        try:
            connector.connect()
            # Connection successful
            assert connector.connection is not None
        except Exception as e:
            pytest.fail(f"Failed to connect to Snowflake: {str(e)}")
        finally:
            connector.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])