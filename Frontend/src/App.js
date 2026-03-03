import React, { useState } from "react";
import OptionForm from "./components/OptionForm";
import MLPredictions from "./components/MLPredictions";
import "./App.css";

function App() {
  const [tab, setTab] = useState("pricing");

  return React.createElement("div", { className: "app" }, [
    // Header
    React.createElement("div", { className: "header", key: "hdr" }, [
      React.createElement("h1", { className: "title", key: "t" }, "ThetaStrike"),
      React.createElement("p", { className: "subtitle", key: "s" },
        "Options pricing & analytics — Black-Scholes, Binomial, and ML models"
      ),
    ]),

    // Tabs
    React.createElement("nav", { className: "tab-nav", key: "nav" }, [
      React.createElement("button", {
        className: "tab-btn" + (tab === "pricing" ? " active" : ""),
        onClick: () => setTab("pricing"),
        key: "t1",
      }, "Pricing"),
      React.createElement("button", {
        className: "tab-btn" + (tab === "ml" ? " active" : ""),
        onClick: () => setTab("ml"),
        key: "t2",
      }, "ML Predictions"),
    ]),

    // Page
    tab === "pricing"
      ? React.createElement(OptionForm, { key: "pricing" })
      : React.createElement(MLPredictions, { key: "ml" }),
  ]);
}

export default App;
