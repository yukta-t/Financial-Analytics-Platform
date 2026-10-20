import json
import pandas as pd
from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import datetime
from flask import request, jsonify
from backend.auth import generate_token
from backend.auth import login_required
from backend.logger_config import setup_logger
from flask import render_template
from werkzeug.exceptions import HTTPException
from metrics.stock_metrics import (
    calculate_daily_return,
    calculate_log_return,
    calculate_sma,
    calculate_ema,
    calculate_volatility,
    calculate_vwap,
    calculate_dividend_yield
)


from metrics.bonds_metrics import (
    calculate_ytm,
    calculate_macaulay_duration,
    calculate_modified_duration,
    calculate_dv01,
    build_cashflow_schedule
)


from metrics.security_master_metrics import (
    calculate_completeness,
    calculate_uniqueness,
    get_currency_distribution,
    get_average_price_by_sector
)


from backend.services.snowflake_service import load_table
from backend.services.portfolio_service import (
    PortfolioInputError,
    get_available_tickers,
    simulate_portfolio
)
from data_quality.stock_checks import run_all_stock_checks
from data_quality.bonds_checks import run_all_bond_checks
from data_quality.security_master_checks import (
    calculate_completeness as calculate_security_master_completeness,
    check_identifier_uniqueness,
    run_all_security_master_checks
)

from backend.errors import (
    APIError,
    BadRequestError,
    UnauthorizedError,
    InternalServerError
)
import os
from dotenv import load_dotenv

load_dotenv()


print("ACCOUNT:", os.getenv("SNOW_ACCOUNT"))
print("DATABASE:", os.getenv("SNOW_DATABASE"))
print("SCHEMA:", os.getenv("SNOW_SCHEMA"))

METRICS = {
    "stock": [
        {"id":"daily_return","name":"Daily Return"},
        {"id":"log_return","name":"Log Return"},
        {"id":"sma","name":"Simple Moving Average"},
        {"id":"ema","name":"Exponential Moving Average"},
        {"id":"volatility","name":"Rolling Volatility"},
        {"id":"vwap","name":"VWAP"},
        {"id":"dividend_yield","name":"Dividend Yield"}
    ],

    "bonds": [
        {"id":"ytm","name":"Yield To Maturity"},
        {"id":"duration","name":"Macaulay Duration"},
        {"id":"modified_duration","name":"Modified Duration"},
        {"id":"dv01","name":"DV01"}
    ],

    "security_master": [
    {"id":"completeness","name":"Completeness"},
    {"id":"identifier_uniqueness","name":"Identifier Uniqueness"},
    {"id":"currency_distribution","name":"Currency Distribution"},
    {"id":"average_price_by_sector","name":"Average Price By Sector"}
]
}

STOCK_TIME_SERIES_METRICS = {
    "daily_return",
    "log_return",
    "sma",
    "ema",
    "volatility",
    "dividend_yield"
}


app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
logger = setup_logger()

app.config["JWT_SECRET_KEY"] = (
    "your-secret-key"
)

jwt = JWTManager(app)



@app.post("/api/login")
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    logger.info("Login attempt for username: %s", username)
    
    if (
        username == "admin"
        and password == "admin123"
    ):
        logger.info("Successful login for username: %s", username)

        token = generate_token(username)

        return jsonify({
    "status": "ok",
    "access_token": token
})

    logger.warning("Failed login attempt for username: %s", username)
    return jsonify({
    "status": "error",
    "message": "Invalid credentials"
}), 401



@jwt.expired_token_loader
def expired_token_callback(
    jwt_header,
    jwt_payload
):
    return jsonify({
    "status": "error",
    "message": "Token expired"
}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):

    return jsonify({
    "status": "error",
    "message": "Invalid token"
}), 401




@app.get("/api/health")
def health():

    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.get("/api/metrics")
@login_required
def metrics():

    datatype = request.args.get(
        "datatype"
    )

    logger.info(
    f"Metrics endpoint called. "
    f"datatype={datatype}"
)

    if datatype not in METRICS:

        raise BadRequestError(
            "Invalid datatype"
        )

    return jsonify({
        "status":"ok",
        "metrics": METRICS[datatype]
    })


