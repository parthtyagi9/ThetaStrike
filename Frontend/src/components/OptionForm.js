import React, { useState } from "react";

function OptionForm() {
  const [form, setForm] = useState({
    model: "european",
    ticker: "NVDA",
    expiry: "2026-01-30",
    strike: 200,
    option_type: "call",
    predict_date: "",
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/option-price?" + new URLSearchParams(form)
      );
      const data = await res.json();
      if (!res.ok) { setError(data.detail || "Server error"); setResult(null); }
      else { setResult(data); }
    } catch {
      setError("Could not reach the backend");
      setResult(null);
    }
    setLoading(false);
  };

  const h = React.createElement;

  const field = (label, name, type, opts) =>
    h("div", { className: "field", key: name },
      h("span", { className: "field-label" }, label),
      type === "select"
        ? h("select", { className: "field-select", name, value: form[name], onChange: set },
            opts.map(([v, t]) => h("option", { value: v, key: v }, t))
          )
        : h("input", {
            className: "field-input", type, name, value: form[name],
            onChange: set, placeholder: opts || "",
          })
    );

  const row = (label, val, cls) =>
    h("tr", { key: label },
      h("td", null, label),
      h("td", { className: cls || "" }, val)
    );

  return h("form", { onSubmit: submit, className: "pricing-grid" }, [
    // left — inputs
    h("div", { className: "card", key: "inp" }, [
      h("h3", { className: "card-title", key: "t" }, "Parameters"),
      field("Pricing Model", "model", "select", [
        ["european", "European (Black-Scholes)"],
        ["american", "American (Binomial)"],
      ]),
      field("Ticker", "ticker", "text"),
      field("Option Type", "option_type", "select", [["call", "Call"], ["put", "Put"]]),
      field("Strike Price", "strike", "number"),
      field("Expiry Date", "expiry", "text", "YYYY-MM-DD"),
      field("Predict Date", "predict_date", "text", "YYYY-MM-DD (optional)"),
      h("button", {
        type: "submit", className: "btn btn-dark", key: "go",
        disabled: loading,
      }, loading ? "Calculating..." : "Calculate"),
    ]),

    // right — results
    h("div", { className: "card", key: "res" }, [
      h("h3", { className: "card-title", key: "t" }, "Results"),
      error
        ? h("div", { className: "error-banner", key: "err" }, error)
        : result
        ? h("table", { className: "rtable", key: "tbl" },
            h("tbody", null, [
              row("Premium", "$" + result.premium.toFixed(2), "val-hl"),
              row("Spot Price", "$" + (result.spot_price_used != null ? result.spot_price_used.toFixed(2) : "N/A")),
              row("Ticker", result.ticker),
              row("Strike", result.strike),
              row("Expiry", result.expiry),
              row("Type", result.option_type),
              row("Model", result.model),
            ])
          )
        : h("p", { className: "empty-state", key: "ph" }, "Set parameters and press Calculate"),
    ]),
  ]);
}

export default OptionForm;
