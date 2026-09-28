# Data Quality & Metrics PoC - Complete Project Plan

## Executive Overview

This is a **Proof-of-Concept (PoC)** web application that:
- Connects to Snowflake to fetch Stock, Bonds, and Security Master datasets
- Validates data quality (5 checks per dataset type)
- Computes financial metrics using pandas (SMA, EMA, YTM, Duration, etc.)
- Serves a lightweight Django/Flask UI with dropdown selectors
- Implements token-based authorization
- Returns results as tables and charts

**Estimated Time to Build**: 40-60 hours (full stack, learning included)
**Tech Stack**: Python (Flask/Django), pandas, Snowflake, SQLAlchemy, JWT, Chart.js, HTML/CSS/JS

---

## PART 1: ARCHITECTURE & DESIGN

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (HTML/JS)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Dropdown A: Data Type (Stock/Bonds/Security Master)  │   │
│  │ Dropdown B: Metric/KPI (dynamic, based on type)      │   │
│  │ Execute Button → Call /api/execute                   │   │
│  │ Result: Table + Chart (Chart.js)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP (Bearer Token)
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (Flask/Django)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ API Endpoints:                                       │   │
│  │ • POST /api/login → Token                            │   │
│  │ • GET /api/metrics?datatype=X → Metric List          │   │
│  │ • POST /api/execute → Compute & Return Result        │   │
│  │ • GET /api/health → Health Check                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Middleware:                                          │   │
│  │ • Token Validation (JWT)                             │   │
│  │ • Error Handling                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Services (pandas-based):                             │   │
│  │ • Data Quality Checks (5 per dataset)                │   │
│  │ • Metric Calculations (SMA, EMA, YTM, etc.)         │   │
│  │ • Data Transformations                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ SQL
┌─────────────────────────────────────────────────────────────┐
│                    SNOWFLAKE DATABASE                        │
│  • STOCKS table (Date, Ticker, Open, High, Low, Close, Vol) │
│  • BONDS table (Date, Ticker, Series, Price, VWAP, Vol)     │
│  • SECURITY_MASTER table (SSM_ID, Name, ISIN, Issuer, etc)  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Project File Structure

```
poc-trial-2/
│
├── 00_PROJECT_PLAN.md              (this file)
├── 01_SETUP_GUIDE.md               (step-by-step setup)
├── 02_LEARNING_RESOURCES.md        (background reading)
├── 03_IMPLEMENTATION_ROADMAP.md   (phase breakdown)
│
├── .env.sample                     (example credentials)
├── requirements.txt                (Python dependencies)
├── pytest.ini                      (test configuration)
│
├── config/
│   ├── __init__.py
│   └── settings.py                 (Flask/Django config)
│
├── snowflake_connector/
│   ├── __init__.py
│   ├── connector.py               (Snowflake connection logic)
│   └── cache.py                   (simple query caching)
│
├── data_quality/
│   ├── __init__.py
│   ├── stock_quality.py           (5 stock quality checks)
│   ├── bonds_quality.py           (5 bond quality checks)
│   └── security_master_quality.py (5 SM quality checks)
│
├── metrics/
│   ├── __init__.py
│   ├── stock_metrics.py           (SMA, EMA, volatility, etc.)
│   ├── bonds_metrics.py           (YTM, Duration, DV01, etc.)
│   └── security_master_metrics.py (completeness, uniqueness, etc.)
│
├── backend/
│   ├── __init__.py
│   ├── app.py                     (Flask/Django app entry point)
│   ├── auth.py                    (JWT/token logic)
│   ├── routes.py                  (API endpoints)
│   └── middleware.py              (token validation middleware)
│
├── templates/
│   └── index.html                 (frontend UI)
│
├── static/
│   ├── js/
│   │   └── app.js                (frontend logic, Chart.js)
│   └── css/
│       └── style.css             (styling)
│
├── tests/
│   ├── __init__.py
│   ├── test_data_quality.py       (unit tests for quality checks)
│   ├── test_metrics.py            (unit tests for metrics)
│   ├── test_api.py                (integration tests for endpoints)
│   └── test_snowflake.py          (integration tests for DB connection)
│
└── README.md                       (quick start guide)
```

---

## PART 2: STEP-BY-STEP IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Hours 1-8)
**Goal**: Environment setup and Snowflake connectivity

**Learning Objectives**:
- Python virtual environments and package management
- Environment variable management and secrets
- Snowflake connection and authentication
- Basic SQL and data fetching

