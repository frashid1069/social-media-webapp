import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MeteorShower from "./utils/MeteorShower";
const apiUrl = process.env.REACT_APP_API_URL
/**
 * This is a component for displaying the login page
 * after inputing correct username and password and clicking
 * Login button, user will be redirected to a personal stream page
 */
export default function Login() {
  // const [authors, setAuthors] = useState([]);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState(null);
  const navigate = useNavigate();

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };
  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  // const fetchCurrentAuthor = async (userID) => {
  //   const response = await cusFetch(`${apiUrl}authors/${userID}`);
  //   const data = await response.json();

  //   if (data && data.type==='author') {
  //     const author = new Author(data);
  //     localStorage.setItem("currentAuthor", JSON.stringify(author.toJSON()));
  //   }
  // };

  const verify = async () => {
    try {
      const response = await fetch(`${apiUrl}login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      if (response.ok) {
        //{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6Imp3dCJ9.eyJpZCI6NiwidXNlcm5hbWUiOiJkZCIsImV4cCI6MTczNTgyNjEyNX0.TtEw79FiozqpvXogephO_-IpfCNZQku97rJ7V-1vOcc",
        //"user":{"id":6,"username":"dd","display_name":"dd"}}
        const data = await response.json();
        const token = data.token;
        localStorage.setItem("token", token);
        localStorage.setItem("logged_in_id", data.user.id);
        // fetchCurrentAuthor(data.user.id);
        var user = data.user
        var author = user.author.id
        localStorage.setItem("currentAuthorId", author);
        const store = localStorage.getItem("currentAuthorId");
        navigate(`/stream/${encodeURIComponent(store)}`);
      } else {
        //const data = await response.json();
        //navigate(`${data.error}`);
        setErrorMessage("An error occurred during login.");
      }
    } catch (error) {
      console.error("Login error:", error);
      setErrorMessage("An error occurred during login.");
    }
  };

  function goSignUp() {
    navigate("/signup");
  }




  return (
    <div className="login-page">
      <h2 className="page-subtitle">Welcome to Aquamarine!</h2>
      <div className="login-window">
      <h2 className="page-subtitle">Login</h2>
        <input
          type="text"
          className="username"
          placeholder="Username"
          value={username}
          onChange={handleUsernameChange}
        />

        <input
          type="password"
          className="password"
          placeholder="Password"
          value={password}
          onChange={handlePasswordChange}
        />
        {errorMessage && <p className="error-message">{errorMessage}</p>}

        <button type="submit" className="login-button" onClick={verify}>
          Login
        </button>

        <button type="submit" className="signup-button" onClick={goSignUp}>
          Sign Up
        </button>

      </div>



      <div className="App">
        <MeteorShower count={6} /> {/* Adjust count to change meteor density */}
      </div>

    </div>
  );
}

export const cusFetch = (url, options = {}) => {
  const token = localStorage.getItem("token");
  const defaultHeaders = {
    "Content-Type": "application/json",
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };

  return fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
};
