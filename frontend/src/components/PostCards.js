import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import "../streamStyle_Sukh.css";
import Comment from "./Comment";

/**
 * This is a component for displaying posts for the corresponded author using Comment component
 * @param post: single post object
 * @param editable: a boolean that implies whether the post is editable
 * Click author button => go to the corresponding author's profile
 */

export default function PostCards({ post, editable }) {
  const [authors, setAuthors] = useState([]);
  const [comments, setComments] = useState([]);
  const navigate = useNavigate();
  // get the author list
  useEffect(() => {
    fetch("http://localhost:8000/service/author/")
      .then((response) => response.json())
      .then((data) => setAuthors(data));
  }, []);
  // get the comment list
  useEffect(() => {
    fetch("http://localhost:8000/service/comment/")
      .then((response) => response.json())
      .then((data) => setComments(data));
  }, []);
  // find the corresponding author's name for the post
  const matchAuthor = (authorId) => {
    for (const author of authors) {
      if (author.id === authorId) {
        return author.display_name;
      }
    }
  };
  // find the comments for the post
  const commentFilter = (comment) => {
    return comment.post === post.id;
  };
  const matchedComments = comments.filter((comment) => commentFilter(comment));
  // go to edit page if
  const goEdit = () => {
    if (editable) {
      navigate(`/stream/${post.author}/${post.id}/edit`);
    }
  };

  // go to the corresponding profile
  const goProfile = () => {
    navigate(`/stream/${post.author}/profile`);
  };

  return (
    <div key={post.id} className="post-card" onClick={goEdit}>
      <h3 className="post-card-title">{post.title}</h3>
      <button className="post-card-author" onClick={goProfile}>
        {matchAuthor(post.author)}
      </button>
      <p className="post-card-content">{post.content}</p>
      <p className="post-card-update-date">Updated at: {post.updated_at}</p>
      <div className="comment-grid">
        <h5 className="comment-title">Comments: </h5>
        {matchedComments.map((comment) => (
          <Comment comment={comment} key={comment.id}></Comment>
        ))}
      </div>
    </div>
  );
}
