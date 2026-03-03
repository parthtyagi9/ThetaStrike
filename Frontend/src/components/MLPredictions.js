import React, { useState } from "react";

function MLPredictions() {
  const [form, setForm] = useState({
    ticker: "NVDA",
    expiry: "2026-01-30",
    strike: 200,
    option_type: "call",
    model: "european",
    predict_date: "",
  });

  const [ivResult, setIvResult] = useState(null);
  const [moneynessResult, setMoneynessResult] = useState(null);
  const [training, setTraining] = useState(false);
  const [trainStatus, setTrainStatus] = useState(null);
  const [loading, setLoading] = useState({ iv: false, moneyness: false });
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const trainModels = async () => {
    setTraining(true);
    setTrainStatus(null);
    setError(null);
    try {
      const [ivRes, mRes] = await Promise.all([
        fetch(`http://127.0.0.1:8000/ml/train-iv?ticker=${form.ticker}`),
        fetch(`http://127.0.0.1:8000/ml/train-moneyness?ticker=${form.ticker}`),
      ]);
      const ivData = await ivRes.json();
      const mData = await mRes.json();

      if (!ivRes.ok || !mRes.ok) {
        setError(ivData.detail || mData.detail || "Training failed");
        setTraining(false);
        return;
      }

      setTrainStatus({
        iv: ivData.metrics,
        moneyness: mData.metrics,
      });
    } catch (err) {
      setError("Failed to connect to backend for training");
    }
    setTraining(false);
  };

  const predictIV = async () => {
    setLoading({ ...loading, iv: true });
    setError(null);
    const params = new URLSearchParams({
      ticker: form.ticker,
      strike: form.strike,
      expiry: form.expiry,
      option_type: form.option_type,
      model: form.model,
      predict_date: form.predict_date,
    }).toString();
    try {
      const res = await fetch(`http://127.0.0.1:8000/ml/predict-iv?${params}`);
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "IV prediction failed");
        setIvResult(null);
      } else {
        setIvResult(data);
      }
    } catch (err) {
      setError("Failed to connect to backend");
      setIvResult(null);
    }
    setLoading({ ...loading, iv: false });
  };

  const predictMoneyness = async () => {
    setLoading({ ...loading, moneyness: true });
    setError(null);
    const params = new URLSearchParams({
      ticker: form.ticker,
      strike: form.strike,
      expiry: form.expiry,
      option_type: form.option_type,
    }).toString();
    try {
      const res = await fetch(`http://127.0.0.1:8000/ml/predict-moneyness?${params}`);
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Moneyness prediction failed");
        setMoneynessResult(null);
      } else {
        setMoneynessResult(data);
      }
    } catch (err) {
      setError("Failed to connect to backend");
      setMoneynessResult(null);
    }
    setLoading({ ...loading, moneyness: false });
  };

  // Helper to render probability bar
  const renderProbBar = (label, prob) => {
    const pct = (prob * 100).toFixed(1);
    const color =
      label === "ITM" ? "#22c55e" : label === "OTM" ? "#ef4444" : "#f59e0b";
    return React.createElement("div", { className: "prob-bar-row", key: label }, [
      React.createElement("span", { className: "prob-label", key: "l" }, label),
      React.createElement(
        "div",
        { className: "prob-bar-bg", key: "bg" },
        React.createElement("div", {
          className: "prob-bar-fill",
          style: { width: pct + "%", backgroundColor: color },
          key: "fill",
        })
      ),
      React.createElement("span", { className: "prob-pct", key: "p" }, pct + "%"),
    ]);
  };

  return React.createElement("div", { className: "ml-predictions" }, [
    // Input Section
    React.createElement("div", { className: "ml-inputs-section", key: "inputs" }, [
      React.createElement("h2", { key: "title" }, "ML Model Inputs"),

      React.createElement("div", { className: "ml-form-grid", key: "form" }, [
        React.createElement("label", { key: "ticker" }, [
          "Ticker Symbol",
          React.createElement("input", {
            type: "text", name: "ticker", value: form.ticker, onChange: handleChange,
          }),
        ]),
        React.createElement("label", { key: "strike" }, [
          "Strike Price",
          React.createElement("input", {
            type: "number", name: "strike", value: form.strike, onChange: handleChange,
          }),
        ]),
        React.createElement("label", { key: "expiry" }, [
          "Expiry Date",
          React.createElement("input", {
            type: "text", name: "expiry", value: form.expiry, onChange: handleChange,
            placeholder: "YYYY-MM-DD",
          }),
        ]),
        React.createElement("label", { key: "option_type" }, [
          "Option Type",
          React.createElement("select", {
            name: "option_type", value: form.option_type, onChange: handleChange,
          }, [
            React.createElement("option", { value: "call", key: "c" }, "Call"),
            React.createElement("option", { value: "put", key: "p" }, "Put"),
          ]),
        ]),
        React.createElement("label", { key: "model" }, [
          "Pricing Model",
          React.createElement("select", {
            name: "model", value: form.model, onChange: handleChange,
          }, [
            React.createElement("option", { value: "european", key: "e" }, "European (Black-Scholes)"),
            React.createElement("option", { value: "american", key: "a" }, "American (Binomial)"),
          ]),
        ]),
        React.createElement("label", { key: "predict_date" }, [
          "Predict Date (Optional)",
          React.createElement("input", {
            type: "text", name: "predict_date", value: form.predict_date,
            onChange: handleChange, placeholder: "YYYY-MM-DD",
          }),
        ]),
      ]),

      // Train button
      React.createElement("div", { className: "ml-actions", key: "actions" }, [
        React.createElement(
          "button",
          {
            className: "btn btn-train",
            onClick: trainModels,
            disabled: training,
            key: "train",
          },
          training ? "Training Models..." : "Train Models on " + form.ticker
        ),
        React.createElement(
          "button",
          {
            className: "btn btn-predict",
            onClick: predictIV,
            disabled: loading.iv,
            key: "pred-iv",
          },
          loading.iv ? "Predicting..." : "Predict IV & Price"
        ),
        React.createElement(
          "button",
          {
            className: "btn btn-classify",
            onClick: predictMoneyness,
            disabled: loading.moneyness,
            key: "pred-m",
          },
          loading.moneyness ? "Classifying..." : "Predict Moneyness"
        ),
      ]),
    ]),

    // Error
    error
      ? React.createElement("div", { className: "ml-error", key: "error" }, error)
      : null,

    // Training Results
    trainStatus
      ? React.createElement("div", { className: "ml-train-results", key: "train" }, [
          React.createElement("h2", { key: "t" }, "Training Results"),
          React.createElement("div", { className: "train-cards", key: "cards" }, [
            React.createElement("div", { className: "train-card", key: "iv-card" }, [
              React.createElement("h3", { key: "h" }, "Ridge Regression (IV Predictor)"),
              React.createElement("table", { className: "results-table", key: "tbl" },
                React.createElement("tbody", null, [
                  React.createElement("tr", { key: "s" }, [
                    React.createElement("td", null, "Training Samples"),
                    React.createElement("td", null, trainStatus.iv.samples),
                  ]),
                  React.createElement("tr", { key: "f" }, [
                    React.createElement("td", null, "Features Used"),
                    React.createElement("td", null, trainStatus.iv.features_used),
                  ]),
                  React.createElement("tr", { key: "r2" }, [
                    React.createElement("td", null, "Train R²"),
                    React.createElement("td", null, trainStatus.iv.train_r2.toFixed(4)),
                  ]),
                  React.createElement("tr", { key: "cv" }, [
                    React.createElement("td", null, "Cross-Val R² (mean ± std)"),
                    React.createElement("td", null,
                      trainStatus.iv.cv_r2_mean.toFixed(4) + " ± " + trainStatus.iv.cv_r2_std.toFixed(4)
                    ),
                  ]),
                ])
              ),
            ]),
            React.createElement("div", { className: "train-card", key: "m-card" }, [
              React.createElement("h3", { key: "h" }, "Random Forest (Moneyness Classifier)"),
              React.createElement("table", { className: "results-table", key: "tbl" },
                React.createElement("tbody", null, [
                  React.createElement("tr", { key: "s" }, [
                    React.createElement("td", null, "Training Samples"),
                    React.createElement("td", null, trainStatus.moneyness.samples),
                  ]),
                  React.createElement("tr", { key: "f" }, [
                    React.createElement("td", null, "Features Used"),
                    React.createElement("td", null, trainStatus.moneyness.features_used),
                  ]),
                  React.createElement("tr", { key: "a" }, [
                    React.createElement("td", null, "Train Accuracy"),
                    React.createElement("td", null, (trainStatus.moneyness.train_accuracy * 100).toFixed(1) + "%"),
                  ]),
                  React.createElement("tr", { key: "cv" }, [
                    React.createElement("td", null, "Cross-Val Accuracy (mean ± std)"),
                    React.createElement("td", null,
                      (trainStatus.moneyness.cv_accuracy_mean * 100).toFixed(1) + "% ± " +
                      (trainStatus.moneyness.cv_accuracy_std * 100).toFixed(1) + "%"
                    ),
                  ]),
                  React.createElement("tr", { key: "d" }, [
                    React.createElement("td", null, "Class Distribution"),
                    React.createElement("td", null,
                      Object.entries(trainStatus.moneyness.class_distribution)
                        .map(([k, v]) => k + ": " + v)
                        .join(", ")
                    ),
                  ]),
                ])
              ),
            ]),
          ]),
        ])
      : null,

    // Results Section
    React.createElement("div", { className: "ml-results-grid", key: "results" }, [
      // IV Prediction Results
      React.createElement("div", { className: "ml-result-card", key: "iv" }, [
        React.createElement("h2", { key: "h" }, "IV Prediction (Ridge Regression)"),
        ivResult
          ? React.createElement("div", { key: "content" }, [
              React.createElement("table", { className: "results-table", key: "tbl" },
                React.createElement("tbody", null, [
                  React.createElement("tr", { key: "spot" }, [
                    React.createElement("td", null, "Spot Price"),
                    React.createElement("td", null, "$" + ivResult.spot_price.toFixed(2)),
                  ]),
                  React.createElement("tr", { key: "mliv" }, [
                    React.createElement("td", null, "ML Predicted IV"),
                    React.createElement("td", { className: "highlight-value" }, (ivResult.ml_predicted_iv * 100).toFixed(2) + "%"),
                  ]),
                  React.createElement("tr", { key: "mktiv" }, [
                    React.createElement("td", null, "Market IV"),
                    React.createElement("td", null,
                      ivResult.market_iv ? (ivResult.market_iv * 100).toFixed(2) + "%" : "N/A"
                    ),
                  ]),
                  React.createElement("tr", { key: "prem" }, [
                    React.createElement("td", null, "ML-Based Premium"),
                    React.createElement("td", { className: "highlight-value" }, "$" + ivResult.ml_premium.toFixed(2)),
                  ]),
                  React.createElement("tr", { key: "mon" }, [
                    React.createElement("td", null, "Moneyness (S/K)"),
                    React.createElement("td", null, ivResult.moneyness.toFixed(4)),
                  ]),
                  React.createElement("tr", { key: "tte" }, [
                    React.createElement("td", null, "Time to Expiry (yrs)"),
                    React.createElement("td", null, ivResult.tte.toFixed(4)),
                  ]),
                  React.createElement("tr", { key: "model" }, [
                    React.createElement("td", null, "Pricing Model"),
                    React.createElement("td", null, ivResult.model),
                  ]),
                ])
              ),
            ])
          : React.createElement("p", { className: "placeholder-text", key: "ph" },
              "Train models first, then click \"Predict IV & Price\""
            ),
      ]),

      // Moneyness Prediction Results
      React.createElement("div", { className: "ml-result-card", key: "moneyness" }, [
        React.createElement("h2", { key: "h" }, "Moneyness (Random Forest)"),
        moneynessResult
          ? React.createElement("div", { key: "content" }, [
              React.createElement("div", {
                className: "moneyness-badge " + moneynessResult.prediction.toLowerCase(),
                key: "badge",
              }, moneynessResult.prediction),
              React.createElement("div", { className: "prob-bars", key: "bars" },
                ["ITM", "ATM", "OTM"].map((label) =>
                  moneynessResult.probabilities[label] !== undefined
                    ? renderProbBar(label, moneynessResult.probabilities[label])
                    : null
                )
              ),
              React.createElement("table", { className: "results-table", key: "tbl" },
                React.createElement("tbody", null, [
                  React.createElement("tr", { key: "spot" }, [
                    React.createElement("td", null, "Spot Price"),
                    React.createElement("td", null, "$" + moneynessResult.spot_price.toFixed(2)),
                  ]),
                  React.createElement("tr", { key: "mon" }, [
                    React.createElement("td", null, "Moneyness (S/K)"),
                    React.createElement("td", null, moneynessResult.moneyness.toFixed(4)),
                  ]),
                  React.createElement("tr", { key: "iv" }, [
                    React.createElement("td", null, "IV Used"),
                    React.createElement("td", null, (moneynessResult.iv_used * 100).toFixed(2) + "%"),
                  ]),
                  React.createElement("tr", { key: "tte" }, [
                    React.createElement("td", null, "Time to Expiry (yrs)"),
                    React.createElement("td", null, moneynessResult.tte.toFixed(4)),
                  ]),
                ])
              ),
            ])
          : React.createElement("p", { className: "placeholder-text", key: "ph" },
              "Train models first, then click \"Predict Moneyness\""
            ),
      ]),
    ]),
  ]);
}

export default MLPredictions;
