import numpy as np
import pandas as pd 


def calculate_ytm( 
    face_value,             # money youll eventually receive at maturity
    coupon_rate,            # (annual) percentage as a decimal (e.g., 0.08 for 8%)   
    price,                  # price u buy it for / current mkt price 
    years_to_maturity,       # years until the bond matures
    tolerance=1e-6,            # ie 0.000001 algo stops when it becomes accurate 
    max_iterations=100          # to avoid infinite loops 
):
    """
    Returns annual YTM as decimal.
    Example:
    0.08 = 8%
    """

    coupon = face_value * coupon_rate      # eg current price= 1000 and coupon rate= 0.08 then coupon= 1000*0.08 = 80 /// amount paid annually 

    ytm = coupon_rate

    for _ in range(max_iterations):     # iterate until it finds correct YTM

        pv = 0      # present value: will store calculated bond price 
        derivative = 0  # how sensitive price is to YTM 

        for t in range(1, years_to_maturity + 1):

            pv += coupon / ((1 + ytm) ** t)     # PV of the coupon

            derivative += (
                -t *
                coupon /
                ((1 + ytm) ** (t + 1))
            )

        pv += (
            face_value /
            ((1 + ytm) ** years_to_maturity)
        )

        derivative += (
            -years_to_maturity *
            face_value /
            ((1 + ytm) ** (years_to_maturity + 1))
        )

        error = pv - price

        if abs(error) < tolerance:
            return ytm

        ytm = ytm - (error / derivative)

    return None


def calculate_macaulay_duration(
    cf_schedule,
    ytm,
    price
):

    duration = 0

    for t, cf in enumerate(
        cf_schedule,
        start=1
    ):

        pv_cf = cf / ((1 + ytm) ** t)

        duration += t * pv_cf

    return duration / price



def calculate_modified_duration(
    macaulay_duration,
    ytm
):

    return (
        macaulay_duration
        / (1 + ytm)
    )



def calculate_dv01(
    duration,
    price
):

    return (
        -duration
        * price
        / 10000
    )



def build_cashflow_schedule(
    face_value,
    coupon_rate,
    years_to_maturity
):

    coupon = face_value * coupon_rate

    cashflows = [
        coupon
    ] * years_to_maturity

    cashflows[-1] += face_value

    return cashflows