@app.get("/api/quality")
@login_required
def quality():

    datatype = request.args.get("datatype")
    if datatype not in {
        "stock",
        "bonds",
        "security_master"
    }:
        raise BadRequestError("Invalid datatype")

    try:
        df = load_table(datatype)
        if df.empty:
            return jsonify({
                "status": "error",
                "message": "No data available for the selected dataset"
            }), 400

        if datatype == "stock":
            results = run_all_stock_checks(df)
            display_names = {
                "Duplicate Records": "Duplicate Detection"
            }
        elif datatype == "bonds":
            results = run_all_bond_checks(df)
            display_names = {
                "Maturity Date Validation": "Maturity Validation",
                "Bond Numeric Validation": "Numeric Validation",
                "Bond VWAP Validation": "VWAP Validation",
                "Duplicate Trade Check": "Unique Trade Validation",
                "Prev Close Consistency": "Previous Close Consistency"
            }
        else:
            results = run_all_security_master_checks(df)
            display_names = {
                "Security Master Numeric Ranges": "Numeric Validation",
                "Duplicate SSM_ID Check": "Duplicate SSM_ID",
                "Duplicate Name ISIN Check": "Duplicate Name/ISIN"
            }

        checks = [
            {
                "check_name": display_names.get(
                    result["check_name"],
                    result["check_name"]
                ),
                "status": result["status"],
                "offending_count": int(result["offending_count"]),
                "sample_rows": json.loads(
                    pd.DataFrame(result["sample_rows"]).to_json(
                        orient="records",
                        date_format="iso"
                    )
                )
            }
            for result in results
        ]

        if datatype == "security_master":
            completeness = calculate_security_master_completeness(df)
            completeness_columns = list(completeness)
            incomplete_rows = df.loc[
                df[completeness_columns].isna().any(axis=1)
            ]
            checks.append({
                "check_name": "Completeness",
                "status": (
                    "PASS"
                    if all(value == 100 for value in completeness.values())
                    else "FAIL"
                ),
                "offending_count": int(len(incomplete_rows)),
                "sample_rows": json.loads(
                    incomplete_rows.head(5).to_json(
                        orient="records",
                        date_format="iso"
                    )
                )
            })

            uniqueness = check_identifier_uniqueness(df)
            duplicate_identifier_rows = df.loc[
                df["ssm_id"].isna()
                | df.duplicated(subset=["ssm_id"], keep=False)
            ]
            checks.append({
                "check_name": uniqueness["metric_name"],
                "status": (
                    "PASS"
                    if uniqueness["uniqueness_percent"] == 100
                    else "FAIL"
                ),
                "offending_count": int(len(duplicate_identifier_rows)),
                "sample_rows": json.loads(
                    duplicate_identifier_rows.head(5).to_json(
                        orient="records",
                        date_format="iso"
                    )
                )
            })

        logger.info("Quality checks called | datatype=%s", datatype)
        return jsonify({
            "status": "ok",
            "checks": checks
        })
    except Exception as error:
        logger.exception(
            "Quality checks failed | datatype=%s",
            datatype
        )
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


