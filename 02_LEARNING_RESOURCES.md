# Learning Resources Guide

This document provides curated learning materials organized by topic and phase. **Use this to build foundational knowledge before starting each phase.**

---

## FOUNDATIONAL PYTHON CONCEPTS

### 1. Virtual Environments
**Why you need this**: Isolate project dependencies; avoid conflicts with system Python.

**Resources**:
- Official tutorial: https://docs.python.org/3/tutorial/venv.html
- Real Python guide: https://realpython.com/python-virtual-environments-a-primer/
- Video (10 min): https://www.youtube.com/watch?v=Kg1Yvry_Yuk

**Key concepts to understand**:
- How venv creates isolated Python installations
- Activation and deactivation
- Why requirements.txt matters
- pip freeze vs pip install -r

**Quick exercise**:
```python
# Create, activate, and install a package in venv
python -m venv test_env
test_env\Scripts\Activate.ps1
pip install requests
python -c "import requests; print(requests.__version__)"
deactivate
```

---

### 2. Package Management (pip & requirements.txt)
**Why you need this**: Manage dependencies consistently across team and environments.

**Resources**:
- pip documentation: https://pip.pypa.io/en/stable/
- Real Python - requirements files: https://realpython.com/courses/managing-python-dependencies/
- Semantic versioning: https://semver.org/

**Key concepts**:
- Pinning versions (==) vs ranges (>=, ~=)
- requirements.txt format
- Installing from requirements
- pip freeze
- Difference between requirements.txt and setup.py

**Quick exercise**:
```bash
# Create requirements.txt with pinned versions
pip freeze > requirements.txt

# Install from requirements (clean environment)
pip install -r requirements.txt

# Verify all installed
pip list
```

---

### 3. Environment Variables & .env Files
**Why you need this**: Securely manage credentials without hardcoding them.

**Resources**:
- 12-factor app config: https://12factor.net/config
- python-dotenv docs: https://github.com/theskumar/python-dotenv
- Video (8 min): https://www.youtube.com/watch?v=SqFVVU_q80U

**Key concepts**:
- os.getenv() and os.environ
- .env file format
- Never commit .env to git
- .env.sample as template
- Precedence (environment > .env > defaults)

**Quick exercise**:
```python
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Access variables
user = os.getenv('SNOW_USER')
pwd = os.getenv('SNOW_PWD')

# With defaults
warehouse = os.getenv('SNOW_WAREHOUSE', 'COMPUTE_WH')
```

---

## PHASE 1: DATABASE & CONNECTIVITY

### 1. Snowflake Connector
**Why you need this**: Connect Python applications to Snowflake and fetch data.

**Resources**:
- Official Snowflake Python docs: https://docs.snowflake.com/en/user-guide/python-connector.html
- GitHub repo: https://github.com/snowflakedb/snowflake-connector-python
- Snowflake Python API reference: https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api.html

**Key concepts**:
- Connection object and lifecycle
- Cursor objects
- SQL execution
- Error handling
- Connection pooling (optional for PoC)

**Quick exercise**:
```python
from snowflake.connector import connect

conn = connect(
    user="USER",
    password="PASSWORD",
    account="ACCOUNT",
    warehouse="WH",
    database="DB",
    schema="SCHEMA"
)

# Execute query
cursor = conn.cursor()
cursor.execute("SELECT CURRENT_DATE()")
result = cursor.fetchall()
print(result)

conn.close()
```

---

### 2. SQL for Data Analysis
**Why you need this**: Write efficient queries to push filtering/aggregation to database.

**Resources**:
- SQL tutorial: https://www.w3schools.com/sql/
- PostgreSQL docs (generalizable): https://www.postgresql.org/docs/current/tutorial.html
- Mode SQL tutorial: https://mode.com/sql-tutorial/

**Key concepts**:
- SELECT, WHERE, GROUP BY, ORDER BY
- JOINs (INNER, LEFT, RIGHT)
- Aggregate functions (COUNT, SUM, AVG, MAX, MIN)
- HAVING clause
- LIMIT and pagination
- Date functions (DATE_TRUNC, DATEDIFF, etc.)

