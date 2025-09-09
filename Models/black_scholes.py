import math
from scipy.stats import norm


class black_scholes:
    """
    An estiimstor to estimate prices of European options for a given price S at maturity T.

    Attributes:
        S: Price at Maturity
        K: Strike Price
        T: Time to maturity in years
        R: Risk free rate of Interest
        sigma: Volatility
        option_type: "call" or "put"
    """
    S: float
    K: float
    T: float
    R: float
    sigma: float
    option_type: str

    def __init__(self, S, K, R, sigma, T, option_type="call"):
        self.S = S
        self.K = K
        self.R = R
        self.sigma = sigma
        self.T = T
        self.option_type = option_type.lower()

    def calculate_option_price(self) -> float:
        d1 = (math.log(self.S/self.K) + (self.R + (self.sigma ** 2) / 2) * self.T) / (self.sigma * self.T**(0.5))
        d2 = d1 - (self.sigma * self.T**(0.5))
        if self.option_type == "call":
            return self.S * norm.cdf(d1) - self.K * math.exp(-self.R * self.T) * norm.cdf(d2)
        elif self.option_type == "put":
            return self.K * math.exp(-self.R * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
