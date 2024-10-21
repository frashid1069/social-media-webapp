import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import ReactMarkdown from 'react-markdown';
import "../streamStyle_Sukh.css";  // Import the CSS file for consistent styling

export default function PostDetail() {
  const { postId } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`http://localhost:8000/posts/${postId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Post not found");
            }
            return response.json();
        })
        .then((data) => {
            if (data.visibility === "public" || data.visibility === "unlisted") {
                setPost(data);
            } else {
                setError("This post is private and cannot be viewed.");
            }
        })
        .catch((error) => setError("Failed to fetch post. " + error.message));
}, [postId]);



  if (error) {
    return <p>{error}</p>;
  }

  if (!post) {
    return <p>Loading...</p>;
  }

  return (
    <div className="post-card">
      <h2 className="post-card-title">{post.title}</h2>
      <h4 className="post-card-author">Author ID: {post.author_id}</h4>
      
      {/* Render the Markdown content using react-markdown */}
      <div className="post-card-content">
        <ReactMarkdown>{post.content}</ReactMarkdown>
      </div>
      
      <p className="post-card-update-date">
        Last updated: {new Date(post.updated_at).toLocaleString()}
      </p>
    </div>
  );
}