**Quick exercise**:
```sql
-- Find stock price anomalies
SELECT DATE, TICKER, CLOSE, HIGH, LOW
FROM STOCKS
WHERE CLOSE > HIGH OR CLOSE < LOW
ORDER BY DATE DESC
LIMIT 10;

-- Calculate daily returns by ticker
SELECT 
    DATE,
    TICKER,
    CLOSE,
    LAG(CLOSE) OVER (PARTITION BY TICKER ORDER BY DATE) AS PREV_CLOSE,
    (CLOSE - LAG(CLOSE) OVER (PARTITION BY TICKER ORDER BY DATE)) / LAG(CLOSE) OVER (PARTITION BY TICKER ORDER BY DATE) AS DAILY_RETURN
FROM STOCKS
ORDER BY TICKER, DATE;
```

---

## PHASE 2: DATA PROCESSING WITH PANDAS

### 1. pandas Fundamentals
**Why you need this**: Manipulate tabular data efficiently in Python.

**Resources**:
- Official tutorials: https://pandas.pydata.org/getting_started/index.html
- "Modern pandas" blog series: https://tomaugspurger.github.io/modern-1-intro.html
- Real Python pandas: https://realpython.com/learning-pandas-data-science/

**Key concepts**:
- Series and DataFrames
- Indexing and selection ([loc, iloc])
- Data types and conversion
- Handling missing values (NaN, None)
- Basic operations (mean, sum, std, etc.)

**Quick exercise**:
```python
import pandas as pd

# Create DataFrame from dict
df = pd.DataFrame({
    'Date': ['2025-01-01', '2025-01-02'],
    'Ticker': ['AAPL', 'AAPL'],
    'Close': [150.0, 151.5]
})

# Convert date column
df['Date'] = pd.to_datetime(df['Date'])

# Filter
apple_data = df[df['Ticker'] == 'AAPL']

# Calculate statistics
print(df['Close'].mean())
print(df['Close'].std())
```

---

### 2. Advanced pandas Operations
**Why you need this**: Perform time-series calculations, grouping, merging.

**Resources**:
- pandas documentation: https://pandas.pydata.org/docs/
- Time-series guide: https://pandas.pydata.org/docs/user_guide/timeseries.html
- Window operations: https://pandas.pydata.org/docs/user_guide/window.html
- Stack Overflow pandas tag: https://stackoverflow.com/questions/tagged/pandas

**Key concepts**:
- groupby() for aggregation
- merge() and join() for combining DataFrames
- Rolling windows for time-series
- resample() for frequency conversion
- apply() and map() for custom functions
- Sorting and ranking

**Quick exercise**:
```python
import pandas as pd
import numpy as np

# Create time-series data
dates = pd.date_range('2025-01-01', periods=100)
df = pd.DataFrame({
    'Date': dates,
    'Ticker': 'AAPL',
    'Close': np.random.randn(100).cumsum() + 150
})

# Calculate 20-day moving average
df['SMA_20'] = df['Close'].rolling(window=20).mean()

# Calculate daily returns
df['Return'] = df['Close'].pct_change()

# Volatility over 30 days
df['Volatility'] = df['Return'].rolling(window=30).std() * np.sqrt(252)

print(df.tail())
```

---

### 3. Data Validation & Cleaning
**Why you need this**: Identify and handle bad data.

**Resources**:
- pandas missing data: https://pandas.pydata.org/docs/user_guide/missing_data.html
- Data validation libraries: https://great-expectations.io/
- Blog post: https://www.datacamp.com/courses/data-cleaning-in-python

**Key concepts**:
- Identifying missing values (isna(), notna())
- Dropping/filling missing data
- Duplicates (drop_duplicates())
- Data type validation
- Outlier detection
- Error logging

