import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../editPost.css";

const EditPost = () => {
  const { postId } = useParams(); // Extract postId from URL
  const [postContent, setPostContent] = useState("");
  const [postContentType, setPostContentType] = useState("text/markdown");
  const [postTitle, setPostTitle] = useState("");
  const [authorID, setAuthorID] = useState("");
  const [visibility, setVisibility] = useState("public");
  const [selectedImage, setSelectedImage] = useState(null); // To handle image uploads
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPost = async () => {
      const response = await fetch(
        `http://localhost:8000/api/post/${postId}/`
      );
      if (response.ok) {
        const data = await response.json();
        setPostContent(data.content);
        setPostTitle(data.title);
        setAuthorID(data.author);
        setPostContentType(data.content_type);
        setVisibility(data.visibility);
      } else {
        alert("Failed to fetch post details");
      }
    };

    fetchPost();
  }, [postId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
  
    // Prepare form data for submission
    const formData = new FormData();
    formData.append("title", postTitle);
    formData.append("content_type", postContentType);
    formData.append("visibility", visibility);
    formData.append("author", authorID);
    formData.append("updated_at", new Date().toISOString());
  
    // Handle different content types
    if (postContentType === "text/markdown") {
      formData.append("content", postContent); // Save Markdown content
    } else if (postContentType === "image/jpeg" && selectedImage) {
      formData.append("content", ""); // Empty content for image uploads
      formData.append("image_content", selectedImage); // Save the image file
    }
  
    // Make PUT request to update the post
    const response = await fetch(
      `http://localhost:8000/api/post/${postId}/`,
      {
        method: "PUT",
        body: formData,
      }
    );
  
    if (response.ok) {
      alert("Post updated successfully");
      navigate(`/stream/${authorID}`);
    } else {
      alert("Failed to update post");
    }
  };
  

  const closeEdit = () => {
    navigate(`/stream/${authorID}`);
  };

  // delete a post
  const deletePost = async (event) => {
    event.preventDefault();
    const confirmDelete = window.confirm("Are you sure you want to delete this post?");
    if (confirmDelete) {
      const response = await fetch(
        `http://localhost:8000/api/post/${postId}/`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        alert("Post deleted successfully");
        navigate(`/stream/${authorID}`);
      } else {
        alert("Failed to delete post");
      }
    }
  };

  return (
    <div className="post-edit">
      <h2>Edit Post</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-div">
          <label>Title:</label>
          <input
            type="text"
            value={postTitle}
            onChange={(e) => setPostTitle(e.target.value)}
            required
          />
        </div>
        <div className="form-div">
          <label>Content Type:</label>
          <select
            value={postContentType}
            onChange={(e) => {
              setPostContentType(e.target.value);
              setSelectedImage(null); // Reset the selected image if content type changes
            }}
            required>
            <option value="text/markdown">Markdown</option>
            <option value="image/jpeg">JPEG</option>
          </select>
        </div>
        <div className="form-div">
          <label>Visibility:</label>
          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
            required
          >
            <option value="public">Public</option>
            <option value="friend-only">Friend Only</option>
            <option value="unlisted">Unlisted</option>
          </select>
        </div>
        <div className="form-div">
          <label>Content:</label>
          {postContentType === "text/markdown" ? (
            <textarea
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
              required
            />
          ) : (
            <input
              type="file"
              accept="image/jpeg"
              onChange={(e) => setSelectedImage(e.target.files[0])}
              required
            />
          )}
        </div>
        <div className="btn-container">
            <button className="save-btn" type="submit">Save Changes</button>
            <button className="cancel-btn" type="button" onClick={closeEdit}>Cancel</button>
            <button className="delete-btn" type="button" onClick={deletePost}>Delete</button>
        </div>
      </form>
    </div>
  );
};

export default EditPost;
