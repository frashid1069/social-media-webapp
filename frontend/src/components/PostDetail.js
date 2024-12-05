import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { cusFetch } from "./Login";
import Header from "./Header";
import { getAdapter } from "axios";

const apiUrl = process.env.REACT_APP_API_URL;

export default function PostDetail() {
    // const { authorId, postId } = useParams();
    const { postFqid } = useParams();
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isCurrentAuthor, setIsCurrentAuthor] = useState(false);
    const token = localStorage.getItem("token");
    const navigate = useNavigate();
    const currentAuthorId = localStorage.getItem("currentAuthorId");
    const encodedCurrentAuthorId = encodeURIComponent(currentAuthorId);
    const encodedPostFqid = encodeURIComponent(postFqid);
    const subtitle = "Post Detail";

    useEffect(() => {
        const fetchPost = async () => {
            try {
                const response = await cusFetch(`${apiUrl}posts/${postFqid}`, {
                    method: "GET",
                });
                if (response.ok) {
                    const data = await response.json();
                    setPost(data);
                    setIsCurrentAuthor(data.author.id === currentAuthorId);
                } else {
                    setError("Failed to fetch post. Please check if the post exists.");
                }
            } catch (error) {
                setError("An error occurred while loading the post.");
            } finally {
                setLoading(false);
            }
        };

        fetchPost();
    }, [postFqid]);

    const deletePost = async (event) => {
        event.preventDefault();
        const confirmDelete = window.confirm("Are you sure you want to delete this post?");
        if (confirmDelete) {
            const response = await fetch(`${postFqid}`, {
                method: "DELETE",
                headers: {
                    "token": token, // Add token for DELETE request
                },
            });

            if (response.ok) {
                alert("Post deleted successfully");
                navigate(`/stream/${encodedCurrentAuthorId}`);
            } else {
                alert("Failed to delete post");
            }
        }
    };

    const goEditPost = () => {
        navigate(`/posts/${encodedPostFqid}/edit`);
    };

    const goToStream = () => {
        navigate(`/stream/${encodedCurrentAuthorId}`);
    };

    if (loading) return <p>Loading post...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="post-detail">
            <Header subtitle={subtitle} />
            {post ? (
                <>
                    <h2>{post.title}</h2>
                    <p>Author: {post.author ? post.author.displayName : "Unknown Author"}</p>

                    {post.contentType.startsWith("image/") ? (
                        <img
                            src={`data:${post.contentType},${post.content}`}
                            alt={post.title}
                            style={{ maxWidth: "100%", height: "auto" }}
                        />
                    ) : (
                        <div>{post.content}</div>
                    )}
                    <p>Posted on: {new Date(post.published).toLocaleString()}</p>
                    {/* <p>Last updated: {new Date(post.updated_at).toLocaleString()}</p> */}
                    {isCurrentAuthor ? 
                        <div className="btn-container">
                            <button className="edit-btn" type="submit" onClick={goEditPost}>Edit</button>
                            <button className="delete-btn" type="button" onClick={deletePost}>Delete</button>
                            <button className="cancel-btn" type="button" onClick={goToStream}>Go Back</button>
                        </div>
                        : 
                        <div className="btn-container">
                            <button className="cancel-btn" type="button" onClick={goToStream}>Go Back</button>
                        </div>
                    }
                    
                </>
            ) : (
                <p>Post not found.</p>
            )}
        </div>
    );
}
