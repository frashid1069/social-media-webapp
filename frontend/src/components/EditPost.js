import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../editPost.css";
/**
 * This is a component for displaying edit page for the corresponded post, the edit
 * page can update and delete a post
 *
 */
const EditPost = () => {
  const { postId } = useParams(); // Extract postId from URL
  const [postContent, setPostContent] = useState("");
  const [postContentType, setPostContentType] = useState("");
  const [postTitle, setPostTitle] = useState("");
  const [authorID, setAuthorID] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPost = async () => {
      const response = await fetch(
        `http://localhost:8000/service/post/${postId}`
      );
      if (response.ok) {
        const data = await response.json();
        setPostContent(data.content);
        setPostTitle(data.title);
        setAuthorID(data.author);
        setPostContentType(data.content_type);
      } else {
        alert("Failed to fetch post details");
      }
    };

    fetchPost();
  }, [postId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const response = await fetch(
      `http://localhost:8000/service/post/${postId}/`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          author: authorID,
          content_type: postContentType,
          content: postContent, // The content is saved as Markdown
          title: postTitle,
          updated_at: new Date().toISOString(), // Update the timestamp
        }),
      }
    )
      .then((responsess) => responsess.json())
      .then((data) => console.log(data));

    navigate(`/stream/${authorID}`);
  };

  const closeEdit = () => {
    window.location.href = "/posts/"; // Redirect
  };

  // delete a post
  const deletePost = async (event) => {
    event.preventDefault();
    const response = await fetch(
      `http://localhost:8000/service/post/${postId}/`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          author: authorID,
          content_type: postContentType,
          content: postContent, // The content is saved as Markdown
          title: postTitle,
          is_deleted: true,
          updated_at: new Date().toISOString(), // Update the timestamp
        }),
      }
    )
      .then((responsess) => responsess.json())
      .then((data) => console.log(data));

    navigate(`/stream/${authorID}`);
  };

  return (
    <div className="post-edit">
      <h2>Edit Post</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label>
          <input
            type="text"
            value={postTitle}
            onChange={(e) => setPostTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Content Type:</label>
          <input
            type="text"
            value={postContentType}
            onChange={(e) => setPostContentType(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Content:</label>
          <textarea
            value={postContent}
            onChange={(e) => setPostContent(e.target.value)}
            required
          />
        </div>
        <button type="submit">Save Changes</button>
        <button type="button" onClick={closeEdit}>
          Cancel
        </button>
      </form>
      <button onClick={deletePost}>Delete</button>
    </div>
  );
};

export default EditPost;
