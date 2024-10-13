import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";

export default function Stream() {
  const [posts, setPosts] = useState([]);
  const { id } = useParams();
  const navigate = useNavigate();

  // get the posts list
  useEffect(() => {
    fetch("http://localhost:8000/service/post/")
      .then((response) => response.json())
      .then((data) => setPosts(data));
  }, []);

  // check if the post is public
  const matchesVisibility = (post) => {
    return post.visibility.toLowerCase() === "public";
  };

  // check if the post is from current user
  const matchesAuthor = (post, id) => {
    return post.author === id;
  };

  // get the public posts and posts that belong to the current user
  const visiblePosts = posts.filter(
    (post) => matchesVisibility(post) || matchesAuthor(post, id)
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
  // redirect to edit page
  function goEdit() {
    navigate(`/edit`);
  }
  // get the editable posts
  const editablePosts = posts.filter((post) => matchesAuthor(post, id));
  return (
    <div className="stream-page">
      <h2 className="page-subtitle">Welcome to the stream page!</h2>
      <a className="profile-link" href="/stream/:id/profile">
        Profile
      </a>

      <div className="post-grid" onClick={goEdit}>
        {sortedPosts.map((post) => (
          <PostCards post={post} key={post.id}></PostCards>
        ))}
      </div>
    </div>
  );
}