**Quick exercise**:
```python
import pandas as pd

df = pd.DataFrame({
    'Date': ['2025-01-01', None, '2025-01-03'],
    'Price': [100, 101, 'invalid'],
    'Volume': [1000, 1000, 1000]
})

# Check for nulls
print(df.isnull())  # Show null locations
print(df.isnull().sum())  # Count nulls per column

# Drop rows with nulls
df_clean = df.dropna()

# Fill nulls with forward fill
df['Date'] = df['Date'].fillna(method='ffill')

# Remove duplicates
df_unique = df.drop_duplicates()
```

---

### 4. Exporting Data
**Why you need this**: Return results to frontend/files.

**Resources**:
- pandas I/O: https://pandas.pydata.org/docs/user_guide/io.html
- JSON with pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html
- CSV operations: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html

**Key concepts**:
- to_dict() for JSON responses
- to_csv() for file export
- to_excel() for spreadsheets
- to_json() with orient options (split, records, index, columns, values)

**Quick exercise**:
```python
import pandas as pd

df = pd.DataFrame({
    'Date': ['2025-01-01', '2025-01-02'],
    'Ticker': ['AAPL', 'MSFT'],
    'Close': [150.0, 310.5]
})

# Convert to API response format
response = {
    'columns': df.columns.tolist(),
    'rows': df.values.tolist()
}
print(response)

# Convert to JSON string
json_str = df.to_json(orient='records')
print(json_str)

# Export to CSV
df.to_csv('output.csv', index=False)
```

---

## PHASE 3: FINANCIAL METRICS

### 1. Stock Market Fundamentals
**Why you need this**: Understand what you're calculating.

**Resources**:
- Khan Academy - Stocks: https://www.khanacademy.org/economics-finance-domain/core-finance/stock-and-bonds
- Investopedia dictionary: https://www.investopedia.com/
- "A Random Walk Down Wall Street" - Burton Malkiel (book)

**Key concepts**:
- Stock price vs returns
- Open, High, Low, Close (OHLC)
- Volume and liquidity
- Moving averages
- Volatility
- Dividend yield

**Important formulas**:
```
Daily Return = (Close_t - Close_{t-1}) / Close_{t-1}
Log Return = ln(Close_t / Close_{t-1})
Simple Moving Average = Sum(Close[t-n:t]) / n
Annualized Volatility = Daily_Std * sqrt(252)  # 252 trading days/year
```

---

### 2. Bond Mathematics
**Why you need this**: Complex calculations for fixed income.

**Resources**:
- Introduction to bonds: https://www.investopedia.com/terms/b/bond.asp
- Yield to Maturity explained: https://www.investopedia.com/terms/y/yieldtomaturity.asp
- Duration and convexity: https://www.investopedia.com/terms/d/duration.asp
- Numerical methods for YTM: https://www.youtube.com/watch?v=eIEn1bnMEAE

**Key concepts**:
- Face value, coupon rate, maturity
- Yield to Maturity (YTM) - the internal rate of return
- Macaulay Duration - average time to receive cash flows
- Modified Duration - price sensitivity to yield changes
- DV01 - dollar value of 1 basis point
- Present Value calculation

**Important formulas**:
```
Bond Price = Sum(Coupon / (1+y)^t) + FaceValue / (1+y)^N
YTM = y (solve iteratively using Newton-Raphson)
Macaulay Duration = Sum(t * CF_t / (1+y)^t) / Price
Modified Duration = Macaulay Duration / (1 + y)
DV01 = -Modified Duration * Price / 10000
```

---

### 3. Numerical Methods (Newton-Raphson)
**Why you need this**: Solve YTM equation iteratively.

**Resources**:
- Newton-Raphson method: https://en.wikipedia.org/wiki/Newton%27s_method
- Khan Academy calculus: https://www.khanacademy.org/math/calculus
- Numerical Recipes book (classic reference)

**Key concepts**:
- Function and derivative
- Iterative convergence
- Stopping criteria
- Handling no-convergence cases

