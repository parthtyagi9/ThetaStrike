import math
from scipy.stats import norm


class black_scholes:
    """
    An estimator to estimate prices of European options.

    Attributes:
        S: Spot price today
        K: Strike price
        T: Time to maturity in years
        R: Risk-free rate
        sigma: Volatility
        option_type: "call" or "put"
    """
    S: float; K: float; T: float; R: float; sigma: float; option_type: str

    def __init__(self, S, K, R, sigma, T, option_type="call"):
        self.S = S
        self.K = K
        self.R = R
        self.sigma = sigma
        self.T = T
        self.option_type = option_type.lower()

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
            # At or past expiry, use intrinsic value
            if self.option_type == "call":
                return max(S - self.K, 0.0)
            elif self.option_type == "put":
                return max(self.K - S, 0.0)
            else:
                raise ValueError("option_type must be 'call' or 'put'")

        d1 = (math.log(S / self.K) + (self.R + (self.sigma ** 2) / 2) * T) / (self.sigma * math.sqrt(T))
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
        if T_remaining <= 0:  # at (or past) maturity
            if self.option_type == "call":
                return max(S_future - self.K, 0.0)
            elif self.option_type == "put":
                return max(self.K - S_future, 0.0)
            else:
                raise ValueError("option_type must be 'call' or 'put'")
        else:
            # Reuse the core BS pricer with overrides
            return self.calculate_option_price(S=S_future, T=T_remaining)
