import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked";
import "../streamStyle.css";
import "../likes.css";
import Comment from "./Comment";
import { cusFetch } from './Login';
const apiUrl = process.env.REACT_APP_API_URL;

export default function PostCards({ post, editable, isRepost, repostedBy, onClick, isFriend }) {
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState([]);
  const [liked, setLiked] = useState(false);
  const [newCommentContent, setNewCommentContent] = useState("");
  const { AUTHOR_SERIAL, POST_SERIAL } = useParams();
  const authorIdInt = parseInt(AUTHOR_SERIAL);
  const [hasReposted, setHasReposted] = useState(false);
  const token = localStorage.getItem('token'); 
  const [reposted_by, setRepostedBy] = useState("");

  const navigate = useNavigate();

  
  function getAuthorId(url) {
    const authorMatch = url.match(/authors\/(\d+)/);
    return authorMatch ? authorMatch[1] : null;       // Returns author ID or null if not found
  }
  
  function getPostId(url) {
    const postMatch = url.match(/posts\/(\d+)/);
    return postMatch ? postMatch[1] : null;       // Returns post ID or null if not found
  }
  // Fetch repostedBy author info if post is a repost
  useEffect(() => {
    if (isRepost) {
      fetch(`${apiUrl}author/${repostedBy}/`, {
        method: "GET",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
        }
      })
      .then((response) => response.json())
      .then((data) => setRepostedBy(data.display_name));
    }
  }, [isRepost, repostedBy, token]);


  // Fetch likes for the post
  const cusFetchLikes = () => {
    cusFetch(`${apiUrl}authors/${AUTHOR_SERIAL}/posts/${POST_SERIAL}/likes/`)
      .then((response) => response.json())
      .then((data) => {
        const postLikes = [];
        if (data.src.length > 0) {
          postLikes = [...data.src]
          setLikes(postLikes);
          const userLiked = postLikes.some((like) => like.author.id === `${apiUrl}authors/${AUTHOR_SERIAL}`);
          setLiked(userLiked);
        }
      });
  };

  useEffect(() => {
    cusFetchLikes();
  }, [hasReposted]);


  // get the author's display name for the post
  const displayAuthor = (post) => {
    const author = post.author
    return author.displayName
  };

  // get comments for the post
  const matchedComments = post.comments;


  const goProfile = () => {
    navigate(`/stream/${getAuthorId(post.id)}/profile`);
  };


  const submitComment = async (event) => {
    event.preventDefault();
    const response = await cusFetch(`${apiUrl}comment/`, {
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
      cusFetchComments();
    }
  };

  const getMarkdownContent = () => {
    // From https://www.w3schools.com/jsref/jsref_startswith.asp 
    if(post.content.startsWith("/")) {
      return { __html: marked("") };
    }
    return { __html: marked(post.content || "") };
  };

  const imageURL = post.image_url || null;
  const myProfile = cusFetch(`${apiUrl}authors/${authorIdInt}/`).then((response) => response.json())

  const handleLike = async () => {
    if (!liked) {
      const likeObject = {
        author: myProfile,
        object: post,
      };

      const response = await cusFetch(`${apiUrl}authors/${AUTHOR_SERIAL}/inbox`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(likeObject),
      });

      if (response.ok) {
        setLiked(true);
        cusFetchLikes();
      }
    }
  };

  const handleShare = async () => {
    if (post.visibility === "public") {
      try {
        const response = await cusFetch(`${apiUrl}post/${post.id}/share/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            token: `${localStorage.getItem("token")}`,
          },
        });
        if (response.ok) {
          alert("Post shared successfully!");
        } else {
          alert("Failed to share post.");
        }
      } catch (error) {
        console.error("Error sharing post:", error);
      }
    }
  };

  useEffect(() => {
    const fetchReposts = async () => {
      const response = await fetch(`${apiUrl}repost/?post=${post.id}&reposted_by=${authorIdInt}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "token": `${token}`,
        }
      });
      const data = await response.json();
      if (data.length > 0) {
        setHasReposted(true);
      }
    };
    fetchReposts();
  }, [post.id, authorIdInt, token]);

  const handleRepost = async () => {
    const response = await cusFetch(`${apiUrl}repost/`, {
      method: "POST",
      headers: {
        "token": `${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        reposted_by: authorIdInt,
        post: post.id,
      }),
    });

    if (response.ok) {
      setHasReposted(!hasReposted);
    }
  };



  return (
    <div key={post.id} className="post-card" onClick={onClick} style={{ cursor: "pointer" }}>
      <h3 className="post-card-title">{post.title}</h3>
      <div className="btn-container">
        <button className="post-card-author" onClick={(e) => { e.stopPropagation(); goProfile(); }}>
          {displayAuthor(post)}
        </button>
        <button className="btn-like" onClick={(e) => { e.stopPropagation(); handleLike(); }}>
          {liked ? "Liked" : "Like"} ({likes.length})
        </button>
        {post.visibility === "public" && (
          <button className="btn-share" onClick={(e) => { e.stopPropagation(); handleShare(); }}>
            Share
          </button>
        )}
        {!isRepost && !hasReposted && (
          <button className="btn-repost" onClick={(e) => { e.stopPropagation(); handleRepost(); }}>
            Repost
          </button>
        )}
      </div>
      <div className="post-card-content" dangerouslySetInnerHTML={getMarkdownContent()} />
      {imageURL && (
        <div className="post-card-image">
          <img src={imageURL} alt="Post" className="post-image" />
        </div>
      )}
      <p className="post-card-update-date">Updated at: {new Date(post.updated_at).toLocaleString()}</p>
      <div className="comment-grid" onClick={(e) => e.stopPropagation()}>
        <h5 className="comment-title">Comments:</h5>
        {matchedComments.map((comment) => (
          <Comment comment={comment} key={comment.id} />
        ))}
      </div>
      <form onSubmit={submitComment} onClick={(e) => e.stopPropagation()}>
        <textarea
          placeholder="Write your comment here..."
          value={newCommentContent}
          onChange={(e) => setNewCommentContent(e.target.value)}
          required
        />
        <button type="submit">Send</button>
      </form>
      {isRepost && <p><strong>Reposted by {reposted_by}</strong></p>}
    </div>
  );
}
