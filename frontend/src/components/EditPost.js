import React, { useState, useEffect } from 'react';
import './EditPost.css';

const EditPost = ({ postId, onClose }) => {
  const [postContent, setPostContent] = useState('');
  const [postTitle, setPostTitle] = useState('');
//   const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch the existing post details to prefill the form
    const fetchPost = async () => {
        // setIsLoading(true);
        const response = await fetch(`/posts/${postId}/`);
        if (response.ok) {
            const data = await response.json();
            setPostContent(data.content);
            setPostTitle(data.title);
        } else {
            console.error('Failed to fetch post details');
        }
        // setIsLoading(false);
    };

    fetchPost();
  }, [postId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const response = await fetch(`/api/post/${postId}/edit/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: postContent, title: postTitle }),
    });

    if (response.ok) {
      onClose(); // Close the editing modal
    } else {
      console.error('Failed to update post');
    }
  };

//   if (isLoading) {
//     return <div>Loading...</div>; // Display a loading message while fetching data
//   }

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
          <label>Content:</label>
          <textarea
            value={postContent}
            onChange={(e) => setPostContent(e.target.value)}
            required
          />
        </div>
        <button type="submit">Save Changes</button>
        <button type="button" onClick={onClose}>Cancel</button>
      </form>
    </div>
  );
};

export default EditPost;
