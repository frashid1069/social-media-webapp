import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
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
  // const [isFollowing, setIsFollowing] = useState(() => {
  //   const savedState = localStorage.getItem(`isFollowing_${authorId}`);
  //   return savedState ? JSON.parse(savedState) : false;})
  const [isFollowing, setIsFollowing] = useState(false);
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  // get the author id as an int
  const authorIdInt = parseInt(authorId);

  // https://stackoverflow.com/questions/63193114/how-do-i-call-a-function-automatically-when-page-loads-up-in-react-js-in-2020
  useEffect(() => {
    ownProfile();
  }, []);

  // useEffect(() => {
  //   localStorage.setItem(`isFollowing_${authorId}`, JSON.stringify(isFollowing));
  // }, [isFollowing, authorId]);

  // get the author info
  useEffect(() => {
    cusFetch(`${apiUrl}authors/${authorId}/`)
      .then((response) => response.json())
      .then((data) => setAuthor(data));
  }, [authorId]);
  // get the posts owned by the current user
  useEffect(() => {
    cusFetch(`${apiUrl}authors/${authorIdInt}/posts/`)
      .then((response) => response.json())
      .then((data) => setPosts(data.src));
  }, [authorIdInt]);

  // get the follower list
  useEffect(() => {
    cusFetch(`${apiUrl}authors/${authorIdInt}/followers`)
      .then((response) => response.json())
      .then((data) => setFollowers(data.followers));
  }, []);

  // get the followers' display name of current user
  const followerAuthors = [];
  followers.forEach(getFollowerAuthor);
  function getFollowerAuthor(f) {
    followerAuthors.push(f.displayName)
  };
  

  useEffect(() => {
    // checkFollowingStatus();
  }, [authorId]);

  // // Check if the logged-in user is following the profile author
  // const checkFollowingStatus = async () => {
  //   const loggedIn = localStorage.getItem("logged_in_id");
  //   try {
  //     const response = await cusFetch(`${apiUrl}follow/?author_id=${authorId}&follower=${loggedIn}`);
  //     if (response.ok) {
  //       const data = await response.json();
  //       if(data.length > 0) {
  //         localStorage.setItem("follow_id", data[0].id)
  //         setIsFollowing(true);
  //       }
  //       else {
  //         // No follow relationship found, reset follow status
  //         // localStorage.removeItem("follow_id");
  //         setIsFollowing(false);
  //       }
  //     }
  //   } 
  //   catch (error) {
  //     console.error("Error checking following status:", error);
  //   }
  // };


  // navigate to the edit profile page
  const handleEditProfile = () => {
    navigate(`/stream/${authorId}/editProfile`);
  };

  // go back to stream page
  const goBackStream = () => {
    navigate(`/stream/${localStorage.getItem("logged_in_id")}`);
  };
  
  // Handle following
  const handleFollow = async (event) => {
    event.preventDefault();
      
    // Fetch the logged-in author's details
    const actorResponse = await cusFetch(`${apiUrl}authors/${localStorage.getItem("logged_in_id")}/`, {
      method: "GET",
      headers: {
        token: `${token}`,
        "Content-Type": "application/json",
      },
    });
  
    if (!actorResponse.ok) {
      alert("Failed to fetch logged-in author's details.");
      return;
    }
  
    const actor = await actorResponse.json();
  
    // // Fetch the author to follow's details
    // const objectResponse = await cusFetch(`${author.id}/`, {
    //   method: "GET",
    //   headers: {
    //     token: `${token}`,
    //     "Content-Type": "application/json",
    //   },
    // });
  
    // if (!objectResponse.ok) {
    //   alert("Failed to fetch author details for following.");
    //   return;
    // }
    // const object = await objectResponse.json();

    const object = author;
  
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
    // const follow_id = localStorage.getItem("follow_id");
    // const response = await cusFetch(`${apiUrl}follow/${follow_id}/`, {
    //   method: "DELETE",
    //   headers: {
    //     "Content-Type": "application/json",
    //   },
    // });
    // if (response.ok) {
    //   alert("You have unfollowed this author.");
    //   await checkFollowingStatus(); // Refresh follow status after unfollowing
    //   setIsFollowing(false); 
    // }
  };


  const ownProfile = () => {
    if(authorId == localStorage.getItem("logged_in_id")) {
      document.getElementById("followButton").hidden = true;
    };
    if(authorId !== localStorage.getItem("logged_in_id")) {
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
