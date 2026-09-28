# Step-by-Step Setup Guide

This guide walks you through setting up the project from scratch. **Estimated time: 1-2 hours**.

---

## STEP 1: Verify Prerequisites (15 minutes)

<!-- ### 1.1 Check Python Installation

Open PowerShell and run:
```powershell
python --version
```

**Expected**: Python 3.9 or higher
**If not installed**: Download from https://www.python.org/downloads/

### 1.2 Check Git Installation

```powershell
git --version
```

**If not installed**: Download from https://git-scm.com/ -->

<!-- ### 1.3 Check pip (Python package manager)

```powershell
pip --version
```

**Expected**: Should show pip version (usually installed with Python)

---

## STEP 2: Initialize Project Repository (10 minutes)

### 2.1 Navigate to Project Directory

```powershell
cd C:\Users\Yukta.Thakran\Desktop\poc-trial-2
```

### 2.2 Initialize Git Repository

```powershell
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 2.3 Create .gitignore File

```powershell
# Create .gitignore to exclude sensitive files and caches
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
.venv

# Environment variables (NEVER commit .env with real credentials)
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

# Cache
.cache/
*.cache
"@ | Out-File -Encoding UTF8 .gitignore
```

### 2.4 Create README.md (Placeholder)

```powershell
@"
# Data Quality & Metrics PoC

Financial data quality and metrics calculation platform.

## Quick Start

See 01_SETUP_GUIDE.md for detailed setup instructions.

## Project Structure

- \`config/\` - Configuration files
- \`snowflake_connector/\` - Snowflake connection logic
- \`data_quality/\` - Data quality checks
- \`metrics/\` - Metric calculations
- \`backend/\` - Flask API
- \`templates/\` - HTML templates
- \`static/\` - CSS, JS files
- \`tests/\` - Unit and integration tests
"@ | Out-File -Encoding UTF8 README.md
```

---

## STEP 3: Create Python Virtual Environment (15 minutes)

### 3.1 Create Virtual Environment

```powershell
# Navigate to project directory
cd C:\Users\Yukta.Thakran\Desktop\poc-trial-2

# Create virtual environment named 'venv'
python -m venv venv
```

**What's happening?**
- Virtual environment isolates your project's Python packages
- This prevents conflicts with other projects on your system

### 3.2 Activate Virtual Environment

```powershell
# Windows PowerShell
venv\Scripts\Activate.ps1
```

**Note**: If you get an error about execution policies, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try Activate.ps1 again.

**Expected output**: Your prompt should now show `(venv)` prefix
```
(venv) PS C:\Users\Yukta.Thakran\Desktop\poc-trial-2>
```

### 3.3 Upgrade pip

```powershell
python -m pip install --upgrade pip
```

--- -->

<!-- ## STEP 4: Install Python Dependencies (15 minutes)

### 4.1 Create requirements.txt

Create a file named `requirements.txt` in your project root:

```powershell
@"
# Web Framework
Flask==2.3.0
Flask-Cors==4.0.0
Flask-JWT-Extended==4.5.0
Werkzeug==2.3.0

# Data Processing
pandas==2.0.0
numpy==1.24.0

# Database
snowflake-connector-python==3.0.0
SQLAlchemy==2.0.0

# Testing
pytest==7.3.0
pytest-cov==4.1.0
requests==2.31.0

# Configuration
python-dotenv==1.0.0

# Utilities
PyJWT==2.8.0
"@ | Out-File -Encoding UTF8 requirements.txt
```

### 4.2 Install Dependencies

```powershell
# Make sure virtual environment is activated
pip install -r requirements.txt
``` -->

<!-- **Expected output**: Should show "Successfully installed" messages for all packages
**Time taken**: 2-5 minutes depending on internet speed -->

### 4.3 Verify Installation
  
```powershell
pip list
```

**Expected**: Should show all packages from requirements.txt

---

## STEP 5: Configure Snowflake Connection (15 minutes)

### 5.1 Create .env.sample File

This file documents what environment variables you need (NO real credentials):

```powershell
# @"
# # Snowflake Configuration (SAMPLE - DO NOT COMMIT WITH REAL VALUES)
# SNOW_USER=your_snowflake_username
# SNOW_PWD=your_snowflake_password
# SNOW_ACCOUNT=your_account_identifier
# SNOW_WAREHOUSE=COMPUTE_WH
# SNOW_DATABASE=YOUR_DATABASE
# SNOW_SCHEMA=PUBLIC

# # Flask Configuration
# FLASK_ENV=development
# FLASK_DEBUG=1
# SECRET_KEY=your_secret_key_here_change_in_production

# # JWT Configuration
# JWT_SECRET=your_jwt_secret_here_change_in_production
# JWT_ALGORITHM=HS256

# # Logging
# LOG_LEVEL=INFO
# "@ | Out-File -Encoding UTF8 .env.sample
```

