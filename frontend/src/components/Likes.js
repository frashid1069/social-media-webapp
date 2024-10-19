import React from "react";
import "../streamStyle.css";

export default function LikeModal({ likes, closeModal }) {
  return (
    <div className="like-modal">
      <div className="like-modal-content">
        <h2>Likes</h2>
        <button className="close-modal-btn" onClick={closeModal}>
          Close
        </button>
        <ul>
          {likes.length > 0 ? (
            likes.map((like) => (
              <li key={like.id}>
                <p>Liked by: {like.author}</p>
                <p>Date: {new Date(like.created_at).toLocaleString()}</p>
              </li>
            ))
          ) : (
            <p>No likes found for this post.</p>
          )}
        </ul>
      </div>
    </div>
  );
}
