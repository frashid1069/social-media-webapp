import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./css/streamStyle.css";
import PostCards from "./PostCards";
import { cusFetch } from './Login';

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

  const decodedPostAuthorFqid = decodeURIComponent(authorId);

  const currentAuthorId = localStorage.getItem("currentAuthorId")
  const encodedCurrentAuthorFqid = encodeURIComponent(currentAuthorId);



  // https://stackoverflow.com/questions/63193114/how-do-i-call-a-function-automatically-when-page-loads-up-in-react-js-in-2020
  useEffect(() => {
    ownProfile();
  }, []);

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
      // await checkFollowingStatus(); // Update follow status and follow_id after following
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
      // await checkFollowingStatus(); // Update follow status and follow_id after following
      setIsFollowing(true);
    } else {
      alert("Failed to unfollow the author.");
    }
  };


  const ownProfile = () => {
    if(decodedPostAuthorFqid == currentAuthorId) {
      document.getElementById("followButton").hidden = true;
    };
    if(decodedPostAuthorFqid !== currentAuthorId) {
      document.getElementById("editButton").hidden = true;
    };
  };
  return (
    <div className="profile-page">
      <h2 className="page-subtitle">Welcome to the Profile page!</h2>
      <button className="profile-goBackBtn" onClick={goBackStream}>
        Back To Stream
      </button>
      <h4 className="profile-txt">Name: </h4>
      <p className="profile-name">{author.displayName}</p>
      <h4 className="profile-txt">Github URL: </h4>
      <p className="profile-git">{author.github}</p>
      <h4 className="profile-txt">Followers: </h4>
      {followerAuthors.map((f)=> (<p>{f}</p>))}
      <button id = "editButton" onClick={handleEditProfile}>Edit Profile</button>
      {isFollowing ? (
        <button id="unfollowButton" onClick={handleUnfollow}>Unfollow</button>
      ) : (
        <button id="followButton" onClick={handleFollow}>Follow</button>
      )}
      <div className="post-grid">
        {posts.map((post) => (
          <PostCards post={post} key={post.id} editable={false}></PostCards>
        ))}

      </div>

    </div>
  );
}
