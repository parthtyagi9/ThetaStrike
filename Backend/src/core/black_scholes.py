import math
from dataclasses import dataclass
from typing import Literal
from scipy.stats import norm


@dataclass
class BlackScholes:
    """
    Estimate prices of European options using the Black–Scholes model.

    Attributes:
        S (float): Spot price today
        K (float): Strike price
        T (float): Time to maturity in years
        R (float): Risk-free rate
        sigma (float): Volatility
        option_type (str): "call" or "put"
    """
    S: float
    K: float
    R: float
    sigma: float
    T: float
    option_type: Literal["call", "put"] = "call"

    def calculate_option_price(self, S: float = None, T: float = None) -> float:
        """
        Black–Scholes price for current parameters.
        Optional overrides:
            S: spot price to use instead of self.S
            T: time to maturity to use instead of self.T
        """
        S = self.S if S is None else S
        T = self.T if T is None else T

        if T <= 0:
            # At or past expiry, intrinsic value
            return max(S - self.K, 0.0) if self.option_type == "call" else max(self.K - S, 0.0)

        d1 = (math.log(S / self.K) + (self.R + 0.5 * self.sigma ** 2) * T) / (self.sigma * math.sqrt(T))
        d2 = d1 - self.sigma * math.sqrt(T)

        if self.option_type == "call":
            return S * norm.cdf(d1) - self.K * math.exp(-self.R * T) * norm.cdf(d2)
        elif self.option_type == "put":
            return self.K * math.exp(-self.R * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    def option_value_at_future(self, S_future: float, T_remaining: float) -> float:
        """
        Calculate option premium at a future time given predicted stock price
        and time left until expiry.
        """
        if T_remaining <= 0:
            return max(S_future - self.K, 0.0) if self.option_type == "call" else max(self.K - S_future, 0.0)

        return self.calculate_option_price(S=S_future, T=T_remaining)