**Example implementation**:
```python
def newton_raphson(f, df, x0, max_iter=100, tol=1e-6):
    """
    f: function
    df: derivative
    x0: initial guess
    """
    x = x0
    for i in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = df(x)
        x = x - fx / dfx
    return x

# Example: solve y^2 = 2 (sqrt(2))
def f(x): return x**2 - 2
def df(x): return 2*x
result = newton_raphson(f, df, 1.0)
print(result)  # ≈ 1.414
```

---

## PHASE 4: WEB BACKEND

### 1. Flask Framework Basics
**Why you need this**: Build lightweight REST API.

**Resources**:
- Official Flask tutorial: https://flask.palletsprojects.com/
- Miguel Grinberg's mega-tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- Real Python Flask by example: https://realpython.com/flask-by-example-part-1-project-setup/

**Key concepts**:
- Creating Flask app
- Routes and methods (GET, POST, etc.)
- Request/response handling
- JSON serialization
- Error handling (try/except)
- Logging

**Quick exercise**:
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello():
    name = request.args.get('name', 'World')
    return jsonify({'message': f'Hello, {name}!'})

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.get_json()
    # Process data
    return jsonify({'status': 'ok', 'received': data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Testing locally**:
```bash
# Terminal 1: Start server
python backend/app.py

# Terminal 2: Make requests
curl http://localhost:5000/api/hello?name=Alice
curl -X POST http://localhost:5000/api/data -H "Content-Type: application/json" -d '{"key":"value"}'
```

---

### 2. JWT Authentication
**Why you need this**: Secure API endpoints with tokens.

**Resources**:
- JWT.io introduction: https://jwt.io/introduction
- PyJWT docs: https://pyjwt.readthedocs.io/
- Flask-JWT-Extended: https://flask-jwt-extended.readthedocs.io/
- Blog: https://www.toptal.com/web/cookie-free-authentication-with-json-web-tokens-an-overview

**Key concepts**:
- JWT structure (header.payload.signature)
- Token generation and validation
- Expiration
- Decorators for protecting routes

**Quick exercise**:
```python
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-key-change-in-production'
jwt = JWTManager(app)

@app.route('/api/login', methods=['POST'])
def login():
    # Verify username/password (simplified)
    username = 'user'
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token})

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    username = get_jwt_identity()
    return jsonify({'message': f'Hello, {username}!'})
```

---

### 3. REST API Design
**Why you need this**: Design consistent, usable APIs.

**Resources**:
- REST API best practices: https://restfulapi.net/
- HTTP status codes: https://httpstatuses.com/
- API versioning: https://www.troyhunt.com/your-api-versioning-is-wrong-which-is/

**Key concepts**:
- Resource-oriented design
- Proper HTTP methods and status codes
- Request/response formats (JSON)
- Error responses
- Pagination and filtering
- Documentation (Swagger/OpenAPI)

**API design checklist**:
```
✓ Use nouns for resources (/api/metrics, not /api/getMetrics)
✓ Use HTTP methods correctly (GET read, POST create, PUT update, DELETE delete)
✓ Return appropriate status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 500 Server Error)
✓ Include error messages in response: {"status": "error", "message": "Description"}
✓ Version your API: /api/v1/...
✓ Use consistent naming (camelCase, snake_case - pick one)
✓ Paginate large responses: ?page=1&limit=100
✓ Filter on server side: ?ticker=AAPL&start_date=2025-01-01
✓ Document with examples
```

---

## PHASE 5: FRONTEND

### 1. HTML & CSS Basics
**Why you need this**: Build user interface.

**Resources**:
- MDN Web Docs - HTML: https://developer.mozilla.org/en-US/docs/Web/HTML
- MDN Web Docs - CSS: https://developer.mozilla.org/en-US/docs/Web/CSS
- FreeCodeCamp HTML/CSS course: https://www.youtube.com/watch?v=mU6anWqk3SY

**Key concepts**:
- HTML elements (div, input, select, button, table)
- CSS selectors and properties
- Flexbox and Grid
- Responsive design (media queries)
- Bootstrap for quick styling (optional)

**Quick exercise**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 1000px; margin: auto; }
        button { padding: 10px 20px; background: blue; color: white; cursor: pointer; }
        button:hover { background: darkblue; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Metrics</h1>
        <select id="dataType"><option>Select Type</option></select>
        <select id="metric"><option>Select Metric</option></select>
        <button onclick="execute()">Execute</button>
        <table id="results"></table>
    </div>
</body>
</html>
```

---

### 2. JavaScript & Fetch API
**Why you need this**: Communicate with backend, handle user interactions.

**Resources**:
- MDN JavaScript basics: https://developer.mozilla.org/en-US/docs/Learn/JavaScript/First_steps
- Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- Async/await: https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises

**Key concepts**:
- DOM manipulation (getElementById, querySelector)
- Event listeners (click, change)
- Fetch API (HTTP requests)
- Promises and async/await
- JSON parsing
- Error handling

**Quick exercise**:
```javascript
// Fetch data from API
async function fetchData() {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/metrics?datatype=stock', {
        headers: {'Authorization': `Bearer ${token}`}
    });
    const data = await response.json();
    return data;
}

