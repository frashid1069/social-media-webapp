import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import PostCards from "./PostCards";
import { cusFetch } from './Login';
import Header from "./Header";
import './css/profile.css'
const apiUrl = process.env.REACT_APP_API_URL

/**
 * This is a component for displaying the profile page\
 *
 */
export default function Profile() {
  const { authorId } = useParams();
  const [author, setAuthor] = useState([]);
  const [posts, setPosts] = useState([]);
  const [followers, setFollowers] = useState([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const token = localStorage.getItem("token");
  const navigate = useNavigate();
  const getFollowingKey = () => `followingState:${currentAuthorId}`;

  const decodedPostAuthorFqid = decodeURIComponent(authorId);

  const currentAuthorId = localStorage.getItem("currentAuthorId")
  const encodedCurrentAuthorFqid = encodeURIComponent(currentAuthorId);
  const subtitle = "Profile";


  useEffect(() => {
    const storedFollowing = JSON.parse(localStorage.getItem(getFollowingKey())) || {};
    setIsFollowing(storedFollowing[decodedPostAuthorFqid] || false);
  }, [currentAuthorId, decodedPostAuthorFqid]);

  // get the author info
  useEffect(() => {
    cusFetch(`${decodedPostAuthorFqid}`)
      .then((response) => response.json())
      .then((data) => setAuthor(data));
  }, []);
  // get the posts owned by the current user
  useEffect(() => {
    cusFetch(`${decodedPostAuthorFqid}/posts/`)
      .then((response) => response.json())
      .then((data) => setPosts(data.src));
  }, []);

  // get the follower list
  useEffect(() => {
    cusFetch(`${decodedPostAuthorFqid}/followers`)
      .then((response) => response.json())
      .then((data) => setFollowers(data.followers));
  }, []);

  // get the followers' display name of current user
  const followerAuthors = [];
  followers.forEach(getFollowerAuthor);
  function getFollowerAuthor(f) {
    followerAuthors.push(f.displayName)
  };


  // navigate to the edit profile page
  const handleEditProfile = () => {
    navigate(`/stream/${encodedCurrentAuthorFqid}/editProfile`);
  };

  // go back to stream page
  const goBackStream = () => {
    navigate(`/stream/${encodedCurrentAuthorFqid}`);
  };

  // Handle following
  const handleFollow = async (event) => {
    event.preventDefault();

    // Fetch the logged-in author's details
    const actorResponse = await cusFetch(`${currentAuthorId}/`, {
      method: "GET",
    });

    if (!actorResponse.ok) {
      alert("Failed to fetch logged-in author's details.");
      return;
    }

    const actor = await actorResponse.json();


    const objectResponse = await cusFetch(`${decodedPostAuthorFqid}/`, {
      method: "GET",
    });

    if (!objectResponse.ok) {
      alert("Failed to fetch this author's details.");
      return;
    }

    const object = await objectResponse.json();

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
      headers: {
        token: `${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(followRequest),
    });

    if (response.ok) {
      alert("you have sent a follow request to this author");
      // Update state and localStorage
      const storedFollowing = JSON.parse(localStorage.getItem(getFollowingKey())) || {};
      storedFollowing[decodedPostAuthorFqid] = true;
      localStorage.setItem(getFollowingKey(), JSON.stringify(storedFollowing));
      setIsFollowing(true);
    } else {
      alert("Failed to follow the author.");
    }
  };

  // Unfollow functionality
  const handleUnfollow = async (event) => {
    event.preventDefault();

    // Fetch the logged-in author's details
    const actorResponse = await cusFetch(`${currentAuthorId}/`, {
      method: "GET",
    });

    if (!actorResponse.ok) {
      alert("Failed to fetch logged-in author's details.");
      return;
    }

    const actor = await actorResponse.json();


    const objectResponse = await cusFetch(`${decodedPostAuthorFqid}/`, {
      method: "GET",
    });

    if (!objectResponse.ok) {
      alert("Failed to fetch this author's details.");
      return;
    }

    const object = await objectResponse.json();

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
      headers: {
        token: `${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(followRequest),
    });

    if (response.ok) {
      alert("you have unfollowed this author");
      // Update state and localStorage
      const storedFollowing = JSON.parse(localStorage.getItem(getFollowingKey())) || {};
      delete storedFollowing[decodedPostAuthorFqid];
      localStorage.setItem(getFollowingKey(), JSON.stringify(storedFollowing));
      setIsFollowing(false);
    } else {
      alert("Failed to unfollow the author.");
    }
  };

  return (
    <div className="profile-page">
      <Header subtitle={subtitle} />
      <div className="profile-content">
        <h4 className="profile-txt">Name: <span className="profile-txt-content">{author.displayName}</span></h4>
        <h4 className="profile-txt">Github URL: <span className="profile-txt-content">{author.github}</span></h4>
      </div>
      <div className="followers-content">
        <h4 className="followers-header">Followers:</h4>
        {followerAuthors.map((f, index) => (
          <p className="follower-name" key={index}>{f}</p>
        ))}
      </div>
      <div className="buttons-container">
        {decodedPostAuthorFqid === currentAuthorId && (
          <button className="edit-profile-btn" onClick={handleEditProfile}>Edit Profile</button>
        )}
        {decodedPostAuthorFqid !== currentAuthorId && (
          isFollowing ? (
            <button className="unfollow-btn" onClick={handleUnfollow}>Unfollow</button>
        ) : (
            <button className="follow-btn" onClick={handleFollow}>Follow</button>
        ))}
        <button className="profile-goBackBtn" onClick={goBackStream}>
          Back To Stream
        </button>
      </div>
      
      <div className="post-grid">
        {posts.map((post) => (
          <PostCards className="profile-postcard" post={post} key={post.id} editable={false}></PostCards>
        ))}
      </div>
    </div>
  );
}
