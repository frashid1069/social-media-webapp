import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";
import { cusFetch } from "./Login";
import Author from "./Author";
import { getCurrentAuthor } from "./Author";

export const getAuthorId = (url) => {
    const authorMatch = url.match(/authors\/(\d+)/);
    return authorMatch ? authorMatch[1] : null;       // Returns author ID or null if not found
  }
  
export const getPostId = (url) => {
    const postMatch = url.match(/posts\/(\d+)/);
    return postMatch ? postMatch[1] : null;       // Returns post ID or null if not found
  }

/**
 * This is a component for displaying the personal stream page by using PostCards component.
 * Click Profile button => go to profile page
 * Click Go to Edit Mode button => show only editable posts
 *      Click a post => go to edit page
 * Click Go to Stream Mode button => show all accessible posts
 * Add comment functionality completed
 */
export default function Stream() {
  const apiUrl = process.env.REACT_APP_API_URL;
  const [editablePosts, setEditablePosts] = useState([]);
  const [follows, setFollows] = useState([]);
  const [isVisible, setIsVisible] = useState(true);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const { authorId } = useParams();
  const authorIdInt = parseInt(authorId);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const follow_id = localStorage.getItem("follow_id");
  const [streamPosts, setstreamPosts] = useState([]);
  const [pendingFollowRequests, setPendingFollowRequests] = useState([]);
  const currentAuthorId = authorId

  // get the current author object
  const [currentAuthor, setCurrentAuthor] = useState([]);
  useEffect(() => {
    cusFetch(`${apiUrl}authors/${authorId}`)
      .then((response) => response.json())
      .then((data) => {
        setCurrentAuthor(data);
      });
  }, []);

  // Get the posts list
  useEffect(() => {
    cusFetch(`${apiUrl}posts/`)
      .then((response) => response.json())
      .then((data) => {
          setstreamPosts(data.src);
      });
  }, []);
  
  // get the posts owned by the current user
  useEffect(() => {
    cusFetch(`${apiUrl}authors/${authorId}/posts/`)
      .then((response) => response.json())
      .then((data) => {
          setEditablePosts(data.src);
      });
  }, []);

  // Fetch all pending follow requests for the author
  useEffect(() => {
    cusFetch(`${apiUrl}follows/`)
      .then((response) => {
        response.json();
        console.log(response);
      })
      .then((data) => {
        console.log("data", data);
        setPendingFollowRequests(...data);
        console.log("pending: ", pendingFollowRequests)
      })
      .catch((error) => {
        console.log(error);
        console.log("pending: ", pendingFollowRequests);}) 
    });
    
  // Fetch follow requests and get follower details
  useEffect(() => {
    fetch(`${apiUrl}follow/`, {
      method: "GET",
      headers: {
        "token": `${token}`,
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const pendingRequests = data.filter(
          (follow) => follow.pending === "yes" && follow.followed === authorIdInt
        );

        // Fetch follower details for each follow request
        const followerPromises = pendingRequests.map((follow) =>
          fetch(`${apiUrl}author/${follow.follower}`, {
            method: "GET",
            headers: {
              "token": `${token}`,
              "Content-Type": "application/json",
            },
          }).then((response) => response.json())
        );

        // Map display names to the follow requests
        Promise.all(followerPromises).then((followers) => {
          const followsWithNames = pendingRequests.map((follow, index) => ({
            ...follow,
            followerName: followers[index].display_name, // Use display_name field from Author model
          }));
          setFollows(followsWithNames);
        });
      });
  }, [apiUrl, token, authorIdInt]);

  // Handle accepting or declining follow requests
  const handleAccept = async (followRequest) => {
    try {
      const response = await cusFetch(`${apiUrl}follows/${followRequest.id}`, {
        method: "PUT",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
        },
        body: {
          "pending": "no"
        },
      });
      if (response.ok) {
        alert(`Accepted follow request from ${followRequest.follower.displayName}`);
      }
    } catch (error) {
      console.error("Error declining follow request:", error);
    }
  };

  const handleDecline = async (followRequest) => {
    try {
      const response = await cusFetch(`${apiUrl}follows/${followRequest.id}`, {
        method: "PUT",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
        },
        body: {
          "pending": "yes"
        },
      });
      if (response.ok) {
        alert(`Declined follow request from ${followRequest.follower.displayName}`);
      }
    } catch (error) {
      console.error("Error declining follow request:", error);
    }
  };
  // go to profile page
  const goEditableProfile = () => {
    navigate(`/stream/${authorId}/profile`);
  };
  // go to create post page
  const goCreatePost = () => {
    navigate(`/stream/${authorId}/createPost`);
  };
  const goShowAuthors = () => {
    navigate(`/stream/${currentAuthorId}/authors`);
  }
  // log out the current user
  const goLogout = () => {
    localStorage.setItem("token", '');
    navigate("/login")
  }
  const matchId = (follow) => {
    return follow.followed.toString() === localStorage.getItem("logged_in_id");
  };
  const matchPending = (follow) => {
    return follow.pending === "yes";
  };
  const pendingFollows = follows.filter((follow) => matchId(follow) && matchPending(follow));

  const toggleDropdown = () => setDropdownOpen(!dropdownOpen);
  return (
    <div className="stream-page">
      <h2 className="page-subtitle">{isVisible ? "Welcome to the Stream Page!" : "Edit Page"}</h2>

      <div className="button-container">
      <button className="show-authors" onClick={goShowAuthors}>
          Show All Authors
        </button>
        <button className="edit-profile-btn" onClick={goEditableProfile}>
          Profile
        </button>
        <button className="go-create-post" onClick={goCreatePost}>
          Make a Post
        </button>
        <button
          className="post-edit-btn"
          onClick={() => setIsVisible(!isVisible)}
        >
          {isVisible ? "Go to Edit Mode" : "Go to Stream Mode"}
        </button>
        <button className="logout-btn" onClick={goLogout}>Logout</button>
        {/* Custom dropdown for follow requests 
            CHAT GPT: Prompt help me create a custom dropdown that shows the follow requestsindividually and along with
            options to accept or decline. Date: NOV 2, 2024*/}
        <div className="dropdown">
          <button className="dropdown-toggle" onClick={toggleDropdown}>
            {follows.length} pending follow requests
          </button>

          {dropdownOpen && (
            <div className="dropdown-menu">
              {pendingFollowRequests.map((followRequest) => (
                <div key={followRequest.id} className="dropdown-item">
                  <span>{followRequest.follower.displayName}</span> {/* Display follower's name */}
                  <button
                    className="tick-btn"
                    onClick={(e) => { handleAccept(followRequest) }}
                  >
                    ✔️
                  </button>
                  <button
                    className="cross-btn"
                    onClick={(e) => { handleDecline(followRequest) }}
                  >
                    ❌
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>


      {isVisible && (
        <div className="post-grid">
          {!streamPosts && <p>Loading posts...</p>}
          {streamPosts && streamPosts.length === 0 && <p>No posts available.</p>}
          {streamPosts && streamPosts.length > 0 && streamPosts.map((post) => (
            <PostCards
              post={post}
              key={post.id}
              currenAuthor={currentAuthor}
              onClick={() =>
                isVisible
                  ? navigate(`authors/${getAuthorId(post.id)}/posts/${getPostId(post.id)}`)
                  : navigate(`/stream/${getAuthorId(post.id)}/${getAuthorId(post.id)}/edit`)
              }
              canShare={post.can_share}
            />
            ))
          }
        </div>
      )}
      {!isVisible && (
        <div>
          {!editablePosts && <p>Loading posts...</p>} 
          {editablePosts && editablePosts.length === 0 && <p>No posts available.</p>} 
          {editablePosts && editablePosts.length > 0 && editablePosts.map((post) => (
            <PostCards
              post={post}
              key={post.id}
              currenAuthor={currentAuthor}
              onClick={() =>
                isVisible
                  ? navigate(`authors/${getAuthorId(post.id)}/posts/${getPostId(post.id)}`)
                  : navigate(`/stream/${getAuthorId(post.id)}/${getPostId(post.id)}/edit`)
              }
              canShare={post.can_share}
            />
            ))
          } 
        </div>
      )}
    </div>
  );
}
