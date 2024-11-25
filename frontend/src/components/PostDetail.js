import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../editPost.css";
import { cusFetch } from "./Login";

const apiUrl = process.env.REACT_APP_API_URL;

export default function PostDetail() {
    // const { authorId, postId } = useParams();
    const { authorFqid, postFqid } = useParams();
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const token = localStorage.getItem("token");
    const navigate = useNavigate();
    const decodedAuthorFqid = decodeURIComponent(authorFqid);
    const decodedPostFqid = decodeURIComponent(postFqid);

    useEffect(() => {
        const fetchPost = async () => {
            try {
                const response = await cusFetch(`${apiUrl}posts/${decodedPostFqid}`, {
                    method: "GET",
                });
                if (response.ok) {
                    const data = await response.json();
                    setPost(data);
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
    }, [decodedAuthorFqid, decodedPostFqid]);

    const deletePost = async (event) => {
        event.preventDefault();
        const confirmDelete = window.confirm("Are you sure you want to delete this post?");
        if (confirmDelete) {
            const response = await fetch(`${decodedPostFqid}`, {
                method: "DELETE",
                headers: {
                    "token": token, // Add token for DELETE request
                },
            });

            if (response.ok) {
                alert("Post deleted successfully");
                navigate(`/stream/${decodedAuthorFqid}`);
            } else {
                alert("Failed to delete post");
            }
        }
    };

    const goEditPost = () => {
        navigate(`/stream/${authorFqid}/${postFqid}/edit`);
    };

    const goToStream = () => {
        navigate(`/stream/${authorFqid}`);
    };

    if (loading) return <p>Loading post...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="post-detail">
            {post ? (
                <>
                    <h2>{post.title}</h2>
                    <p>Author: {post.author ? post.author.displayName : "Unknown Author"}</p>

                    {post.contentType === "image/jpeg" ? (
                        <img
                            src={`data:image/jpeg;base64,${post.content}`}
                            alt={post.title}
                            style={{ maxWidth: "100%", height: "auto" }}
                        />
                    ) : (
                        <div>{post.content}</div>
                    )}
                    {/* {post.image_content && (
                        <img
                            src={post.image_content}
                            alt={post.title}
                            style={{ maxWidth: "100%", height: "auto" }}
                        />
                    )} */}
                    <p>Posted on: {new Date(post.published).toLocaleString()}</p>
                    {/* <p>Last updated: {new Date(post.updated_at).toLocaleString()}</p> */}
                    <div className="btn-container">
                        <button className="edit-btn" type="submit" onClick={goEditPost}>Edit</button>
                        <button className="delete-btn" type="button" onClick={deletePost}>Delete</button>
                        <button className="cancel-btn" type="button" onClick={goToStream}>Go Back</button>
                    </div>
                </>
            ) : (
                <p>Post not found.</p>
            )}
        </div>
    );
}
