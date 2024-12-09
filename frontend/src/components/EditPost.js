import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { cusFetch } from "./Login";
import Header from "./Header";

const EditPost = () => {
    const { postFqid } = useParams();
    const [postContent, setPostContent] = useState("");
    const [postContentType, setPostContentType] = useState("text/markdown");
    const [postTitle, setPostTitle] = useState("");
    const [postDescription, setPostDescription] = useState("");
    const [visibility, setVisibility] = useState("public");
    const [selectedImage, setSelectedImage] = useState(null);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const token = localStorage.getItem("token");
    const apiUrl = process.env.REACT_APP_API_URL

    const currentAuthorId = localStorage.getItem("currentAuthorId")
    const encodedAuthorFqid = encodeURIComponent(currentAuthorId);
    const subtitle = "Post Edition";

    useEffect(() => {
        const fetchPost = async () => {
            try {
                const response = await cusFetch(`${postFqid}`, {
                    method: "GET",
                });

                if (response.ok) {
                    const data = await response.json();
                    setPostContent(data.content);
                    setPostTitle(data.title);
                    setPostDescription(data.description)
                    setPostContentType(data.contentType);
                    setVisibility(data.visibility);
                } else {
                    setError("Failed to fetch post details. Please check if the post exists or if you have permission.");
                }
            } catch (error) {
                setError("An error occurred while fetching the post details.");
            }
        };

        fetchPost();
    }, [postFqid]);

    const handleSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append("title", postTitle);
        formData.append("description", postDescription);
        formData.append("contentType", postContentType);
        formData.append("visibility", visibility);

        if (postContentType === "text/markdown") {
            formData.append("content", postContent);
        }
        else if (postContentType === "image/jpeg" && selectedImage) {
            formData.append("content", selectedImage);
        }
        const response = await fetch(`${postFqid}`, {
            method: "PUT",
            headers: {
                "token": token,
            },
            body: formData,
        });
        console.log(formData)
        if (response.ok) {
            alert("Post updated successfully");
            navigate(`/stream/${encodedAuthorFqid}`);
        } else {
            alert("Failed to update post. Please try again.");
        }
    };

    const goToStream = () => {
        navigate(`/stream/${encodedAuthorFqid}`);
    };

    const deletePost = async (event) => {
        event.preventDefault();
        const confirmDelete = window.confirm("Are you sure you want to delete this post?");
        if (confirmDelete) {
            const response = await cusFetch(`${postFqid}`, {
                method: "DELETE",
            });

            if (response.ok) {
                alert("Post deleted successfully");
                navigate(`/stream/${encodedAuthorFqid}`);
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
            <Header subtitle={subtitle} />
            <div id="post-edit-window">
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
                        <label>Description:</label>
                        <input
                            type="text"
                            value={postDescription}
                            onChange={(e) => setPostDescription(e.target.value)}
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
                            {/* <option value="text/plain">UTF-8</option>
                        <option value="image/jpeg;base64">JPEG</option>
                        <option value="application/base64">JPEG/PNG</option>
                        <option value="image/png;base64">PNG</option> */}
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
                            <option value="friends">Friend Only</option>
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
                            />)
                        }
                    </div>
                    <div className="btn-container">
                        <button className="save-btn" type="submit">Save Changes</button>
                        <button className="cancel-btn" type="button" onClick={goToStream}>Cancel</button>
                        <button className="delete-btn" type="button" onClick={deletePost}>Delete</button>
                    </div>
                </form>
            </div>

        </div>
    );
};

export default EditPost;
