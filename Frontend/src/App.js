import React, { useState } from "react";
import OptionForm from "./components/OptionForm";
import MLPredictions from "./components/MLPredictions";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("pricing");

  return React.createElement(
    "div",
    { className: "app" },
    [
      React.createElement("h1", { className: "title", key: "title" }, "ThetaStrike"),
      React.createElement(
        "p",
        { className: "subtitle", key: "subtitle" },
        "AI-Powered Options Pricing & Analytics Engine"
      ),

      // Tab Navigation
      React.createElement("div", { className: "tab-nav", key: "tabs" }, [
        React.createElement(
          "button",
          {
            className: "tab-btn" + (activeTab === "pricing" ? " active" : ""),
            onClick: () => setActiveTab("pricing"),
            key: "tab-pricing",
          },
          "Option Pricing"
        ),
        React.createElement(
          "button",
          {
            className: "tab-btn" + (activeTab === "ml" ? " active" : ""),
            onClick: () => setActiveTab("ml"),
            key: "tab-ml",
          },
          "ML Predictions"
        ),
      ]),

      // Tab Content
      activeTab === "pricing"
        ? React.createElement(OptionForm, { key: "form" })
        : React.createElement(MLPredictions, { key: "ml" }),
    ]
  );
}

export default App;
