/**
 * Acknowledgment of Assistance from ChatGPT:
For this project, I (sukh) sought assistance from OpenAI's ChatGPT to 
help clarify and explain the user story related to CommonMark and 
image links in posts. Specifically, ChatGPT provided a detailed explanation 
of how to approach the user story thay meets the requirements of the user story. No code was directly copied from ChatGPT, 
and I fully understand all the code and its functionality.
 */
import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked"; // Import the Markdown library
import "../loginStyles.css";
const apiUrl = process.env.REACT_APP_API_URL

export default function CreatePost() {
  const [postContent, setPostContent] = useState(""); // For Markdown content
  const [postTitle, setPostTitle] = useState("");
  const [visibility, setVisibility] = useState("public");
  const [selectedImage, setSelectedImage] = useState(null); // To handle image uploads

  const { authorId } = useParams();
  const navigate = useNavigate();

  const createPost = async (event) => {
    event.preventDefault();

    // Create FormData to include file (if any)
    const formData = new FormData();
    formData.append("title", postTitle);
    formData.append("content", postContent); // Markdown content
    formData.append("content_type", "text/markdown"); // Setting default type to Markdown
    formData.append("visibility", visibility);
    formData.append("author", parseInt(authorId));
    formData.append("created_at", new Date().toISOString());
    formData.append("updated_at", new Date().toISOString());

    // Append the image file if an image is selected
    if (selectedImage) {
      formData.append("image_content", selectedImage);
    }

    try {
      const response = await fetch(`${apiUrl}post/`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        navigate(`/stream/${authorId}`);
      } else {
        alert("Failed to create a post");
      }
    } catch (error) {
      console.error("Error creating post:", error);
      alert("Error creating post");
    }
  };

  // Handle cancel action
  const cancelPostCreation = () => {
    navigate(`/stream/${authorId}`);
  };

  // Convert the Markdown content to HTML using "marked"
  const getMarkdownPreview = () => {
    return { __html: marked(postContent) };
  };

  return (
    <div className="create-post-page">
      <h2 className="page-subtitle">Create a New Post</h2>
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
          placeholder="Write your post content in Markdown..."
          value={postContent}
          onChange={(e) => setPostContent(e.target.value)}
        />
        {/* Markdown Preview */}
        <div className="markdown-preview">
          <h3>Preview</h3>
          <div className="preview"
            dangerouslySetInnerHTML={getMarkdownPreview()} // Render the Markdown content as HTML 
          ></div>
        </div>
        <div>
          <label htmlFor="image-upload">Upload an image (optional):</label>
          <input
            id="image-upload"
            type="file"
            accept="image/jpeg"
            onChange={(e) => setSelectedImage(e.target.files[0])}
          />
        </div>
        <div className="new-post-visibility">
          <label htmlFor="visi">Visibility:</label>
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
        </div>
        <div className="button-container">
          <button type="submit">Send</button>
          {/* Cancel button */}
          <button type="button" onClick={cancelPostCreation} className="cancel-btn">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
