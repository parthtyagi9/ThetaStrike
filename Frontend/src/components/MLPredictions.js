import React, { useState } from "react";
import TickerSearch from "./TickerSearch";

const API = "http://127.0.0.1:8000";
const h = React.createElement;

function MLPredictions() {
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    ticker: "NVDA", expiry: today, strike: 200,
    option_type: "call", model: "european", predict_date: today,
  });
  const [ivResult, setIvResult] = useState(null);
  const [mResult, setMResult] = useState(null);
  const [trainInfo, setTrainInfo] = useState(null);
  const [busy, setBusy] = useState({ train: false, iv: false, m: false });
  const [error, setError] = useState(null);

  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  // ── actions ──
  const train = async () => {
    setBusy({ ...busy, train: true }); setTrainInfo(null); setError(null);
    try {
      const [a, b] = await Promise.all([
        fetch(API + "/ml/train-iv?ticker=" + form.ticker),
        fetch(API + "/ml/train-moneyness?ticker=" + form.ticker),
      ]);
      const ja = await a.json(), jb = await b.json();
      if (!a.ok || !b.ok) { setError(ja.detail || jb.detail || "Training failed"); }
      else { setTrainInfo({ iv: ja.metrics, m: jb.metrics }); }
    } catch { setError("Backend unreachable"); }
    setBusy((p) => ({ ...p, train: false }));
  };

  const predictIV = async () => {
    setBusy((p) => ({ ...p, iv: true })); setError(null);
    try {
      const r = await fetch(API + "/ml/predict-iv?" + new URLSearchParams(form));
      const d = await r.json();
      r.ok ? setIvResult(d) : setError(d.detail || "Prediction failed");
    } catch { setError("Backend unreachable"); }
    setBusy((p) => ({ ...p, iv: false }));
  };

  const predictM = async () => {
    setBusy((p) => ({ ...p, m: true })); setError(null);
    try {
      const r = await fetch(API + "/ml/predict-moneyness?" + new URLSearchParams({
        ticker: form.ticker, strike: form.strike,
        expiry: form.expiry, option_type: form.option_type,
      }));
      const d = await r.json();
      r.ok ? setMResult(d) : setError(d.detail || "Classification failed");
    } catch { setError("Backend unreachable"); }
    setBusy((p) => ({ ...p, m: false }));
  };

  // ── helpers ──
  const field = (label, name, type, opts) =>
    h("div", { className: "field", key: name },
      h("span", { className: "field-label" }, label),
      type === "select"
        ? h("select", { className: "field-select", name, value: form[name], onChange: set },
            opts.map(([v, t]) => h("option", { value: v, key: v }, t)))
        : h("input", { className: "field-input", type, name, value: form[name], onChange: set, placeholder: opts || "" })
    );

  const row = (label, val, cls) =>
    h("tr", { key: label }, h("td", null, label), h("td", { className: cls || "" }, val));

  const probBar = (label, p) => {
    const pct = (p * 100).toFixed(1);
    const clr = label === "ITM" ? "#22c55e" : label === "OTM" ? "#ef4444" : "#eab308";
    return h("div", { className: "prob-row", key: label }, [
      h("span", { className: "prob-lbl", key: "l" }, label),
      h("div", { className: "prob-track", key: "t" },
        h("div", { className: "prob-fill", style: { width: pct + "%", background: clr }, key: "f" })
      ),
      h("span", { className: "prob-val", key: "v" }, pct + "%"),
    ]);
  };

  // ── render ──
  return h("div", { className: "ml-page" }, [

    // Inputs card
    h("div", { className: "card", key: "inp" }, [
      h("h3", { className: "card-title", key: "t" }, "Model Inputs"),
      h("div", { className: "ml-field-grid", key: "fg" }, [
        h(TickerSearch, { value: form.ticker, onChange: (v) => setForm({ ...form, ticker: v }), key: "ticker" }),
        field("Strike", "strike", "number"),
        field("Expiry", "expiry", "date"),
        field("Option Type", "option_type", "select", [["call", "Call"], ["put", "Put"]]),
        field("Pricing Model", "model", "select", [
          ["european", "European (Black-Scholes)"], ["american", "American (Binomial)"],
        ]),
        field("Predict Date", "predict_date", "date"),
      ]),
      h("div", { className: "ml-btn-row", key: "btns" }, [
        h("button", { className: "btn btn-dark", onClick: train, disabled: busy.train, key: "b1" },
          busy.train ? "Training..." : "Train on " + form.ticker),
        h("button", { className: "btn btn-blue", onClick: predictIV, disabled: busy.iv, key: "b2" },
          busy.iv ? "Running..." : "Predict IV & Premium"),
        h("button", { className: "btn btn-green", onClick: predictM, disabled: busy.m, key: "b3" },
          busy.m ? "Running..." : "Classify Moneyness"),
      ]),
    ]),

    // Error
    error ? h("div", { className: "error-banner", key: "err" }, error) : null,

    // Training metrics
    trainInfo ? h("div", { className: "card", key: "train" }, [
      h("h3", { className: "card-title", key: "t" }, "Training Metrics"),
      h("div", { className: "metrics-grid", key: "g" }, [
        h("div", { className: "metric-box", key: "iv" }, [
          h("p", { className: "metric-box-title", key: "t" }, "Ridge Regression — IV"),
          h("table", { className: "rtable", key: "tb" }, h("tbody", null, [
            row("Samples", trainInfo.iv.samples),
            row("Features", trainInfo.iv.features_used),
            row("Train R\u00B2", trainInfo.iv.train_r2.toFixed(4)),
            row("CV R\u00B2", trainInfo.iv.cv_r2_mean.toFixed(4) + " \u00B1 " + trainInfo.iv.cv_r2_std.toFixed(4)),
          ])),
        ]),
        h("div", { className: "metric-box", key: "m" }, [
          h("p", { className: "metric-box-title", key: "t" }, "Random Forest — Moneyness"),
          h("table", { className: "rtable", key: "tb" }, h("tbody", null, [
            row("Samples", trainInfo.m.samples),
            row("Features", trainInfo.m.features_used),
            row("Train Accuracy", (trainInfo.m.train_accuracy * 100).toFixed(1) + "%"),
            row("CV Accuracy", (trainInfo.m.cv_accuracy_mean * 100).toFixed(1) + "% \u00B1 " + (trainInfo.m.cv_accuracy_std * 100).toFixed(1) + "%"),
            row("Distribution", Object.entries(trainInfo.m.class_distribution).map(([k, v]) => k + ": " + v).join("  ")),
          ])),
        ]),
      ]),
    ]) : null,

    // Prediction results
    h("div", { className: "ml-results-row", key: "res" }, [

      // IV card
      h("div", { className: "card", key: "iv" }, [
        h("h3", { className: "card-title", key: "t" }, "IV & Premium Prediction"),
        ivResult
          ? h("table", { className: "rtable", key: "tb" }, h("tbody", null, [
              row("Spot", "$" + ivResult.spot_price.toFixed(2)),
              row("ML Predicted IV", (ivResult.ml_predicted_iv * 100).toFixed(2) + "%", "val-hl"),
              row("Market IV", ivResult.market_iv ? (ivResult.market_iv * 100).toFixed(2) + "%" : "—"),
              row("ML Premium", "$" + ivResult.ml_premium.toFixed(2), "val-hl"),
              row("Moneyness", ivResult.moneyness.toFixed(4)),
              row("TTE (yrs)", ivResult.tte.toFixed(4)),
              row("Model", ivResult.model),
            ]))
          : h("p", { className: "empty-state", key: "ph" }, "Train first, then predict"),
      ]),

      // Moneyness card
      h("div", { className: "card", key: "m" }, [
        h("h3", { className: "card-title", key: "t" }, "Moneyness Classification"),
        mResult
          ? h("div", { key: "c" }, [
              h("span", { className: "m-badge " + mResult.prediction.toLowerCase(), key: "b" }, mResult.prediction),
              h("div", { className: "prob-bars", key: "bars" },
                ["ITM", "ATM", "OTM"].map((l) =>
                  mResult.probabilities[l] !== undefined ? probBar(l, mResult.probabilities[l]) : null
                )
              ),
              h("table", { className: "rtable", key: "tb" }, h("tbody", null, [
                row("Spot", "$" + mResult.spot_price.toFixed(2)),
                row("Moneyness", mResult.moneyness.toFixed(4)),
                row("IV Used", (mResult.iv_used * 100).toFixed(2) + "%"),
                row("TTE (yrs)", mResult.tte.toFixed(4)),
              ])),
            ])
          : h("p", { className: "empty-state", key: "ph" }, "Train first, then classify"),
      ]),
    ]),
  ]);
}

export default MLPredictions;
