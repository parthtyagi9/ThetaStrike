import math
from dataclasses import dataclass
from typing import Literal

@dataclass
class OptionParamsBinomial:
    S: float; K: float; T: float; r: float; sigma: float; steps: int
    option_type: Literal["call","put"]

def american_binomial(p: OptionParamsBinomial) -> float:
    dt = p.T/p.steps
    u = math.exp(p.sigma*math.sqrt(dt)); d = 1/u
    disc = math.exp(-p.r*dt)
    q = (math.exp(p.r*dt)-d)/(u-d)

    # terminal payoffs
    prices = [p.S*(u**j)*(d**(p.steps-j)) for j in range(p.steps+1)]
    vals = [max(0, (s-p.K) if p.option_type=="call" else (p.K-s)) for s in prices]

    # roll back
    for i in range(p.steps-1,-1,-1):
        for j in range(i+1):
            cont = disc*(q*vals[j+1] + (1-q)*vals[j])
            prices[j] = prices[j]/u
            exer = max(0, (prices[j]-p.K) if p.option_type=="call" else (p.K-prices[j]))
            vals[j] = max(cont, exer)
    return vals[0]
