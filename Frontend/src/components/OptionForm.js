import React, { useState } from "react";

function OptionForm() {
  const [form, setForm] = useState({
    model: "european",
    ticker: "AAPL",
    expiry: "2025-09-26",
    strike: 150,
    option_type: "call",
    predict_date: "",
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const params = new URLSearchParams(form).toString();
    try {
      const res = await fetch(`http://127.0.0.1:8000/option-price?${params}`);
      if (!res.ok) {
        const err = await res.json();
        setError(err.detail || "Server error");
        setResult(null);
        return;
      }
      const data = await res.json();
      console.log("API Response:", data); // debug log
      setResult(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching:", err);
      setError("Failed to connect to backend");
      setResult(null);
    }
  };

  return React.createElement("div", { className: "calculator" }, [
    React.createElement(
      "form",
      { onSubmit: handleSubmit, className: "form-grid", key: "form" },
      [
        // Left column: Inputs
        React.createElement("div", { className: "inputs", key: "inputs" }, [
          React.createElement("h2", { key: "ip-title" }, "Input Parameters"),

          React.createElement("label", { key: "model" }, [
            "Market Model",
            React.createElement("select", {
              name: "model",
              value: form.model,
              onChange: handleChange
            }, [
              React.createElement("option", { value: "european", key: "euro" }, "European (Black-Scholes)"),
              React.createElement("option", { value: "american", key: "amer" }, "American (Binomial)")
            ])
          ]),

          React.createElement("label", { key: "ticker" }, [
            "Ticker Symbol",
            React.createElement("input", {
              type: "text",
              name: "ticker",
              value: form.ticker,
              onChange: handleChange
            })
          ]),

          React.createElement("label", { key: "option_type" }, [
            "Option Type",
            React.createElement("select", {
              name: "option_type",
              value: form.option_type,
              onChange: handleChange
            }, [
              React.createElement("option", { value: "call", key: "call" }, "Call"),
              React.createElement("option", { value: "put", key: "put" }, "Put")
            ])
          ]),

          React.createElement("label", { key: "strike" }, [
            "Strike Price",
            React.createElement("input", {
              type: "number",
              name: "strike",
              value: form.strike,
              onChange: handleChange
            })
          ]),

          React.createElement("label", { key: "expiry" }, [
            "Expiry Date",
            React.createElement("input", {
              type: "text",
              name: "expiry",
              value: form.expiry,
              onChange: handleChange,
              placeholder: "YYYY-MM-DD"
            })
          ]),

          React.createElement("label", { key: "predict_date" }, [
            "Predict Date (Optional)",
            React.createElement("input", {
              type: "text",
              name: "predict_date",
              value: form.predict_date,
              onChange: handleChange,
              placeholder: "YYYY-MM-DD"
            })
          ]),

          React.createElement("button", { type: "submit", className: "btn", key: "submit" }, "Calculate")
        ]),

        // Right column: Results
        React.createElement("div", { className: "results", key: "results" }, [
          React.createElement("h2", { key: "res-title" }, "Calculated Values"),

          error
            ? React.createElement("p", { className: "error", key: "error" }, error)
            : result
            ? React.createElement("table", { className: "results-table", key: "res-table" }, [
                React.createElement("tbody", { key: "body" }, [
                  React.createElement("tr", { key: "premium" }, [
                    React.createElement("td", { key: "label" }, "Theoretical Price"),
                    React.createElement(
                      "td",
                      { key: "value" },
                      result.premium !== undefined && result.premium !== null
                        ? result.premium.toFixed(2)
                        : "N/A"
                    )
                  ]),
                  React.createElement("tr", { key: "ticker" }, [
                    React.createElement("td", null, "Ticker"),
                    React.createElement("td", null, result.ticker || "N/A")
                  ]),
                  React.createElement("tr", { key: "expiry" }, [
                    React.createElement("td", null, "Expiry"),
                    React.createElement("td", null, result.expiry || "N/A")
                  ]),
                  React.createElement("tr", { key: "strike" }, [
                    React.createElement("td", null, "Strike"),
                    React.createElement("td", null, result.strike || "N/A")
                  ]),
                  React.createElement("tr", { key: "type" }, [
                    React.createElement("td", null, "Option Type"),
                    React.createElement("td", null, result.option_type || "N/A")
                  ]),
                  React.createElement("tr", { key: "model" }, [
                    React.createElement("td", null, "Model Used"),
                    React.createElement("td", null, result.model || "N/A")
                  ])
                ])
              ])
            : React.createElement("p", { key: "no-data" }, "Enter inputs and click Calculate to see results")
        ])
      ]
    )
  ]);
}

export default OptionForm;