**Tasks**:
1. Initialize project directory and git repository
2. Set up Python virtual environment
3. Install dependencies (Flask, pandas, Snowflake connector, pytest, etc.)
4. Configure .env file with Snowflake credentials
5. Create Snowflake connector module (snowflake_connector/connector.py)
6. Write integration test to verify Snowflake connection
7. Document setup in README.md

**Deliverables**:
- ✅ Project directory structure
- ✅ requirements.txt with all dependencies
- ✅ .env.sample file (no real credentials)
- ✅ snowflake_connector module working
- ✅ One passing integration test

---

### Phase 2: Data Quality Checks (Hours 9-20)
**Goal**: Implement all 5 quality checks for each dataset

**Learning Objectives**:
- pandas DataFrame operations (filtering, validation, groupby)
- Error detection and logging
- Unit testing with pytest
- Data validation patterns

**Tasks**:

**Stock Data Quality (stock_quality.py)**:
1. Date validity check: parse dates, no future dates
2. Price sanity check: High >= Low, Open/Close in [Low, High]
3. Volume non-negative check
4. Duplicate detection: (Date, Ticker) pairs
5. Test with unit tests

**Bonds Data Quality (bonds_quality.py)**:
1. Maturity date vs Date: maturity >= date for historical
2. Numeric sanity: Volume, Value, Trades >= 0; VWAP in range
3. Unique trade key: no duplicates (Date, Ticker, Series)
4. Previous close vs current day comparison
5. Test with unit tests

**Security Master Data Quality (security_master_quality.py)**:
1. Numeric sanity: Price, Duration, Convexity are valid numbers
2. Duplicate detection: SSM_ID or (Name, ISIN) duplicates
3. Reference integrity checks
4. Completeness checks on critical columns
5. Test with unit tests

**Deliverables**:
- ✅ Three quality check modules (stock, bonds, SM)
- ✅ Each check is a testable function
- ✅ 15+ unit tests (3 checks × 5 datasets)
- ✅ Quality report generation (JSON/dict)

---

### Phase 3: Metric Calculations (Hours 21-35)
**Goal**: Implement all metrics with pandas

**Learning Objectives**:
- Time-series calculations (rolling windows, exponential smoothing)
- Financial formulas (returns, moving averages, yield)
- Numerical methods (Newton-Raphson for YTM)
- Caching and optimization

**Tasks**:

**Stock Metrics (stock_metrics.py)**:
1. Daily return: (Close_t / Close_{t-1}) - 1
2. Log return: ln(Close_t / Close_{t-1})
3. Simple Moving Average (SMA, param: n)
4. Exponential Moving Average (EMA, param: n)
5. Rolling volatility annualized (param: n)
6. VWAP (if intraday data available)
7. Dividend yield (if dividend data available)

**Bond Metrics (bonds_metrics.py)**:
1. Yield to Maturity (YTM) - numeric solve with Newton-Raphson
2. Duration (Macaulay)
3. Modified Duration
4. Term to Maturity in years
5. DV01 (price change per 1 bp move)
6. Helper: cash flow schedule generation

**Security Master Metrics (security_master_metrics.py)**:
1. Completeness % (1 - null_count / total)
2. Identifier uniqueness (% distinct SSM_ID)
3. Currency distribution (counts & percentages)
4. Average Price by Sector
5. Related Securities count

**Deliverables**:
- ✅ Three metric modules
- ✅ 15+ metric functions
- ✅ Parametrized metrics (SMA_n, EMA_n, rolling vol window)
- ✅ 20+ unit tests for metric functions

---

### Phase 4: Backend API (Hours 36-48)
**Goal**: Build Flask/Django API with authorization

**Learning Objectives**:
- Flask/Django routing and blueprints
- JWT token generation and validation
- Middleware and decorators
- RESTful API design
- Error handling and logging

**Tasks**:
1. Set up Flask/Django app (app.py)
2. Implement JWT auth module (auth.py)
3. Create token validation middleware
4. Implement POST /api/login endpoint
5. Implement GET /api/metrics?datatype=X endpoint
6. Implement POST /api/execute endpoint
7. Implement GET /api/health endpoint
8. Add error handling and logging
9. Write integration tests for all endpoints

**API Contracts**:

