import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../editPost.css";

const apiUrl = process.env.REACT_APP_API_URL;

const EditPost = () => {
    const { postId } = useParams();
    const [postContent, setPostContent] = useState("");
    const [postContentType, setPostContentType] = useState("text/markdown");
    const [postTitle, setPostTitle] = useState("");
    const [authorID, setAuthorID] = useState("");
    const [visibility, setVisibility] = useState("public");
    const [selectedImage, setSelectedImage] = useState(null);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const token = localStorage.getItem("token");

    useEffect(() => {
        const fetchPost = async () => {
            try {
                const response = await fetch(`${apiUrl}post/${postId}/`, {
                    headers: {
                        "Content-Type": "application/json",
                        "token": token, // Add token to the request headers
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setPostContent(data.content);
                    setPostTitle(data.title);
                    setAuthorID(data.author);
                    setPostContentType(data.content_type);
                    setVisibility(data.visibility);
                } else {
                    setError("Failed to fetch post details. Please check if the post exists or if you have permission.");
                }
            } catch (error) {
                setError("An error occurred while fetching the post details.");
            }
        };

        fetchPost();
    }, [postId, token]);

    const handleSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append("title", postTitle);
        formData.append("content_type", postContentType);
        formData.append("visibility", visibility);
        formData.append("author", authorID);
        formData.append("updated_at", new Date().toISOString());

        if (postContentType === "text/markdown") {
            formData.append("content", postContent);
        } else if (postContentType === "image/jpeg" && selectedImage) {
            formData.append("content", "");
            formData.append("image_content", selectedImage);
        }

        const response = await fetch(`${apiUrl}post/${postId}/`, {
            method: "PUT",
            headers: {
                "token": token, // Add token to the request headers for PUT
            },
            body: formData,
        });

        if (response.ok) {
            alert("Post updated successfully");
            navigate(`/stream/${authorID}`);
        } else {
            alert("Failed to update post. Please try again.");
        }
    };

    const closeEdit = () => {
        navigate(`/stream/${authorID}`);
    };

    const deletePost = async (event) => {
        event.preventDefault();
        const confirmDelete = window.confirm("Are you sure you want to delete this post?");
        if (confirmDelete) {
            const response = await fetch(`${apiUrl}post/${postId}/`, {
                method: "DELETE",
                headers: {
                    "token": token, // Add token for DELETE request
                },
            });

            if (response.ok) {
                alert("Post deleted successfully");
                navigate(`/stream/${authorID}`);
            } else {
                alert("Failed to delete post");
            }
        }
    };

    if (error) {
        return <p>{error}</p>;
    }

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
                            setSelectedImage(null);
                        }}
                        required
                    >
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
