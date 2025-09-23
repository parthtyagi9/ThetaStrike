import React from "react";
import OptionForm from "./components/OptionForm";
import "./App.css";

function App() {
  return React.createElement(
    "div",
    { className: "app" },
    [
      React.createElement("h1", { className: "title", key: "title" }, "Option Pricing Calculator"),
      React.createElement(
        "p",
        { className: "subtitle", key: "subtitle" },
        "Calculate theoretical option prices using Black-Scholes (European) and Binomial (American) models"
      ),
      React.createElement(OptionForm, { key: "form" })
    ]
  );
}

export default App;