```
POST /api/login
Request: { "username": "user", "password": "pass" }
Response: { "status": "ok", "token": "eyJhbGciOiJIUzI1NiIs..." }

GET /api/metrics?datatype=stock
Response: {
  "status": "ok",
  "metrics": [
    { "id": "daily_return", "name": "Daily Return", "params": [] },
    { "id": "sma", "name": "Simple Moving Average", "params": ["n"] }
  ]
}

POST /api/execute
Request: {
  "datatype": "stock",
  "metric_id": "sma",
  "params": { "n": 20 },
  "filters": { "ticker": ["AAPL", "MSFT"], "date_range": ["2025-01-01", "2025-01-31"] }
}
Response: {
  "status": "ok",
  "columns": ["Date", "Ticker", "SMA_20"],
  "rows": [["2025-01-10", "AAPL", 150.25], ["2025-01-10", "MSFT", 310.50]],
  "chart": {
    "type": "line",
    "x": "Date",
    "series": [
      { "name": "AAPL", "values": [150.25, 150.30, ...] },
      { "name": "MSFT", "values": [310.50, 310.75, ...] }
    ]
  }
}

GET /api/health
Response: { "status": "ok", "timestamp": "2025-01-15T10:30:00Z" }
```

**Deliverables**:
- ✅ Flask/Django app with all endpoints
- ✅ JWT auth module
- ✅ Token validation middleware
- ✅ 10+ integration tests
- ✅ Error responses (400, 401, 500)

---

### Phase 5: Frontend UI (Hours 49-55)
**Goal**: Build lightweight HTML/JS frontend

**Learning Objectives**:
- HTML/CSS basics
- Vanilla JavaScript (fetch API)
- Chart.js integration
- UI/UX patterns

**Tasks**:
1. Create base HTML template (index.html)
2. Implement Dropdown A (Data Type selector)
3. Implement Dropdown B (Metric selector - dynamic)
4. Add Execute button with loading state
5. Display results table
6. Integrate Chart.js for visualization
7. Add token management (login screen)
8. Style with CSS (basic, responsive)

**Frontend Flow**:
```
1. User lands on page → Show login screen
2. Enter credentials → Click Login → Store token in localStorage
3. Show Data Type dropdown (Stock/Bonds/Security Master)
4. User selects data type → Fetch available metrics → Populate Metric dropdown
5. User selects metric + optional params → Click Execute
6. Send request with Bearer token
7. Display table + chart
```

**Deliverables**:
- ✅ index.html (login + main UI)
- ✅ app.js (fetch calls, dropdown logic, Chart.js)
- ✅ style.css (responsive design)
- ✅ localStorage token management

---

### Phase 6: Testing & Documentation (Hours 56-60)
**Goal**: Comprehensive tests and documentation

**Learning Objectives**:
- pytest fixtures and parametrization
- Integration testing strategies
- Documentation best practices
- Git workflow

**Tasks**:
1. Write comprehensive unit tests for all quality checks
2. Write comprehensive unit tests for all metrics
3. Write integration tests for API endpoints
4. Write end-to-end test scenarios
5. Document all functions and classes
6. Create RUNNING.md (how to start app)
7. Create TESTING.md (how to run tests)
8. Create API_DOCUMENTATION.md (endpoint specs)
9. Commit and push to git

**Test Coverage Target**: > 80%

**Deliverables**:
- ✅ 50+ unit tests
- ✅ 15+ integration tests
- ✅ README.md (quick start)
- ✅ TESTING.md (test guide)
- ✅ API_DOCUMENTATION.md
- ✅ Clean git history

---

## PART 3: LEARNING RESOURCES BY PHASE

### Phase 1: Snowflake & Connection
- Python virtual environments: https://docs.python.org/3/tutorial/venv.html
- Snowflake Python connector: https://docs.snowflake.com/en/user-guide/python-connector.html
- SQLAlchemy with Snowflake: https://docs.sqlalchemy.org/
- Environment variables: https://12factor.net/config

### Phase 2: pandas & Data Quality
- pandas getting started: https://pandas.pydata.org/getting_started/index.html
- Data validation patterns: Look at "Great Expectations" library (optional for advanced)
- Unit testing with pytest: https://docs.pytest.org/

### Phase 3: Metrics & Time Series
- Financial metrics formulas: Khan Academy, Investopedia
- pandas rolling operations: https://pandas.pydata.org/docs/user_guide/window.html
- Numerical methods (Newton-Raphson): Numerical Recipes book, scipy.optimize

### Phase 4: Backend & API
- Flask tutorial: https://flask.palletsprojects.com/
- Django REST framework: https://www.django-rest-framework.org/
- JWT in Python: https://pyjwt.readthedocs.io/
- RESTful API design: https://restfulapi.net/

### Phase 5: Frontend
- Chart.js: https://www.chartjs.org/
- Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- HTML/CSS/JavaScript: MDN Web Docs