### 5.2 Create .env File with Your Credentials

```powershell
@"
# Snowflake Configuration (REAL CREDENTIALS - NEVER COMMIT THIS)
SNOW_USER=your_actual_username
SNOW_PWD=your_actual_password
SNOW_ACCOUNT=xy12345.us-east-1
SNOW_WAREHOUSE=COMPUTE_WH
SNOW_DATABASE=FINANCIAL_DB
SNOW_SCHEMA=PUBLIC

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# JWT Configuration
JWT_SECRET=dev-jwt-secret-change-in-production
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
"@ | Out-File -Encoding UTF8 .env
```

**IMPORTANT**: Never commit `.env` file - it contains real credentials! ✅ Already in .gitignore

### 5.3 Verify .env is in .gitignore

```powershell
# This file should already exist from STEP 2
Get-Content .gitignore | Select-String ".env"
```

**Expected**: Should show `.env` in the output

---

## STEP 6: Create Project Directory Structure (10 minutes)

### 6.1 Create All Directories

```powershell
# Create directories
New-Item -ItemType Directory -Path config -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path snowflake_connector -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path data_quality -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path metrics -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path backend -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path templates -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path static/js -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path static/css -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path tests -ErrorAction SilentlyContinue
```

### 6.2 Create __init__.py Files

These files mark directories as Python packages:

```powershell
# Create __init__.py in each package directory
@"
"@ | Out-File -Encoding UTF8 config/__init__.py
@"
"@ | Out-File -Encoding UTF8 snowflake_connector/__init__.py
@"
"@ | Out-File -Encoding UTF8 data_quality/__init__.py
@"
"@ | Out-File -Encoding UTF8 metrics/__init__.py
@"
"@ | Out-File -Encoding UTF8 backend/__init__.py
@"
"@ | Out-File -Encoding UTF8 tests/__init__.py
```

### 6.3 Verify Structure

```powershell
# View directory tree
Get-ChildItem -Recurse -Directory | ForEach-Object { Write-Host $_.FullName }
```

---

## STEP 7: Test Snowflake Connection (20 minutes)

### 7.1 Create snowflake_connector/connector.py

```python
# File: snowflake_connector/connector.py
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
```

Save this file in `snowflake_connector/connector.py`

### 7.2 Test the Connection

```powershell
# Make sure virtual environment is activated
# cd to project directory
python snowflake_connector/connector.py
```

**Expected output**: Either ✅ Connection successful! or ❌ with error details

**Troubleshooting**:
- **Error: "No module named snowflake"** → Run `pip install -r requirements.txt` again
- **Error: "Authentication failed"** → Check credentials in .env file
- **Error: "Account identifier invalid"** → Verify SNOW_ACCOUNT format (e.g., xy12345.us-east-1)

---

## STEP 8: Create First Unit Test (15 minutes)

### 8.1 Create pytest.ini

```powershell
@"
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
"@ | Out-File -Encoding UTF8 pytest.ini
```

### 8.2 Create tests/test_snowflake.py

```python
# File: tests/test_snowflake.py
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
```

### 8.3 Run Tests

```powershell
pytest tests/test_snowflake.py -v
```

**Expected output**: Tests pass (assuming Snowflake credentials are correct)

---

## STEP 9: Commit Initial Setup to Git (5 minutes)

```powershell
# Check what files are untracked
git status

# Add all files (except those in .gitignore)
git add .

# Create initial commit
git commit -m "Initial project setup: venv, requirements, Snowflake connector, tests"

# View commit history
git log --oneline
```

---

## STEP 10: Create Development Checklist (5 minutes)

Create a `DEVELOPMENT.md` file to track your progress:

