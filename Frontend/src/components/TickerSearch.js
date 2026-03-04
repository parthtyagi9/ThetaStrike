import React, { useState, useRef, useEffect } from "react";

const API = "http://127.0.0.1:8000";
const h = React.createElement;

/**
 * Autocomplete ticker input.
 * Props: value, onChange(ticker), name
 */
function TickerSearch({ value, onChange, name = "ticker" }) {
  const [query, setQuery] = useState(value || "");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [activeIdx, setActiveIdx] = useState(-1);
  const wrapRef = useRef(null);
  const timerRef = useRef(null);

  // sync external value changes
  useEffect(() => { setQuery(value || ""); }, [value]);

  // close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const search = (q) => {
    clearTimeout(timerRef.current);
    if (q.length < 1) { setResults([]); setOpen(false); return; }
    timerRef.current = setTimeout(async () => {
      try {
        const r = await fetch(API + "/search-ticker?q=" + encodeURIComponent(q));
        const data = await r.json();
        setResults(data);
        setOpen(data.length > 0);
        setActiveIdx(-1);
      } catch { setResults([]); setOpen(false); }
    }, 200);
  };

  const pick = (symbol) => {
    setQuery(symbol);
    setOpen(false);
    setResults([]);
    onChange(symbol);
  };

  const handleChange = (e) => {
    const v = e.target.value.toUpperCase();
    setQuery(v);
    onChange(v);
    search(v);
  };

  const handleKey = (e) => {
    if (!open || results.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      pick(results[activeIdx].symbol);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  return h("div", { className: "field", key: name, ref: wrapRef },
    h("span", { className: "field-label" }, "Ticker"),
    h("div", { className: "ticker-wrap" },
      h("input", {
        className: "field-input",
        type: "text",
        name,
        value: query,
        onChange: handleChange,
        onKeyDown: handleKey,
        onFocus: () => { if (results.length > 0) setOpen(true); },
        placeholder: "Search ticker…",
        autoComplete: "off",
      }),
      open && results.length > 0
        ? h("ul", { className: "ticker-dropdown" },
            results.map((r, i) =>
              h("li", {
                key: r.symbol,
                className: "ticker-opt" + (i === activeIdx ? " active" : ""),
                onMouseDown: () => pick(r.symbol),
                onMouseEnter: () => setActiveIdx(i),
              },
                h("span", { className: "ticker-sym" }, r.symbol),
                h("span", { className: "ticker-name" }, r.name),
              )
            )
          )
        : null
    )
  );
}

export default TickerSearch;
