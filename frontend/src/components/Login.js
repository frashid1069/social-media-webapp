import React from "react";
import "../loginStyles.css";

export default function Login() {
  return (
    <div className="login-page">
      <h2 className="app-subtitle">Welcome to the login page!</h2>
      <img className="login-image" src="login-image.png" alt="login" />
      <input type="text" className="username" placeholder="Username" />
      <input type="password" className="password" placeholder="Password" />
      <button type="submit" className="login-button">
        Login
      </button>
      <button type="submit" className="signup-button">
        Sign Up
      </button>
    </div>
  );
}
