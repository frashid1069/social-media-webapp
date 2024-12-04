import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { cusFetch } from './Login';
const apiUrl = process.env.REACT_APP_API_URL

export default function Likes() {
  const { authorId, postId } = useParams();

  // Initialize state variables
  const [likes, setLikes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authors, setAuthors] = useState([]);
  const navigate = useNavigate(); // For navigation

  useEffect(() => {
    // cusFetch likes for the specific post
    cusFetch(`${apiUrl}like/?post=${postId}`)
      .then((response) => response.json())
      .then((data) => {
        setLikes(data); // Set filtered likes based on postId
        setLoading(false); // Turn off loading
      })
      .catch((error) => console.error("Error cusFetching likes:", error));
  }, [postId]); // Dependency array ensures this runs when postId changes

  useEffect(() => {
    // cusFetch authors for name matching
    cusFetch(`${apiUrl}author/`)
      .then((response) => response.json())
      .then((data) => setAuthors(data))
      .catch((error) => console.error("Error cusFetching authors:", error));
  }, []); // Empty dependency array ensures this runs only once on mount

  // Match the author's display name by their ID
  const matchAuthor = (authorId) => {
    const author = authors.find((a) => a.id === authorId);
    return author ? author.display_name : "Unknown Author";
  };

  // Function to handle the "Back" button click
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
        {/* Display a loading message while likes data is being cusFetched */}
        {loading ? (
          <p>Loading likes...</p>
        ) : (
          <>{/* Show the total number of likes once the data has loaded */}
            <p>Total Likes: {likes.length}</p>
            <ul>
              {/* If there are likes, display each like with information */}
              {likes.length > 0 ? (
                likes.map((like) => (
                  <li key={like.id}>
                    <p>Liked by: {matchAuthor(like.author)}</p>
                    <p>Date: {new Date(like.created_at).toLocaleString()}</p>
                  </li>
                ))
              ) : (
                // If no likes are found
                <p>No likes found for this post.</p>
              )}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
