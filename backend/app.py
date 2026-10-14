from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import datetime
from flask import request, jsonify
from backend.auth import generate_token
from backend.auth import login_required
from backend.logger_config import setup_logger
from metrics.stock_metrics import (
    calculate_daily_return,
    calculate_log_return,
    calculate_sma,
    calculate_ema,
    calculate_volatility,
    calculate_vwap,
    calculate_dividend_yield
)

from backend.services.snowflake_service import load_table

from backend.errors import (
    APIError,
    BadRequestError,
    UnauthorizedError,
    InternalServerError
)

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
        {"id":"identifier_uniqueness","name":"Identifier Uniqueness"}
    ]
}


app = Flask(__name__)
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




        logger.info(
            f"Execute called | "
            f"datatype={datatype} | "
            f"metric={metric_id}"
        )

        rows = result.fillna("").values.tolist()

        columns = result.columns.tolist()

        return jsonify({
            "status":"ok",
            "columns":columns,
            "rows":rows,
            "chart":{}
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



@app.errorhandler(APIError)
def handle_api_error(error):

    return jsonify({
        "status": "error",
        "message": error.message
    }), error.status_code


@app.errorhandler(Exception)
def handle_unexpected_error(error):

    logger.exception(
        "Unhandled exception occurred"
    )

    return jsonify({
        "status":"error",
        "message":"Internal server error"
    }), 500



if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )






