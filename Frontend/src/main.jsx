import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.js";   // use App.js not App.jsx
import "./App.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  React.createElement(React.StrictMode, null,
    React.createElement(App)
  )
);
