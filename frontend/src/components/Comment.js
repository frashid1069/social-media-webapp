import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import "../streamStyle_Sukh.css";
/**
 * This is a component for displaying comments for the corresponded post
 * @param comment: single comment object
 *
 */
export default function Comment({ comment }) {
  const [authors, setAuthors] = useState([]);
  const navigate = useNavigate();
  // get the author list
  useEffect(() => {
    fetch("http://localhost:8000/service/author/")
      .then((response) => response.json())
      .then((data) => setAuthors(data));
  }, []);
  // find the corresponding author's name for the comment
  const matchAuthor = () => {
    for (const author of authors) {
      if (author.id === comment.author) {
        return author.display_name;
      }
    }
  };
  return (
    <div key={comment.id} className="comment">
      <p className="comment-content">{comment.content}</p>
      <p className="comment-author">{matchAuthor()}</p>
    </div>
  );
}
