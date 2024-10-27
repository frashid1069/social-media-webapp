import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const apiUrl = process.env.REACT_APP_API_URL;

export default function PostDetail() {
    const { postId } = useParams();
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPost = async () => {
            try {
                const response = await fetch(`${apiUrl}/post/${postId}/`);
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
    }, [postId]);

    if (loading) return <p>Loading post...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="post-detail">
            {post ? (
                <>
                    <h2>{post.title}</h2>
                    <p>Author: {post.author.display_name || "Unknown Author"}</p>
                    <div
                        dangerouslySetInnerHTML={{ __html: post.content }}
                    ></div>
                    {post.image_content && (
                        <img
                            src={post.image_content}
                            alt={post.title}
                            style={{ maxWidth: "100%", height: "auto" }}
                        />
                    )}
                    <p>Posted on: {new Date(post.created_at).toLocaleString()}</p>
                    <p>Last updated: {new Date(post.updated_at).toLocaleString()}</p>
                </>
            ) : (
                <p>Post not found.</p>
            )}
        </div>
    );
}
