import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";

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
  // get the author info
  useEffect(() => {
    fetch(`http://localhost:8000/service/author/${authorId}`)
      .then((response) => response.json())
      .then((data) => setAuthor(data));
  }, [authorId]);
  // get the posts list
  useEffect(() => {
    fetch("http://localhost:8000/service/post/")
      .then((response) => response.json())
      .then((data) => setPosts(data));
  }, []);
  // get the author id as an int
  const authorIdInt = parseInt(authorId);

  // check if the post is from current user
  const matchesAuthor = (post, id) => {
    return post.author === id;
  };

  // navigate to the edit profile page
  const handleEditProfile = () => {
    navigate(`/stream/${authorId}/editProfile`);
  };

  // get posts that belong to the current user
  const visiblePosts = posts.filter((post) => matchesAuthor(post, authorIdInt));
  // sort visible posts so that the most recent updated posts appear at the top
  const sortedPosts = visiblePosts
    .sort((a, b) => {
      return (
        new Date(a.scheduled_for).getTime() -
        new Date(b.scheduled_for).getTime()
      );
    })
    .reverse();
  return (
    <div className="profile-page">
      <h2 className="page-subtitle">Welcome to the Profile page!</h2>
      <h4 className="profile-txt">Name: </h4>
      <p className="profile-name">{author.display_name}</p>
      <h4 className="profile-txt">Bio: </h4>
      <p className="profile-bio">{author.bio}</p>
      <h4 className="profile-txt">Github URL: </h4>
      <p className="profile-git">{author.github_url}</p>
      <button onClick={handleEditProfile}>Edit Profile</button>
      <div className="post-grid">
        {sortedPosts.map((post) => (
          <PostCards post={post} key={post.id} editable={false}></PostCards>
        ))}
        
      </div>
      
    </div>
  );
}
