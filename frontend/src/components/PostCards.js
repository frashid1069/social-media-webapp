import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked";
import "../streamStyle.css";
import "../likes.css"
import Comment from "./Comment";
const apiUrl = process.env.REACT_APP_API_URL

export default function PostCards({ post, editable }) {
  const [authors, setAuthors] = useState([]);
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState([]);
  const [liked, setLiked] = useState(false);
  const [newCommentContent, setNewCommentContent] = useState("");
  const { authorId } = useParams();
  const authorIdInt = parseInt(authorId);

  const navigate = useNavigate();

  // Fetch the list of authors
  useEffect(() => {
    fetch(`${apiUrl}author/`)
      .then((response) => response.json())
      .then((data) => setAuthors(data));
  }, []);

  // Fetch the list of comments
  useEffect(() => {
    fetch(`${apiUrl}comment/`)
      .then((response) => response.json())
      .then((data) => setComments(data));
  }, []);

  // Function to fetch likes for the post
  const fetchLikes = () => {
    fetch(`${apiUrl}like/`)
      .then((response) => response.json())
      .then((data) => {
        const postLikes = data.filter((like) => like.post === post.id);
        setLikes(postLikes);

        // Check if the current author has already liked this post
        const userLiked = postLikes.some((like) => like.author === authorIdInt);
        setLiked(userLiked);
      })
  };

  // Fetch likes when the component mounts or when post ID or author ID changes
  useEffect(() => {
    fetchLikes();
  }, [post.id, authorIdInt]);


  // Match the corresponding author's name for the post
  const matchAuthor = (authorId) => {
    const author = authors.find((a) => a.id === authorId);
    return author ? author.display_name : "Unknown Author";
  };

  // Filter comments for the post
  const matchedComments = comments.filter((comment) => comment.post === post.id);

  // Navigate to the edit page for the post
  const goEdit = () => {
    if (editable) {
      navigate(`/stream/${post.author}/${post.id}/edit`);
    }
  };

  // Navigate to the corresponding profile page
  const goProfile = () => {
    navigate(`/stream/${post.author}/profile`);
  };

  // Navigate to the likes page
  const goToLikesPage = () => {
    navigate(`/stream/${post.author}/${post.id}/likes`);
  };

  // Handle comment submission
  const submitComment = async (event) => {
    event.preventDefault();
    const response = await fetch(`${apiUrl}comment/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: newCommentContent,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        author: authorIdInt,
        post: post.id,
      }),
    });

    if (response.ok) {
      setNewCommentContent("");
      // Optionally, refresh comments list here
    }
  };

  // Convert Markdown content to HTML safely
  const getMarkdownContent = () => {
    return { __html: marked(post.content || "") };
  };

  // Construct a proper URL for the image content
  const imageURL = post.image_content
    ? post.image_content.startsWith("http")
      ? post.image_content // If the URL is already absolute, use it as-is
      : `http://localhost:8000${post.image_content}`
    : null; // Handle the case where image_content is null or undefined

  console.log("Image URL:", imageURL);

  // function for liking and un-liking a post
  const handleLike = async () => {
    // if (liked) {
    //   // Find the like object for this author and post to delete
    //   const likeToDelete = likes.find((like) => like.author === authorIdInt && like.post === post.id);
    
    //   if (likeToDelete) {
    //     // Send DELETE request to delete the specific like
    //     await fetch(`${apiUrl}like/${likeToDelete.id}/`, {
    //       method: "DELETE",
    //       headers: {
    //         "Content-Type": "application/json",
    //       },
    //     });
    //     setLiked(false);
    //     // Refresh likes to update count
    //     fetchLikes();
    //   }
    // } 
    if (!liked){
      // Like the post (send POST request)
      const response = await fetch(`${apiUrl}like/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          author: authorIdInt,
          post: post.id,
        }),
      });

      if (response.ok) {
        setLiked(true);
        // Refresh likes to update count
        fetchLikes();
      }
    }
  }

  return (
    <div key={post.id} className="post-card" onClick={goEdit}>
      <h3 className="post-card-title">{post.title}</h3>
      <div className="btn-container">
        <button className="post-card-author" onClick={goProfile}>
          {matchAuthor(post.author)}
        </button>
        <button className="btn-like" onClick={handleLike}>
            {liked ? "Liked" : "Like"} ({likes.length})
        </button>
        <button className="btn-show-likes" onClick={goToLikesPage}>
          Show Likes
        </button>
      </div>
      {/* Render the Markdown content as HTML */}
      <div
        className="post-card-content"
        dangerouslySetInnerHTML={getMarkdownContent()}
      />
      {/* Render the image if it's available */}
      {imageURL && (
        <div className="post-card-image">
          <img src={imageURL} alt="Post" className="post-image" />
        </div>
      )}
      <p className="post-card-update-date">Updated at: {new Date(post.updated_at).toLocaleString()}</p>
      
      <div className="comment-grid">
        <h5 className="comment-title">Comments:</h5>
        {matchedComments.map((comment) => (
          <Comment comment={comment} key={comment.id} />
        ))}
      </div>
      <form onSubmit={submitComment}>
        <textarea
          placeholder="Write your comment here..."
          value={newCommentContent}
          onChange={(e) => setNewCommentContent(e.target.value)}
          required
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}