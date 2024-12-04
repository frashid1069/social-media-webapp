import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import PostCards from "./PostCards";
import { cusFetch } from "./Login";
import Header from "./Header";

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
  const authorIdInt = decodeURIComponent(authorId);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const follow_id = localStorage.getItem("follow_id");
  const [streamPosts, setstreamPosts] = useState([]);
  const [pendingFollowRequests, setPendingFollowRequests] = useState([]);
  const currentAuthorId = localStorage.getItem("currentAuthorId")
  const subtitle = "Stream";

  // get the current author object
  const [currentAuthor, setCurrentAuthor] = useState([]);
  useEffect(() => {
    cusFetch(`${currentAuthorId}`)
      .then((response) => response.json())
      .then((data) => {
        setCurrentAuthor(data);
      });
  }, []);

  // const handleChatSubmit = async () => {
  //   const currentData = JSON.stringify(availableData); // Serialize data to send
  //   const combinedPrompt = `${userInput}. Here's some data to consider: ${currentData}`;
  //   try {
  //     const res = await fetch('http://localhost:8000/api/chatgpt/', {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({ prompt: combinedPrompt }),
  //     });
  //     const data = await res.json();
  //     setResponse(data.response || 'No response from AI');
  //   } catch (error) {
  //     console.error('Error fetching ChatGPT response:', error);
  //     setResponse('Error occurred. Please try again.');
  //   }
  // };

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
    cusFetch(`${currentAuthorId}/posts/`)
      .then((response) => response.json())
      .then((data) => {
        setEditablePosts(data.src);
      });
  }, []);

  // Fetch all pending follow requests for the author
  useEffect(() => {
    cusFetch(`${apiUrl}follows/`)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        setPendingFollowRequests(data);
      })
      .catch((error) => {
        console.error("Error getting follow requests: ", error);
      })
  }, [currentAuthorId, pendingFollowRequests.length]);

  // Handle accepting or declining follow requests
  const handleAccept = async (followRequest) => {
    try {
      const response = await cusFetch(`${apiUrl}follows/${followRequest.id}`, {
        method: "PUT",
        body: JSON.stringify({ pending: "no" })
      });
      if (response.ok) {
        alert(`Accepted follow request from ${followRequest.follower.displayName}`);
        setPendingFollowRequests((prevRequests) =>
          prevRequests.filter((request) => request.id !== followRequest.id)
        );
      }
    } catch (error) {
      console.error("Error declining follow request:", error);
    }
  };

  const handleDecline = async (followRequest) => {
    try {
      const response = await cusFetch(`${apiUrl}follows/${followRequest.id}`, {
        method: "PUT",
        body: JSON.stringify({ pending: "yes" })
      });
      if (response.ok) {
        alert(`Declined follow request from ${followRequest.follower.displayName}`);
        setPendingFollowRequests((prevRequests) =>
          prevRequests.filter((request) => request.id !== followRequest.id)
        );
      }
    } catch (error) {
      console.error("Error declining follow request:", error);
    }
  };
  // go to profile page
  const goEditableProfile = () => {
    navigate(`/stream/${encodeURIComponent(currentAuthorId)}/profile`);
  };
  // go to create post page
  const goCreatePost = () => {
    navigate(`/stream/${encodeURIComponent(currentAuthorId)}/createPost`);
  };
  const goShowAuthors = () => {
    navigate(`/stream/${encodeURIComponent(currentAuthorId)}/authors`);
  }
  // log out the current user
  const goLogout = () => {
    localStorage.setItem("token", '');
    navigate("/login")
  }

  const toggleDropdown = () => setDropdownOpen(!dropdownOpen);
  return (
    <div className="stream-page">
      <Header subtitle={subtitle} />
      <div className="button-container">
        <button id="go-create-post" onClick={goCreatePost}>
          Create a Post 
        </button>
        <div className="right-buttons">
          <button className="show-authors" onClick={goShowAuthors}>
            Show All Authors
          </button>
          <button className="edit-profile-btn" onClick={goEditableProfile}>
            Profile
          </button>
          <button
            className="post-edit-btn"
            onClick={() => setIsVisible(!isVisible)}
          >
            {isVisible ? "Go to Edit Mode" : "Go to Stream Mode"}
          </button>

          {/* Custom dropdown for follow requests 
            CHAT GPT: Prompt help me create a custom dropdown that shows the follow requestsindividually and along with
            options to accept or decline. Date: NOV 2, 2024*/}
          <div className="dropdown">
            <button className="dropdown-toggle" onClick={toggleDropdown}>
              {pendingFollowRequests.length} pending follow requests
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
          <button className="logout-btn" onClick={goLogout}>Logout</button>
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
                  ? navigate(`/posts/${encodeURIComponent(post.id)}`)
                  : navigate(`/posts/${encodeURIComponent(post.id)}/edit`)
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
                  ? navigate(`/posts/${encodeURIComponent(post.id)}`)
                  : navigate(`/posts/${encodeURIComponent(post.id)}/edit`)
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