```powershell
@"
# Development Checklist

## Phase 1: Foundation ✅
- [x] Project initialized with git
- [x] Virtual environment created
- [x] Dependencies installed
- [x] .env configured
- [x] Directory structure created
- [x] Snowflake connector module created
- [x] Connection test passing
- [x] Initial tests written

## Phase 2: Data Quality Checks
- [ ] Stock quality checks (5)
- [ ] Bonds quality checks (5)
- [ ] Security Master quality checks (5)
- [ ] Unit tests for all quality checks

## Phase 3: Metric Calculations
- [ ] Stock metrics (7)
- [ ] Bond metrics (5)
- [ ] Security Master metrics (5)
- [ ] Unit tests for all metrics

## Phase 4: Backend API
- [ ] Flask app initialization
- [ ] JWT authentication module
- [ ] POST /api/login endpoint
- [ ] GET /api/metrics endpoint
- [ ] POST /api/execute endpoint
- [ ] GET /api/health endpoint
- [ ] Token validation middleware
- [ ] Integration tests

## Phase 5: Frontend UI
- [ ] HTML template with dropdowns
- [ ] JavaScript for dropdown logic
- [ ] Chart.js integration
- [ ] Login screen
- [ ] Results table and chart display

## Phase 6: Testing & Documentation
- [ ] Comprehensive unit tests (>50)
- [ ] Integration tests (>15)
- [ ] Code coverage report
- [ ] README.md complete
- [ ] API documentation
- [ ] Final commit and review
"@ | Out-File -Encoding UTF8 DEVELOPMENT.md
```

---

## STEP 11: Understand Project Structure (10 minutes)

**Read through the file structure you just created:**

```
poc-trial-2/
├── config/                          # Configuration
│   └── __init__.py
├── snowflake_connector/             # Database connectivity
│   ├── __init__.py
│   └── connector.py (✅ created)
├── data_quality/                    # Data validation
│   └── __init__.py
├── metrics/                         # Calculations
│   └── __init__.py
├── backend/                         # Flask API
│   └── __init__.py
├── templates/                       # HTML
│   └── (index.html - next phase)
├── static/                          # CSS, JS
│   ├── js/
│   └── css/
├── tests/                           # Tests
│   ├── __init__.py
│   └── test_snowflake.py (✅ created)
├── .env (✅ created - DO NOT COMMIT)
├── .env.sample (✅ created)
├── .gitignore (✅ created)
├── requirements.txt (✅ created)
├── README.md (✅ created)
├── pytest.ini (✅ created)
└── DEVELOPMENT.md (✅ created)
```

---

## STEP 12: Verify Everything (5 minutes)

Run this checklist to confirm everything is set up:

```powershell
# 1. Check virtual environment is active (should show (venv) prompt)
Write-Host "Virtual env active: " -NoNewline
if ($env:VIRTUAL_ENV) { Write-Host "✅ YES" } else { Write-Host "❌ NO" }

# 2. Check all required packages installed
Write-Host "`nChecking packages..."
pip list | Select-String "pandas|Flask|snowflake"

# 3. Check .env file exists
Write-Host "`nEnvironment file: " -NoNewline
if (Test-Path .env) { Write-Host "✅ .env exists" } else { Write-Host "❌ .env missing" }

# 4. Check directory structure
Write-Host "`nDirectory structure: " -NoNewline
$dirs = @('config', 'snowflake_connector', 'data_quality', 'metrics', 'backend', 'tests', 'templates', 'static')
$all_exist = $dirs | ForEach-Object { Test-Path $_ } | ForEach-Object { $_ }
if ($all_exist -contains $False) { Write-Host "❌ Some directories missing" } else { Write-Host "✅ All directories exist" }

# 5. Run test
Write-Host "`nRunning test..."
pytest tests/test_snowflake.py::TestSnowflakeConnection::test_env_variables_loaded -v
```

---

## STEP 13: Ready to Start Development (5 minutes)

You're now ready! Next steps:

1. **Read**: `02_LEARNING_RESOURCES.md` for background knowledge
2. **Review**: `00_PROJECT_PLAN.md` Phase 2 section
3. **Start coding**: Implement data quality checks (Phase 2)

### Quick Command Reference

```powershell
# Activate virtual environment
venv\Scripts\Activate.ps1

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_snowflake.py::TestSnowflakeConnection -v

# Install new package
pip install package_name

# Update requirements.txt after adding packages
pip freeze > requirements.txt

# Deactivate virtual environment (when done)
deactivate
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "No module named X" | Run `pip install -r requirements.txt` |
| "Execution policy" error | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| ".env not loading" | Make sure you're in project root directory |
| Snowflake connection fails | Verify credentials in .env; check account identifier format |
| Tests don't run | Ensure pytest.ini is in project root |
| Port 5000 already in use | Change FLASK_PORT in .env or kill process using `lsof` |

---

## Summary

✅ **You have completed Phase 1 setup!**

- ✅ Python environment ready
- ✅ Snowflake connector working
- ✅ Testing framework in place
- ✅ Git repository initialized
- ✅ Project structure ready

**Time to complete**: ~1.5-2 hours
**Next phase**: Data Quality Checks (Phase 2)
