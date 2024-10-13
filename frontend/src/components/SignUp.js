import React, { useState, useEffect } from "react";
import "../loginStyles.css";

export default function SignUp() {
  // const [newAuthor, setAuthors] = useState({});
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [githubUrl, setGithubUrl] = useState("");

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };
  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };
  const handleDisplayNameChange = (e) => {
    setDisplayName(e.target.value);
  };
  const handleBioChange = (e) => {
    setBio(e.target.value);
  };
  const handleGithubUrlChange = (e) => {
    setGithubUrl(e.target.value);
  };

  const newA = {
    username: username,
    password: password,
    displayName: displayName,
    bio: bio,
    githubUrl: githubUrl,
  };

  function addAuthor() {}

  return (
    <div>
      <h2 className="app-subtitle">Welcome to the Sign Up page!</h2>
      <img className="login-image" src="login-image.png" alt="login" />
      <input
        type="text"
        className="username"
        placeholder="Username"
        value={username}
        onChange={handleUsernameChange}
      />
      <input
        type="text"
        className="password"
        placeholder="Password"
        value={password}
        onChange={handlePasswordChange}
      />
      <input
        type="text"
        className="display_name"
        placeholder="Display Name"
        value={displayName}
        onChange={handleDisplayNameChange}
      />
      <input
        type="text"
        className="bio"
        placeholder="Bio"
        value={bio}
        onChange={handleBioChange}
      />
      <input
        type="text"
        className="github_url"
        placeholder="Github Url"
        value={githubUrl}
        onChange={handleGithubUrlChange}
      />

      <button type="submit" className="signup-button" onClick={addAuthor}>
        Submit
      </button>
    </div>
  );
}
