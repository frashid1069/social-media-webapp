import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";

/**
 * This is a component for displaying the personal stream page by using PostCards component.
 * Click Profile button => go to profile page
 * Click Go to Edit Mode button => show only editable posts
 *      Click a post => go to edit page
 * Click Go to Stream Mode button => show all accessible posts
 * Add comment functionality completed
 *
 */
export default function Stream() {
  const [posts, setPosts] = useState([]);
  const [isVisible, setIsVisible] = useState(true);
  const navigate = useNavigate();

  const { authorId } = useParams();

  // get the posts list
  useEffect(() => {
    fetch("http://localhost:8000/service/post/")
      .then((response) => response.json())
      .then((data) => setPosts(data));
  }, []);

  // get the author id
  const authorIdInt = parseInt(authorId);

  // check if the post is deleted
  const matchUndelete = (post) => {
    return post.is_deleted === false;
  };

  // check if the post is public
  const matchesPublic = (post) => {
    return post.visibility.toLowerCase() === "public";
  };

  // check if the post is friends-only
  const matchesFriends = (post) => {
    return post.visibility.toLowerCase() === "friend only";
  };

  // check if the post is from current user
  const matchesAuthor = (post, id) => {
    return post.author === id;
  };

  // get the public posts and posts that belong to the current user
  const visiblePosts = posts.filter(
    (post) =>
      matchUndelete(post) &&
      (matchesPublic(post) ||
        matchesAuthor(post, authorIdInt) ||
        matchesFriends(post))
  );

  // sort visible posts so that the most recent updated posts appear at the top
  const sortedAllPosts = visiblePosts
    .sort((a, b) => {
      return (
        new Date(a.scheduled_for).getTime() -
        new Date(b.scheduled_for).getTime()
      );
    })
    .reverse();
  // get the posts that belong to the current user
  const editablePosts = posts.filter((post) =>
    matchesAuthor(post, authorIdInt)
  );
  const sortedEditablePosts = editablePosts
    .sort((a, b) => {
      return (
        new Date(a.scheduled_for).getTime() -
        new Date(b.scheduled_for).getTime()
      );
    })
    .reverse();
  // Go to the editable profile page belongs to the current user
  const goEditableProfile = () => {
    navigate(`/stream/${authorId}/profile`);
  };

  // Go to the create post page for the current user
  const goCreatePost = () => {
    navigate(`/stream/${authorId}/createPost`);
  };

  return (
    <div className="stream-page">
      {/* Conditional Title */}
      <h2 className="page-subtitle">{isVisible ? "Welcome to the Stream Page!" : "Edit Page"}</h2>
      
      <div className="button-container">
        <button className="edit-profile-btn" onClick={goEditableProfile}>
          Profile
        </button>
        <button className="go-create-post" onClick={goCreatePost}>
          Make a Post
        </button>
        <button
          className="post-edit-btn"
          onClick={() => setIsVisible(!isVisible)}
        >
          {isVisible ? "Go to Edit Mode" : "Go to Stream Mode"}
        </button>
      </div>
  
      {isVisible && (
        <div className="post-grid">
          {sortedAllPosts.map((post) => (
            <PostCards post={post} key={post.id} editable={false}></PostCards>
          ))}
        </div>
      )}
      {!isVisible && (
        <div className="post-grid">
          {sortedEditablePosts.map((post) => (
            <PostCards post={post} key={post.id} editable={true}></PostCards>
          ))}
        </div>
      )}
    </div>
  );
  
}
