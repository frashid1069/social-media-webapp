import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { cusFetch } from "./Login";
import "../streamStyle.css";
import { getAuthorId } from "./Stream";
const apiUrl = process.env.REACT_APP_API_URL;


export default function AuthorsPage() {
  const [authors, setAuthors] = useState([]);
  const [currenAuthor, setCurrentAuthor] = useState([]);
  const [isFollowing, setIsFollowing] = useState({});
  const { authorId } = useParams();
  const navigate = useNavigate();
  const currentAuthorId = localStorage.getItem("currentAuthorId");

  useEffect(() => {
    const fetchAuthors = async () => {
      const response = await cusFetch(`${apiUrl}authors/`);
      const data = await response.json();
  
      if (data && data.authors && data.authors.length > 0) {
        setAuthors(data.authors);
      }
    };
  
    fetchAuthors();
  }, [currentAuthorId]);

  useEffect(() => {
    cusFetch(`${currentAuthorId}`)
      .then((response) => response.json())
      .then((data) => {
        setCurrentAuthor(data);
      });
  }, []);

  const goBackStream = () => {
    navigate(`/stream/${authorId}`);
  };

  // Handle following
  const handleFollow = async (authorID) => {
    // Fetch the logged-in author's details
    const actorResponse = await cusFetch(`${currentAuthorId}/`, {
      method: "GET",
    });
  
    if (!actorResponse.ok) {
      alert("Failed to fetch logged-in author's details.");
      return;
    }
  
    const actor = await actorResponse.json();
  
    const object = authors.find((author) => author.id === authorID)
  
    // Construct the follow request object
    const followRequest = {
      type: "follow",
      summary: `${actor.displayName} wants to follow ${object.displayName}`,
      actor: {
        type: "author",
        ...actor,
      },
      object: {
        type: "author",
        ...object,
      },
    };
  
    // Send the follow request to the inbox
    const response = await cusFetch(`${apiUrl}forward/`, {
      method: "POST",
      body: JSON.stringify(followRequest),
    });
  
    if (response.ok) {
      alert(`You have sent a follow request to this author`);
      setIsFollowing((prev) => ({ ...prev, [authorID]: true })); // Mark this author as followed
    } else {
      alert("Failed to follow the author.");
    }
  };
    
  
  // Unfollow functionality
  const handleUnfollow = async (authorID) => {
    // Fetch the logged-in author's details
    const actorResponse = await cusFetch(`${currentAuthorId}/`, {
      method: "GET",
    });
  
    if (!actorResponse.ok) {
      alert("Failed to fetch logged-in author's details.");
      return;
    }
  
    const actor = await actorResponse.json();
  
    const object = authors.find((author) => author.id === authorID)
  
    // Construct the follow request object
    const followRequest = {
      type: "follow",
      summary: `${actor.displayName} wants to follow ${object.displayName}`,
      actor: {
        type: "author",
        ...actor,
      },
      object: {
        type: "author",
        ...object,
      },
    };
  
    // Send the follow request to the inbox
    const response = await cusFetch(`${apiUrl}forward/`, {
      method: "DELETE",
      body: JSON.stringify(followRequest),
    });
  
    if (response.ok) {
      alert(`You have unfollowed this author`);
      setIsFollowing((prev) => ({ ...prev, [authorID]: true })); // Mark this author as followed
    } else {
      alert("Failed to unfollow the author.");
    }
  };


  return (
  <div className="authors-page">
      <h2 className="page-subtitle">List of Authors</h2>
      <button className="authors-goBackBtn" onClick={goBackStream}>
      Back To Stream
      </button>
      <h4 className="author-txt">Authors:</h4>
      {authors.map((author) => (
      <div className="author-item" key={author.id}>
          <span className="author-name">{author.displayName}</span>
          {author.id !== currentAuthorId && ( // Follow/Unfollow button is not shown for the current author
            isFollowing[author.id] ? (
              <button
                id="unfollowButton"
                className="follow-btn"
                onClick={() => handleUnfollow(author.id)}
              >
                Unfollow
              </button>
            ) : (
              <button
                id="followButton"
                className="follow-btn"
                onClick={() => handleFollow(author.id)}
              >
                Follow
              </button>
            )
          )}
      </div>
      ))}
  </div>
  );
}
