import React from "react";
import { useNavigate } from "react-router-dom";
/**
 * This a component for displaying the welcome page
 *
 *
 */
export default function Welcome() {
  const navigate = useNavigate();
  const goLogin = () => {
    navigate("/login");
  };
  const goSignup = () => {
    navigate("/signup");
  };
  return (
    <div>
      <h1>Welcome to Aquamarine 404 Project</h1>
      <button className="go-to-login" onClick={goLogin}>
        Go Login
      </button>
      <button className="go-to-signup" onClick={goSignup}>
        Go Sign Up
      </button>
    </div>
  );
}
