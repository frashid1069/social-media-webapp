import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { cusFetch } from "./Login";
import { getAuthorId } from "./Stream";
import Header from "./Header";
const apiUrl = process.env.REACT_APP_API_URL;


export default function AuthorsPage() {
  const [authors, setAuthors] = useState([]);
  const [currenAuthor, setCurrentAuthor] = useState([]);
  const [isFollowing, setIsFollowing] = useState({});
  const { authorId } = useParams();
  const navigate = useNavigate();
  const currentAuthorId = localStorage.getItem("currentAuthorId");
  const subtitle = "Author List";
  const getFollowingKey = () => `followingState:${currentAuthorId}`;


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
    const storedFollowing = JSON.parse(localStorage.getItem(getFollowingKey())) || {};
    setIsFollowing(storedFollowing);
  }, [currentAuthorId]);

  useEffect(() => {
    cusFetch(`${currentAuthorId}`)
      .then((response) => response.json())
      .then((data) => {
        setCurrentAuthor(data);
      });
  }, []);

  const goBackStream = () => {
    navigate(`/stream/${encodeURIComponent(currentAuthorId)}`);
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
      // Update state and localStorage
      const storedFollowing = JSON.parse(localStorage.getItem(getFollowingKey())) || {};
      storedFollowing[authorID] = true;
      localStorage.setItem(getFollowingKey(), JSON.stringify(storedFollowing));
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
      const storedFollowing = JSON.parse(localStorage.getItem(getFollowingKey())) || {};
      delete storedFollowing[authorID];
      localStorage.setItem(getFollowingKey(), JSON.stringify(storedFollowing));
      setIsFollowing((prev) => ({ ...prev, [authorID]: false })); // Mark this author as unfollowed
    } else {
      alert("Failed to unfollow the author.");
    }
  };


  return (
    <div className="authors-page">
      <Header subtitle={subtitle} />
      <h4 className="author-txt">Authors:</h4>
      <div className="authors-list">
        {authors.map((author) => (
          <div className="author-item" key={author.id}>
            <span className="author-name">{author.displayName}</span>
            {author.id !== currentAuthorId && ( // Follow/Unfollow button is not shown for the current author
              isFollowing[author.id] ? (
                <button
                  id="unfollowButton"
                  className="unfollow-btn"
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
      <button className="authors-goBackBtn" onClick={goBackStream}>
        Back To Stream
      </button>
    </div>
  );
}