// Handle button click
document.getElementById('executeBtn').addEventListener('click', async () => {
    const dataType = document.getElementById('dataType').value;
    const metric = document.getElementById('metric').value;
    
    const response = await fetch('/api/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            datatype: dataType,
            metric_id: metric
        })
    });
    
    const result = await response.json();
    displayTable(result.columns, result.rows);
});

function displayTable(columns, rows) {
    let html = '<tr>' + columns.map(c => `<th>${c}</th>`).join('') + '</tr>';
    html += rows.map(row => 
        '<tr>' + row.map(cell => `<td>${cell}</td>`).join('') + '</tr>'
    ).join('');
    document.getElementById('results').innerHTML = html;
}
```

---

### 3. Chart.js for Visualization
**Why you need this**: Display data as charts.

**Resources**:
- Chart.js documentation: https://www.chartjs.org/
- Chart.js examples: https://www.chartjs.org/docs/latest/samples/
- Interactive tutorial: https://www.w3schools.com/graphics/canvas_intro.asp

**Key concepts**:
- Chart types (line, bar, scatter)
- Data format
- Options and configuration
- Updating charts dynamically
- Responsive design

**Quick exercise**:
```javascript
// Include Chart.js in HTML
// <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>

const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        datasets: [{
            label: 'AAPL',
            data: [150, 151, 152, 151, 153],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: true, position: 'top' },
            title: { display: true, text: 'Stock Price' }
        },
        scales: {
            y: { beginAtZero: false }
        }
    }
});
```

---

## PHASE 6: TESTING

### 1. pytest Basics
**Why you need this**: Automate testing, catch regressions.

**Resources**:
- pytest documentation: https://docs.pytest.org/
- Real Python pytest: https://realpython.com/pytest-python-testing/
- Test-driven development: https://en.wikipedia.org/wiki/Test-driven_development

**Key concepts**:
- Test functions (test_*.py)
- Assertions (assert x == y)
- Fixtures (setup/teardown)
- Parametrization (run test with different inputs)
- Coverage reports

**Quick exercise**:
```python
# tests/test_example.py
import pytest

def add(a, b):
    return a + b

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (1, -1, 0),
    (5, 5, 10)
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

# Run: pytest tests/test_example.py -v
```

---

### 2. Mocking & Test Doubles
**Why you need this**: Test without external dependencies (Snowflake, API).

**Resources**:
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- Real Python mocking: https://realpython.com/python-mock-library/
- pytest-mock: https://pytest-mock.readthedocs.io/

**Key concepts**:
- Mock objects
- Patching functions/classes
- Assertions on mock calls
- Side effects
- Test fixtures with mocks

**Quick exercise**:
```python
from unittest.mock import Mock, patch
import pytest

