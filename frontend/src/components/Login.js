import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../loginStyles.css";
// import SignUp from "./SignUp";
import Stream from "./Stream";

export default function Login() {
  const [authors, setAuthors] = useState([]);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  // get the author list
  useEffect(() => {
    fetch("http://localhost:8000/service/author/")
      .then((response) => response.json())
      .then((data) => setAuthors(data));
  }, []);

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };
  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };
  // check if the input username and author's username match
  const matchesUsername = (author, username) => {
    return author.username === username;
  };
  // check if the input password and author's password match
  const matchesPassword = (author, password) => {
    return author.password === password;
  };
  // find the matched author by comparing username and password
  const filterAuthor = authors.filter(
    (author) =>
      matchesUsername(author, username) && matchesPassword(author, password)
  );
  // for existed user, redirect to its stream page, otherwise redirect to sign up page
  function verify() {
    if (filterAuthor.length === 0) {
      navigate("/signup");
    } else {
      navigate(`/stream/${filterAuthor[0].id}`);
    }
  }
  return (
    <div className="login-page">
      <h2 className="app-subtitle">Welcome to the login page!</h2>
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

      <button type="submit" className="login-button" onClick={verify}>
        Login
      </button>
      <Link to="/signup">
        <button type="submit" className="signup-button">
          Sign Up
        </button>
      </Link>
    </div>
  );
}