@app.post("/api/execute")
@login_required
def execute():

    try:

        payload = request.get_json()

        datatype = payload["datatype"]
        metric_id = payload["metric_id"]
        params = payload.get(
            "params",
            {}
        )

        df = load_table(datatype)
        print("\nLOADED DATA:")
        print(df.head())
        print(df.shape)

        if datatype == "stock":

            if metric_id == "daily_return":

                result = calculate_daily_return(df)

            elif metric_id == "log_return":

                result = calculate_log_return(df)

            elif metric_id == "sma":

                window = params.get(
                    "window",
                    20
                )

                result = calculate_sma(
                    df,
                    window
                )

            elif metric_id == "ema":

                window = params.get(
                    "window",
                    20
                )

                result = calculate_ema(
                    df,
                    window
                )

            elif metric_id == "volatility":

                result = calculate_volatility(df)

            elif metric_id == "vwap":

                return jsonify({
                    "status":"ok",
                    "rows":[calculate_vwap(df)],
                    "columns":["vwap"]
                })

            elif metric_id == "dividend_yield":

                result = calculate_dividend_yield(df)
            
        

            else:

                return jsonify({
                    "status":"error",
                    "message":"Metric not found"
                }), 400

        elif datatype == "bonds":

            if metric_id == "ytm":

                result = df.copy()

                result["ytm"] = result.apply(
                    lambda row: calculate_ytm(
                        row["face_value"],
                        row["coupon_rate"],
                        row["price"],
                        int(row["years_to_maturity"])
                    ),
                    axis=1
                )

            elif metric_id == "duration":

                result = df.copy()

                def get_duration(row):
                
                    ytm = calculate_ytm(
                        row["face_value"],
                        row["coupon_rate"],
                        row["price"],
                        int(row["years_to_maturity"])
                    )

                    cashflows = build_cashflow_schedule(
                        row["face_value"],
                        row["coupon_rate"],
                        int(row["years_to_maturity"])
                    )

                    return calculate_macaulay_duration(
                        cashflows,
                        ytm,
                        row["price"]
                    )

                result["duration"] = result.apply(
                    get_duration,
                    axis=1
                )

            elif metric_id == "modified_duration":

                result = df.copy()

                def get_modified_duration(row):

                    ytm = calculate_ytm(
                        row["face_value"],
                        row["coupon_rate"],
                        row["price"],
                        int(row["years_to_maturity"])
                    )

                    cashflows = build_cashflow_schedule(
                        row["face_value"],
                        row["coupon_rate"],
                        int(row["years_to_maturity"])
                    )

                    duration = calculate_macaulay_duration(
                        cashflows,
                        ytm,
                        row["price"]
                    )

                    return calculate_modified_duration(
                        duration,
                        ytm
                    )
                result["modified_duration"] = result.apply(
                    get_modified_duration,
                    axis=1
                )

            elif metric_id == "dv01":

                result = df.copy()

                def get_dv01(row):
                
                    ytm = calculate_ytm(
                        row["face_value"],
                        row["coupon_rate"],
                        row["price"],
                        int(row["years_to_maturity"])
                    )

                    cashflows = build_cashflow_schedule(
                        row["face_value"],
                        row["coupon_rate"],
                        int(row["years_to_maturity"])
                    )

                    duration = calculate_macaulay_duration(
                        cashflows,
                        ytm,
                        row["price"]
                    )

                    return calculate_dv01(
                        duration,
                        row["price"]
                    )

                result["dv01"] = result.apply(
                    get_dv01,
                    axis=1
                )

           


        elif datatype == "security_master":
            if metric_id == "completeness":
                    
                critical_columns = [
                    "isin",
                    "ssm_id",
                    "issuer_country"
                ]
    
                completeness = calculate_completeness(
                    df,
                    critical_columns
                )
    
                result = pd.DataFrame(
                    list(completeness.items()),
                    columns=[
                        "column",
                        "completeness_percent"
                    ]
                )   

            elif metric_id == "identifier_uniqueness":

                uniqueness = calculate_uniqueness(
                    df,
                    "ssm_id"
                )
                
                result = pd.DataFrame(
                    [uniqueness]
                )   

            elif metric_id == "currency_distribution":
                result = get_currency_distribution(df)


            elif metric_id == "average_price_by_sector":

                result = get_average_price_by_sector(df)

        logger.info(
            f"Execute called | "
            f"datatype={datatype} | "
            f"metric={metric_id}"
        )

        rows = result.fillna("").values.tolist()

        columns = result.columns.tolist()



        chart = {}
        if (
            datatype == "stock"
            and metric_id in STOCK_TIME_SERIES_METRICS
            and {"date", "ticker", metric_id}.issubset(result.columns)
        ):
            chart_data = result.loc[:, ["date", "ticker", metric_id]].dropna(
                subset=["date", "ticker"]
            )
            unique_dates = (
                chart_data["date"]
                .drop_duplicates()
                .sort_values(kind="stable")
            )
            labels = [str(date) for date in unique_dates]
            chart_data = chart_data.sort_values(
                ["ticker", "date"],
                kind="stable"
            )

            datasets = []
            for ticker, ticker_data in chart_data.groupby("ticker", sort=True):
                values_by_date = {
                    str(date): None if pd.isna(value) else float(value)
                    for date, value in ticker_data[
                        ["date", metric_id]
                    ].itertuples(index=False, name=None)
                }
                datasets.append({
                    "label": str(ticker),
                    "data": [
                        values_by_date.get(label)
                        for label in labels
                    ]
                })

            chart = {
                "type": "line",
                "labels": labels,
                "datasets": datasets
            }
        elif "date" in result.columns:
            chart = {
                "labels": (
                    result["date"]
                    .astype(str)
                    .tolist()
                ),
                "values": (
                    result.iloc[:, -1]
                    .fillna(0)
                    .tolist()
                )
            }

            
        return jsonify({
            "status":"ok",
            "columns":columns,
            "rows":rows,
            "chart": chart

        })

    except KeyError as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        }), 500



@app.get("/api/portfolio/securities")
@login_required
def portfolio_securities():

    try:
        tickers = get_available_tickers(load_table("stock"))
    except Exception as error:
        logger.exception("Failed to load portfolio securities")
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500

    return jsonify({
        "status": "ok",
        "securities": tickers
    })


@app.post("/api/portfolio/simulate")
@login_required
def portfolio_simulate():

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise BadRequestError("Request body must be a JSON object")

    try:
        result = simulate_portfolio(
            load_table("stock"),
            payload.get("holdings")
        )
    except PortfolioInputError as error:
        raise BadRequestError(str(error))
    except Exception as error:
        logger.exception("Portfolio simulation failed")
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500

    return jsonify({
        "status": "ok",
        **result
    })


@app.errorhandler(APIError)
def handle_api_error(error):

    return jsonify({
        "status": "error",
        "message": error.message
    }), error.status_code


@app.errorhandler(HTTPException)
def handle_http_exception(error):

    return jsonify({
        "status": "error",
        "message": error.description
    }), error.code







@app.get("/")
def home():

    return render_template("index.html")


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )



