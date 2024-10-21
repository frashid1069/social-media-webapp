import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../likes.css";
const apiUrl = process.env.REACT_APP_API_URL

export default function Likes() {
  const { authorId, postId } = useParams();
  const [likes, setLikes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authors, setAuthors] = useState([]);
  const navigate = useNavigate(); // For navigation

  useEffect(() => {
    // Fetch likes for the specific post
    fetch(`${apiUrl}like/?post=${postId}`)
      .then((response) => response.json())
      .then((data) => {
        setLikes(data); // Set filtered likes based on postId
        setLoading(false); // Turn off loading
      })
      .catch((error) => console.error("Error fetching likes:", error));
  }, [postId]);

  useEffect(() => {
    // Fetch authors for name matching
    fetch(`${apiUrl}author/`)
      .then((response) => response.json())
      .then((data) => setAuthors(data))
      .catch((error) => console.error("Error fetching authors:", error));
  }, []);

  // Match the author's display name by their ID
  const matchAuthor = (authorId) => {
    const author = authors.find((a) => a.id === authorId);
    return author ? author.display_name : "Unknown Author";
  };

  const handleBackClick = () => {
    navigate(-1); // Take the user back to the previous page (/stream/${post.author}/${post.id} or /author/${authorId}/posts/${post.id}/
  };

  return (
    <div className="like-page">
      <div className="like-page-content">
        <button className="btn-back" onClick={handleBackClick}>
          Back
        </button>
        <h2>Likes</h2>
        {loading ? (
          <p>Loading likes...</p>
        ) : (
          <>
            <p>Total Likes: {likes.length}</p>
            <ul>
              {likes.length > 0 ? (
                likes.map((like) => (
                  <li key={like.id}>
                    <p>Liked by: {matchAuthor(like.author)}</p>
                    <p>Date: {new Date(like.created_at).toLocaleString()}</p>
                  </li>
                ))
              ) : (
                <p>No likes found for this post.</p>
              )}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
