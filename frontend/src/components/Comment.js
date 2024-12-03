import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { cusFetch } from './Login';
const apiUrl = process.env.REACT_APP_API_URL
/**
 * This is a component for displaying comments for the corresponded post
 * @param comment: single comment object
 *
 */
export default function Comment({ comment }) {

  return (
    <div key={comment.id} className="comment">
      <p className="comment-content">{comment.comment}</p>
      <p className="comment-author">{comment.author.displayName}</p>
    </div>
  );
}