def get_data_from_snowflake(query):
    # Real implementation
    pass

def test_metric_without_snowflake():
    # Mock Snowflake response
    mock_data = Mock()
    mock_data.execute.return_value = [['2025-01-01', 'AAPL', 150.0]]
    
    # Patch the connector
    with patch('module.SnowflakeConnector') as mock_connector:
        mock_connector.return_value.fetch_data.return_value = mock_data
        # Test your metric function
        result = calculate_sma(mock_data)
        assert result is not None
```

---

### 3. Integration Testing
**Why you need this**: Test entire API workflows.

**Resources**:
- Flask test client: https://flask.palletsprojects.com/en/2.3.x/testing/
- requests library: https://docs.python-requests.org/
- Test data factories: https://factoryboy.readthedocs.io/

**Key concepts**:
- Flask test client (app.test_client())
- Setting up test database
- Cleanup after tests
- Testing complete workflows

**Quick exercise**:
```python
def test_api_workflow(client, token):
    # 1. Login
    login_response = client.post('/api/login', 
        json={'username': 'user', 'password': 'pass'})
    token = login_response.json['token']
    
    # 2. Fetch metrics
    metrics_response = client.get('/api/metrics?datatype=stock',
        headers={'Authorization': f'Bearer {token}'})
    assert metrics_response.status_code == 200
    
    # 3. Execute metric
    execute_response = client.post('/api/execute',
        json={'datatype': 'stock', 'metric_id': 'sma'},
        headers={'Authorization': f'Bearer {token}'})
    assert execute_response.status_code == 200
    data = execute_response.json
    assert 'rows' in data
    assert 'columns' in data
```

---

## QUICK REFERENCE: COMMON LIBRARIES

| Library | Purpose | Install | Use Case |
|---------|---------|---------|----------|
| pandas | Data manipulation | `pip install pandas` | DataFrame operations, metrics calc |
| numpy | Numerical computing | `pip install numpy` | Linear algebra, random numbers |
| Flask | Web framework | `pip install Flask` | REST API |
| Flask-JWT-Extended | JWT auth | `pip install Flask-JWT-Extended` | Token-based authorization |
| snowflake-connector-python | Snowflake connection | `pip install snowflake-connector-python` | Database queries |
| SQLAlchemy | ORM/database abstraction | `pip install sqlalchemy` | Optional: query building |
| pytest | Testing framework | `pip install pytest` | Unit/integration tests |
| python-dotenv | Environment variables | `pip install python-dotenv` | Load .env files |
| requests | HTTP client | `pip install requests` | API testing, calling APIs |
| Chart.js | JavaScript charting | CDN link | Frontend visualization |

---

## STUDY SCHEDULE SUGGESTION

**Week 1: Foundations (12 hours)**
- Day 1-2: Python, venv, pip (3 hours)
- Day 3-4: Snowflake and SQL (3 hours)
- Day 5: Database connectivity (2 hours)
- Day 6-7: Review and mini-projects (4 hours)

**Week 2: Data Processing (14 hours)**
- Day 1-3: pandas basics (5 hours)
- Day 4-5: Advanced pandas (4 hours)
- Day 6-7: Data validation and metrics formulas (5 hours)

**Week 3: Backend (12 hours)**
- Day 1-3: Flask basics (4 hours)
- Day 4-5: JWT authentication (3 hours)
- Day 6-7: REST API design and building (5 hours)

**Week 4: Frontend & Deployment (12 hours)**
- Day 1-3: HTML/CSS/JavaScript (5 hours)
- Day 4-5: Chart.js integration (3 hours)
- Day 6-7: Testing and deployment (4 hours)

**Total: ~50 hours of learning**

---

## Next Steps

1. Start with "Foundational Python Concepts" section
2. Work through all "Quick Exercise" code samples
3. Proceed to Phase 1 learning materials before starting Phase 1 implementation
4. Re-read concepts before implementing each phase

**Good luck with your learning journey!** 🚀
