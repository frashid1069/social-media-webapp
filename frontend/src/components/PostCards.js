import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked";
import "../streamStyle.css";
import "../likes.css";
import Comment from "./Comment";
import { cusFetch } from './Login';
import Stream from "./Stream";
const apiUrl = process.env.REACT_APP_API_URL;

export default function PostCards({ post, currenAuthor, onClick }) {
  const [likes, setLikes] = useState([]);
  const [liked, setLiked] = useState(false);
  const [newCommentContent, setNewCommentContent] = useState("");
  const currentAuthorId = Stream.currentAuthorId;

  const authorId = getAuthorId(post.id)
  const postId = getPostId(post.id)

  const navigate = useNavigate();


  function getAuthorId(url) {
    const authorMatch = url.match(/authors\/(\d+)/);
    return authorMatch ? authorMatch[1] : null;       // Returns author ID or null if not found
  }

  function getPostId(url) {
    const postMatch = url.match(/posts\/(\d+)/);
    return postMatch ? postMatch[1] : null;       // Returns post ID or null if not found
  }



  // Fetch likes for the post
  const cusFetchLikes = () => {
    cusFetch(`${apiUrl}authors/${authorId}/posts/${postId}/likes`)
      .then((response) => response.json())
      .then((data) => {
        let postLikes = [];
        if (data.src.length > 0) {
          postLikes = [...data.src]
          setLikes(postLikes);
          const userLiked = postLikes.some((like) => like.author.id === `${apiUrl}authors/${authorId}`);
          setLiked(userLiked);
        }
      });
  };

  useEffect(() => {
    cusFetchLikes();
  }, []);


  // get the author's display name for the post
  const displayAuthor = (post) => {
    const author = post.author
    return author.displayName
  };

  // get comments for the post
  const matchedComments = post.comments.src;


  const goProfile = () => {
    navigate(`/stream/${authorId}/profile`);
  };


  const submitComment = async (event) => {
    event.preventDefault();
    const response = await cusFetch(`${apiUrl}authors/${authorId}/inbox`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: "comment",
        comment: newCommentContent,
        contentType: "text/markdown",
        post: post.id,
        author: currenAuthor
      }),
    });

    if (response.ok) {
      setNewCommentContent("");
      // cusFetchComments();
    }
  };

  const getMarkdownContent = () => {
    // From https://www.w3schools.com/jsref/jsref_startswith.asp 
    if (post.content.startsWith("/")) {
      return { __html: marked("") };
    }
    return { __html: marked(post.content || "") };
  };

  // if type is image then format the image url
  let imageURL = null;
  if (post.contentType === "image/jpeg") {
    imageURL = `${post.id}/image`;
  } else {
    imageURL = null;
  }

  const handleLike = async () => {
    // Ensure currentAuthor is Author 1 (logged-in user)
    const myProfile = currenAuthor; // currenAuthor should contain the logged-in user's details (Author 1)
  
    // Verify that the post is not already liked
    if (!liked) {
      // Construct the like object with the correct author details (Author 1's details)
      const likeObject = {
        type: "like",
        author: {
          type: "author",
          id: myProfile.id,  // Author ID from myProfile
          page: myProfile.page,  // Author page URL from myProfile
          host: myProfile.host,  // Author host from myProfile
          displayName: myProfile.displayName,  // Author's displayName
          github: myProfile.github,  // Author's GitHub URL
          profileImage: myProfile.profileImage || "https://default.image.url"  // Author's profile image or default
        },
        object: `http://localhost:8000/api/authors/${authorId}/posts/${postId}`,  // Post being liked (Author 1's post)
      };
  
      console.log("Sending like object:", likeObject);  // Log the like object for debugging
  
      // Send the like request to Author 1's /liked endpoint
      const likeUrl = `http://localhost:8000/api/authors/${myProfile.id.split("/").pop()}/liked`;  // Ensure it's Author 1's /liked endpoint
  
      try {
        const response = await cusFetch(likeUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(likeObject),  // Send the like object in the request body
        });
  
        // If the like request was successful, update state
        if (response.ok) {
          setLiked(true);  // Mark post as liked
          cusFetchLikes();  // Refresh the likes for the post
        } else {
          console.error("Failed to like the post");  // Handle failure
        }
      } catch (error) {
        console.error("Error in sending like request: ", error);  // Catch any errors in the request
      }
    }
  };
  

  const handleShare = async () => {
    if (post.visibility === "public") {
      try {
        const response = await cusFetch(`${apiUrl}authors/${currentAuthorId}/posts/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            token: `${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            "title": post.title,
            "content": post.content,
            "contentType": post.contentType,
            "visibility": post.visibility,
            "description": post.description,
          }),
        });

        if (response.ok) {
          alert("Post shared successfully!");
        } else {
          const errorData = await response.json();
          console.error("Error sharing post:", errorData);
          alert("Failed to share post.");
        }
      } catch (error) {
        console.error("Error sharing post:", error);
        alert("Failed to share post.");
      }
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
      </div>
      <div className="post-card-content" dangerouslySetInnerHTML={getMarkdownContent()} />
      {imageURL && (
        <div className="post-card-image">
          <img src={imageURL} alt="Post" className="post-image" />
        </div>
      )}
      <p className="post-card-update-date">Published at: {new Date(post.published).toLocaleString()}</p>
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
    </div>
  );
}