### Phase 6: Testing & DevOps
- pytest advanced: https://docs.pytest.org/en/latest/how-to/
- Test doubles (mocks): unittest.mock docs
- Git workflow: https://git-scm.com/book/en/v2

---

## PART 4: KEY DESIGN PATTERNS

### 4.1 Data Quality Check Pattern

```python
# Example structure in stock_quality.py
def check_date_validity(df: pd.DataFrame) -> dict:
    """
    Returns: {
        'passed': bool,
        'total_records': int,
        'failed_count': int,
        'failed_samples': list of rows
    }
    """
    issues = []
    for idx, row in df.iterrows():
        # validation logic
        if issue:
            issues.append({'row': idx, 'value': row, 'reason': 'reason'})
    
    return {
        'passed': len(issues) == 0,
        'total_records': len(df),
        'failed_count': len(issues),
        'failed_samples': issues[:10]  # show first 10
    }
```

### 4.2 Metric Calculation Pattern

```python
# Example in stock_metrics.py
def calculate_sma(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    Params:
        df: DataFrame with Close column, sorted by date
        window: SMA window size
    Returns:
        Series with SMA values
    """
    return df['Close'].rolling(window=window).mean()
```

### 4.3 API Endpoint Pattern

```python
# Example in routes.py
@app.route('/api/execute', methods=['POST'])
@token_required  # middleware decorator
def execute_metric():
    data = request.get_json()
    datatype = data.get('datatype')  # validate
    metric_id = data.get('metric_id')  # validate
    
    # Fetch data from Snowflake
    # Apply quality checks
    # Calculate metric
    # Format response
    return jsonify({...})
```

### 4.4 Frontend Dropdown Pattern

```javascript
// Example in app.js
document.getElementById('dataTypeSelect').addEventListener('change', async (e) => {
    const dataType = e.target.value;
    const response = await fetch(`/api/metrics?datatype=${dataType}`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    const data = await response.json();
    // populate metricSelect dropdown
});
```

---

## PART 5: DEPENDENCY CHECKLIST

### Python Packages
- **Backend**: Flask==2.3.0, Flask-Cors==4.0.0, Flask-JWT-Extended==4.5.0
- **Data**: pandas==2.0.0, numpy==1.24.0
- **Database**: snowflake-connector-python==3.0.0, sqlalchemy==2.0.0
- **Testing**: pytest==7.3.0, pytest-cov==4.1.0, requests==2.31.0
- **Utilities**: python-dotenv==1.0.0, Werkzeug==2.3.0

### Frontend Libraries (CDN)
- Chart.js 4.x (via CDN)
- Bootstrap 5.x (optional, for quick styling)

### Development Tools
- Git
- Python 3.9+
- VS Code (or your IDE)

---

## PART 6: COMMON PITFALLS & SOLUTIONS

| Pitfall | Solution |
|---------|----------|
| Hardcoded Snowflake credentials | Use .env file + python-dotenv |
| Slow queries pulling huge datasets | Push filters into SQL (date range, ticker) |
| Timezone issues with dates | Use UTC; convert on display |
| Caching stale data in frontend | Add cache-busting headers; refresh on execute |
| Token expiration not handled | Refresh token logic; redirect to login on 401 |
| Pandas column name inconsistencies | Normalize: `.columns.str.lower().str.replace()` |
| NaN/null handling in metrics | Use `.fillna()` or `.dropna()` appropriately |
| YTM calculation not converging | Use bisection method; set max iterations |
| Chart doesn't display | Verify JSON structure matches Chart.js schema |
| CORS issues between frontend & backend | Add `@cross_origin()` or middleware |

---

## PART 7: SUCCESS CRITERIA

- [ ] Snowflake connection working (test passes)
- [ ] All 15 quality checks implemented & tested
- [ ] All 15 metrics implemented & tested
- [ ] All 4 API endpoints working with token auth
- [ ] Frontend loads, dropdowns work
- [ ] Chart renders correctly
- [ ] 50+ unit tests passing
- [ ] 15+ integration tests passing
- [ ] Documentation complete
- [ ] Code coverage > 80%

---

## Next Steps

1. **Read 01_SETUP_GUIDE.md** for step-by-step setup
2. **Read 02_LEARNING_RESOURCES.md** for background
3. **Read 03_IMPLEMENTATION_ROADMAP.md** for phase details
4. **Start Phase 1**: Environment setup

Estimated reading time: 2 hours
Estimated total build time: 40-60 hours
