import math
from dataclasses import dataclass
from typing import Literal

@dataclass
class OptionParamsBinomial:
    S: float
    K: float
    T: float
    r: float
    sigma: float
    steps: int
    option_type: Literal["call", "put"]
    q: float

def american_binomial(p: OptionParamsBinomial) -> float:
    if p.T <= 0:
        return max(p.S - p.K, 0.0) if p.option_type == "call" else max(p.K - p.S, 0.0)

    dt = p.T / p.steps
    u = math.exp(p.sigma * math.sqrt(dt))
    d = 1 / u
    disc = math.exp(-p.r * dt)
    q_prob = (math.exp((p.r - p.q) * dt) - d) / (u - d)


    vals = [
        max(0.0, (p.S * (u ** j) * (d ** (p.steps - j)) - p.K)) if p.option_type == "call"
        else max(0.0, (p.K - p.S * (u ** j) * (d ** (p.steps - j))))
        for j in range(p.steps + 1)
    ]

    # backward induction
    for i in range(p.steps - 1, -1, -1):
        new_vals = []
        for j in range(i + 1):
            cont = disc * (q_prob * vals[j + 1] + (1 - q_prob) * vals[j])
            S_ij = p.S * (u ** j) * (d ** (i - j))
            exer = (
                max(0.0, S_ij - p.K) if p.option_type == "call"
                else max(0.0, p.K - S_ij)
            )
            new_vals.append(max(cont, exer))
        vals = new_vals

    return vals[0]
