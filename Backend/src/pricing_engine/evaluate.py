import math
from dataclasses import dataclass
from typing import Literal

from src.core.black_scholes import BlackScholes
from src.core.binomial import OptionParamsBinomial, american_binomial


@dataclass
class EvaluationParams:
    model: Literal["european", "american"]
    option_type: Literal["call", "put"]
    S_future: float   # predicted stock price at evaluation date
    K: float          # strike price
    T_total: float    # total maturity (years)
    t_elapsed: float  # time elapsed until evaluation date (years)
    r: float          # risk-free rate
    sigma: float      # volatility
    steps: int = 1000  # binomial steps for American


def evaluate_option_price(params: EvaluationParams) -> float:
    """
    Evaluate option price at a given future date using European (Black-Scholes)
    or American (Binomial) model, based on predicted future stock price.

    Args:
        params (EvaluationParams): all inputs for pricing.

    Returns:
        float: option price at the evaluation date.
    """

    T_remaining = params.T_total - params.t_elapsed
    if T_remaining <= 0:
        if params.option_type == "call":
            return max(params.S_future - params.K, 0.0)
        else:
            return max(params.K - params.S_future, 0.0)

    if params.model == "european":
        bs = BlackScholes(
            S=params.S_future,
            K=params.K,
            R=params.r,
            sigma=params.sigma,
            T=T_remaining,
            option_type=params.option_type,
        )
        return bs.calculate_option_price()

    elif params.model == "american":
        opt = OptionParamsBinomial(
            S=params.S_future,
            K=params.K,
            T=T_remaining,
            r=params.r,
            sigma=params.sigma,
            steps=params.steps,
            option_type=params.option_type
        )
        return american_binomial(opt)

    else:
        raise ValueError("model must be 'european' or 'american'")
