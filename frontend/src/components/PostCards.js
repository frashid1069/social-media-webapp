import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";

export default function PostCards({ post }) {
  const [authors, setAuthors] = useState([]);
  useEffect(() => {
    fetch("http://localhost:8000/service/author/")
      .then((response) => response.json())
      .then((data) => setAuthors(data));
  }, []);
  // find the corresponding author's name for the post
  const matchAuthor = (authorId) => {
    for (const author of authors) {
      if (author.id === authorId) {
        return author.display_name;
      }
    }
  };
  return (
    <div key={post.id} className="post-card">
      <h3 className="post-card-title">{post.title}</h3>
      <h4 className="post-card-author">{matchAuthor(post.author)}</h4>
      <p className="post-card-content">{post.content}</p>
      <p className="post-card-update-date">{post.updated_at}</p>
    </div>
  );
}
