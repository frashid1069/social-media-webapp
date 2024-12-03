import React, { useState, useEffect } from "react";
/**
 * This a component for displaying the sign up page
 ***************************** NOT WORKING *******************************
 ***************** NEED TO FIX PROBLEM WITH UPLOADING IMAGE **************
 *
 */
export default function SignUp() {
  // const [newAuthor, setAuthors] = useState({});
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [selectedImage, setSelectedImage] = useState("");

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

const handleSubmit = async (event) => {
  const apiUrl = process.env.REACT_APP_API_URL + 'signup/';
  event.preventDefault();
  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
        display_name: displayName,
        bio: bio,
        profile_image: selectedImage,
        github_url: githubUrl,
      }),
    })
      .then((responsess) => responsess.json())
      .then((data) => console.log(data));

    if (response.ok) {
      // const data = await response.json();
      // console.log("SignUp data: ", data);
      // const author = new Author(data);    // Create an Author instance as current author
      // localStorage.setItem("currentAuthor", JSON.stringify(author.toJSON()));   // Save to local storage
      window.location.href = "/login"; // Redirect after saving
    } 
  } 
  catch (error) {
    alert("Requested admin to register user");
    window.location.href = "/home/login"; // Redirect after saving
  }
};

return (
  <div>
    <h2 className="app-subtitle">Welcome to the Sign Up page!</h2>
    <img className="login-image" src="login-image.png" alt="login" />
    <form onSubmit={handleSubmit}>
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
      <input
        type="file"
        className="myImage"
        // Event handler to capture file selection and update the state
        onChange={(event) => {
          console.log(event.target.files[0]); // Log the selected file
          setSelectedImage(event.target.files[0]); // Update the state with the selected file
        }}
      />

      <button type="submit" className="signup-button">
        Submit
      </button>
    </form>
  </div>
);
}