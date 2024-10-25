import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../loginStyles.css";
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

  // get the author list
  // useEffect(() => {
  //   fetch(`${apiUrl}author/`)
  //     .then((response) => response.json())
  //     .then((data) => {
  //       console.log(data);
  //       setAuthors(data);
  //     });
  // }, []);

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };
  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  // check if the input username and author's username match
  // const matchesUsername = (author, username) => {
  //   return author.username === username;
  // };

  // check if the input password and author's password match
  // const matchesPassword = (author, password) => {
  //   return author.password === password;
  // };

  // find the matched author by comparing username and password
  // const filterAuthor = authors.filter(
  //   (author) =>
  //     matchesUsername(author, username) && matchesPassword(author, password)
  // );

  // for existed user, redirect to its stream page, otherwise redirect to sign up page
  // function verify() {
  //   if (filterAuthor.length === 0) {
  //     console.log(filterAuthor);
  //     navigate("/signup");
  //   } else {
  //     navigate(`/stream/${filterAuthor[0].id}`);
  //   }
  // }
  // function goSignUp() {
  //   navigate("/signup");
  // }
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
        navigate(`/stream/${data.user.id}`);
      } else {
        const data = await response.json();
        navigate(`${data.error}`);
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
      <h2 className="page-subtitle">Welcome to the login page!</h2>

      <img className="login-image" src="login-image.png" alt="login" />

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
  );
}

export const cusFetch = (url, options = {}) => {
  const token = localStorage.getItem("token");
  const defaultHeaders = {
    "Content-Type": "application/json",
    ...(token && { 'token': `${token}` }),
  };

  return fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
};