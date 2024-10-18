import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../loginStyles.css";
/**
 * This is a component for displaying create post page, will be redirected
 * to stream page after submiting
 *
 ********* USABLE, BUT MISSING FUNCTIONALITY ABOUT SNEDING DROPDOWN VALUE AND IMAGE FILE *********
 *
 */
export default function CreatePost() {
  const [postContent, setPostContent] = useState("");
  const [postContentType, setPostContentType] = useState("");
  const [postTitle, setPostTitle] = useState("");
  const [visibility, setVisibility] = useState("");
  const { authorId } = useParams();
  const authorIdInt = parseInt(authorId);
  const navigate = useNavigate();
  // handle submit the new post
  const createPost = async (event) => {
    event.preventDefault();
    const response = await fetch(`http://localhost:8000/service/post/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: postTitle,
        content: postContent,
        content_type: "text/markdown",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        visibility: "public",
        author: authorIdInt,
      }),
    })
      .then((responsess) => responsess.json())
      .then((data) => console.log(data));

    navigate(`/stream/${authorId}`);
  };
  return (
    <div className="create-post-page">
      <h2 className="page-subtitle">Welcome to the create post page!</h2>
      <form onSubmit={createPost}>
        <div>
          <input
            className="new-post-title"
            type="text"
            placeholder="Title"
            value={postTitle}
            onChange={(e) => setPostTitle(e.target.value)}
            required
          />
        </div>
        <textarea
          className="new-post-content"
          placeholder="Write your post content here..."
          value={postContent}
          onChange={(e) => setPostContent(e.target.value)}
          required
        />
        {/* <div className="new-post-content-type">
          <label for="con_type">Content Type:</label>
          <select
            className="content-type-dropdown"
            id="con_type"
            value={postContentType}
            onChange={(e) => setPostContentType(e.target.value)}
          >
            <option value="text/markdown">Markdown</option>
            <option value="image">JPEG</option>
          </select>
        </div> */}
        {/* <div className="new-post-visibility">
          <label for="visi">Visibility:</label>
          <select
            className="visibility-dropdown"
            id="visi"
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
          >
            <option value="public">Public</option>
            <option value="friend-only">Friend Only</option>
            <option value="unlisted">Unlisted</option>
          </select>
        </div> */}
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
