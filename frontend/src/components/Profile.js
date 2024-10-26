import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";
import { cusFetch } from './Login';

const apiUrl = process.env.REACT_APP_API_URL

/**
 * This is a component for displaying the profile page
 *  import "../streamStyle_Sukh.css";
 *
 */
export default function Profile() {
  const [author, setAuthor] = useState([]);
  const [posts, setPosts] = useState([]);
  const { authorId } = useParams();
  const navigate = useNavigate();
  // https://stackoverflow.com/questions/63193114/how-do-i-call-a-function-automatically-when-page-loads-up-in-react-js-in-2020
  useEffect(() => {
    ownProfile();
  }, []);

  // get the author info
  useEffect(() => {
    cusFetch(`${apiUrl}author/${authorId}`)
      .then((response) => response.json())
      .then((data) => setAuthor(data));
  }, [authorId]);
  // get the posts list
  useEffect(() => {
    cusFetch(`${apiUrl}post/`)
      .then((response) => response.json())
      .then((data) => setPosts(data));
  }, []);
  // get the author id as an int
  const authorIdInt = parseInt(authorId);

  // check if the post is from current user
  const matchesAuthor = (post, id) => {
    return post.author === id;
  };
  const matchesPublic = (post) => {
    return post.visibility.toLowerCase() === "public";
  };

  // navigate to the edit profile page
  const handleEditProfile = () => {
    navigate(`/stream/${authorId}/editProfile`);
  };

  // go back to stream page
  const goBackStream = () => {
    navigate(`/stream/${localStorage.getItem("logged_in_id")}`);
  };
  
  // Handle comment submission
  const handleFollow = async (event) => {
    event.preventDefault();
    var loggedIn = localStorage.getItem("logged_in_id");
    const response = await cusFetch(`${apiUrl}follow/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        follower: loggedIn,
        followed: authorId,
        pending: "yes"
      }),
    });
    var body = JSON.stringify({
      follower: authorId,
      followed: authorId,
      pending: "yes"
    });
    if (response.ok) {
      alert("hello");
    }
  };
  // get posts that belong to the current user
  const visiblePosts = posts.filter(
    (post) => matchesAuthor(post, authorIdInt) && matchesPublic(post)
  );
  // sort visible posts so that the most recent updated posts appear at the top
  const sortedPosts = visiblePosts
    .sort((a, b) => {
      return (
        new Date(a.scheduled_for).getTime() -
        new Date(b.scheduled_for).getTime()
      );
    })
    .reverse();
  const ownProfile = () => {
    if(authorId == localStorage.getItem("logged_in_id")) {
      document.getElementById("followButton").hidden = true;
    };
  };
  return (
    <div className="profile-page">
      <h2 className="page-subtitle">Welcome to the Profile page!</h2>
      <button className="profile-goBackBtn" onClick={goBackStream}>
        Back To Stream
      </button>
      <h4 className="profile-txt">Name: </h4>
      <p className="profile-name">{author.display_name}</p>
      <h4 className="profile-txt">Bio: </h4>
      <p className="profile-bio">{author.bio}</p>
      <h4 className="profile-txt">Github URL: </h4>
      <p className="profile-git">{author.github_url}</p>
      <button onClick={handleEditProfile}>Edit Profile</button>
      <button id="followButton" onClick={handleFollow} >Follow</button>
      <div className="post-grid">
        {sortedPosts.map((post) => (
          <PostCards post={post} key={post.id} editable={false}></PostCards>
        ))}

      </div>

    </div>
  );
}
