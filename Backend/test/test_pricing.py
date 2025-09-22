import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.black_scholes import BlackScholes
from src.core.binomial import OptionParamsBinomial, american_binomial
from src.pricing_engine.evaluate import EvaluationParams, evaluate_option_price


def test_black_scholes():
    bs = BlackScholes(S=100, K=100, R=0.05, sigma=0.2, T=1, option_type="call")
    price = bs.calculate_option_price()
    print("European Call (BS):", price)

    bs_put = BlackScholes(S=100, K=100, R=0.05, sigma=0.2, T=1, option_type="put")
    price_put = bs_put.calculate_option_price()
    print("European Put (BS):", price_put)


def test_binomial():
    params = OptionParamsBinomial(S=100, K=100, T=1, r=0.05, sigma=0.2, steps=200, option_type="put")
    price = american_binomial(params)
    print("American Put (Binomial):", price)


def test_evaluate():
    euro_params = EvaluationParams(
        model="european",
        option_type="call",
        S_future=120,
        K=100,
        T_total=1.0,
        t_elapsed=0.25,
        r=0.05,
        sigma=0.2
    )
    print("Eval European Call:", evaluate_option_price(euro_params))

    amer_params = EvaluationParams(
        model="american",
        option_type="put",
        S_future=120,
        K=100,
        T_total=1.0,
        t_elapsed=0.25,
        r=0.05,
        sigma=0.2,
        steps=300
    )
    print("Eval American Put:", evaluate_option_price(amer_params))


if __name__ == "__main__":
    test_black_scholes()
    test_binomial()
    test_evaluate()
