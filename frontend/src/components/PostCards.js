import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked";
import "../streamStyle.css";
import "../likes.css"
import Comment from "./Comment";
import LikeModal from "./Likes";

export default function PostCards({ post, editable }) {
  const [authors, setAuthors] = useState([]);
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState([]);
  const [liked, setLiked] = useState(false);
  const [newCommentContent, setNewCommentContent] = useState("");
  const [showLikeModal, setShowLikeModal] = useState(false);
  const { authorId } = useParams();
  const authorIdInt = parseInt(authorId);

  const navigate = useNavigate();

  // Fetch the list of authors
  useEffect(() => {
    fetch("http://localhost:8000/service/author/")
      .then((response) => response.json())
      .then((data) => setAuthors(data));
  }, []);

  // Fetch the list of comments
  useEffect(() => {
    fetch("http://localhost:8000/service/comment/")
      .then((response) => response.json())
      .then((data) => setComments(data));
  }, []);

  // get the likes for the post
  useEffect(() => {
    // Fetch likes for this post and check if the current author has liked it
    fetch(`http://localhost:8000/service/author/${authorId}/posts/${post.id}/likes`)
      .then((response) => response.json())
      .then((data) => {
        setLikes(data);
        const userLiked = data.some((like) => like.author === authorIdInt);
        setLiked(userLiked);
      });
  }, [post.id, authorIdInt]);


  // Handle opening and closing the modal
  const toggleLikeModal = () => {
    setShowLikeModal(!showLikeModal);
  };

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

  // Handle comment submission
  const submitComment = async (event) => {
    event.preventDefault();
    const response = await fetch(`http://localhost:8000/service/comment/`, {
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
    if (liked) {
      // Unlike the post (send DELETE request)
      await fetch(`http://localhost:8000/service/author/${authorId}/posts/${post.id}/likes`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });
      setLiked(false);
    } 
    else {
      // Like the post (send POST request)
      await fetch(`http://localhost:8000/service/author/${authorId}/posts/${post.id}/likes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          author: authorIdInt,
          post: post.id,
        }),
      });
      setLiked(true);
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
            {liked ? "Unlike" : "Like"} ({likes.length})
        </button>
        <button className="btn-show-likes" onClick={toggleLikeModal}>
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
      
      {/* Show list of likes for the post */}
      {showLikeModal && (
        <LikeModal likes={likes} closeModal={toggleLikeModal} />
      )}
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