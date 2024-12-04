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
    <div class="dialogbox">
      <p className="comment-content"></p>
      <div class="body">
        <span class="tip tip-left"></span>
        <div class="message">
          <span>{comment.author.displayName}: {comment.comment}</span>
        </div>
      </div>
    </div>
  );
}
