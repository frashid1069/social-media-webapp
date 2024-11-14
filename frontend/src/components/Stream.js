import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";
import { cusFetch } from "./Login";

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
  const [posts, setPosts] = useState([]);
  const [follows, setFollows] = useState([]);
  const [isVisible, setIsVisible] = useState(true);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const { authorId } = useParams();
  const authorIdInt = parseInt(authorId);
  const [reposts, setReposts] = useState([]);
  const [posts2, setPosts2] = useState([]);
  const [posts3, setPosts3] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const follow_id = localStorage.getItem("follow_id");

  // Get the posts list
  useEffect(() => {
    fetch(apiUrl + "posts/", {
      method: "GET",
      headers: {
        "token": `${token}`,
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => setPosts3(data.src));
  }, [apiUrl, token]);

  // // Get the follows list
  // useEffect(() => {
  //   fetch(apiUrl + "follow/", {
  //     method: "GET",
  //     headers: {
  //       "token": `${token}`,
  //       "Content-Type": "application/json",
  //     },
  //   })
  //     .then((response) => response.json())
  //     .then((data) => {
  //       console.log(data); // Inspect structure to find the correct field for follower name
  //       setFollows(data);
  //     });
  // }, [apiUrl, token]);

  // Fetch follow requests and get follower details
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
          console.log("Mapped Follows with Names:", followsWithNames); // Verify data
          setFollows(followsWithNames);
        });
      });
  }, [apiUrl, token, authorIdInt]);

  // Handle accepting or declining follow requests
  const handleAccept = async (followerId, followerName) => {
    const response = await cusFetch(`${apiUrl}follow/${follow_id}/`, {
      method: "PUT",
      headers: {
        "token": `${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        follower: followerId,
        followed: authorIdInt,
        pending: "no"
      }),
    });
    if (response.ok) {
      alert(`Accepted follow request from ${followerName}`);
      setFollows((prevFollows) =>
        prevFollows.filter((follow) => follow.follower !== followerId)
      );
    }
  };

  const handleDecline = async (followerId, followerName) => {
    try {
      // First, check if the follow object exists
      const checkResponse = await cusFetch(`${apiUrl}follow/${follow_id}/`, {
        method: "GET",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
        },
      });
  
      if (!checkResponse.ok) {
        alert("The follow request no longer exists.");
        return;
      }
  
      // If it exists, proceed with deletion
      const deleteResponse = await cusFetch(`${apiUrl}follow/${follow_id}/`, {
        method: "DELETE",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
        },
      });
  
      if (deleteResponse.ok) {
        // Remove the follow request from the pending list
        setFollows((prevFollows) =>
          prevFollows.filter((follow) => follow.follower !== followerId)
        );
        alert(`Declined follow request from ${followerName}`);
      }
    } catch (error) {
      console.error("Error declining follow request:", error);
    }
  };



  // Fetch reposts
  useEffect(() => {
    fetch(`${apiUrl}repost/`, {
      method: "GET",
      headers: {
        "token": `${token}`,
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setReposts(data);
      });
  }, [apiUrl, token]);

  useEffect(() => {
    if (reposts.length > 0) {
      const postid = reposts.map((repost) => repost.post);
      fetch(`${apiUrl}post/?ids=${postid.join(",")}`, {
        method: "GET",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          const repostedPosts = data
            .filter((post) => postid.includes(post.id))
            .map((post) => {
              const repost = reposts.find((r) => r.post === post.id);
              return {
                ...post,
                isRepost: true,
                repostedBy: repost.reposted_by,
              };
            });
          setPosts2(repostedPosts);
        });
    }
  }, [reposts, apiUrl, token]);

  useEffect(() => {
    const combinedPosts = [
      ...posts3.map((post) => ({ ...post, isRepost: false })), // Add isRepost property to original posts
      ...posts2,
    ];
    setPosts(combinedPosts);
  }, [posts3, posts2]);

  // Determine mutual friends for friend-only posts
  const followingAuthorsId = follows
    .filter((f) => f.follower === authorIdInt)
    .map((f) => f.followed);

  const friendsAuthorsId = followingAuthorsId.filter((id) =>
    follows.some((f) => f.follower === id && f.followed === authorIdInt)
  );

  // Check if the post is from a friend or the author themselves
  const isFriend = (post) =>
    friendsAuthorsId.includes(post.author) || post.author === authorIdInt;

  // // Define helper functions
  // const matchUndelete = (post) => post.is_deleted === false;

  // const matchesPublic = (post) => post.visibility.toLowerCase() === "public";

  const matchesAuthor = (post, id) => post.author === id;

  // const matchesUnlisted = (post) => post.visibility.toLowerCase() === "unlisted";

  // // Allow authors to view their own friends-only posts
  // const matchesFriendAuthor = (post) =>
  //   post.visibility.toLowerCase() === "friend-only" &&
  //   (friendsAuthorsId.includes(post.author) || post.author === authorIdInt);

  // // Filter posts to show posts belonging to the current user, public posts,
  // // unlisted posts belonging to authors that the current user follows, friend-only posts belonging to friends
  // const visiblePosts = posts.filter(
  //   (post) =>
  //     matchUndelete(post) &&
  //     (matchesPublic(post) ||
  //       matchesAuthor(post, authorIdInt) || // Ensures the author can see their own posts
  //       matchesFriendAuthor(post) ||
  //       (matchesUnlisted(post) &&
  //         follows.some(
  //           (follow) =>
  //             follow.follower === authorIdInt && follow.followed === post.author
  //         )))
  // );

  const sortedAllPosts = posts
    .sort((a, b) => new Date(b.scheduled_for).getTime() - new Date(a.scheduled_for).getTime());

  const editablePosts = posts.filter(
    (post) => matchesAuthor(post, authorIdInt) && !post.isRepost
  );
  const sortedEditablePosts = editablePosts
    .sort((a, b) => new Date(b.scheduled_for).getTime() - new Date(a.scheduled_for).getTime());

  const goEditableProfile = () => {
    navigate(`/stream/${authorId}/profile`);
  };

  const goCreatePost = () => {
    navigate(`/stream/${authorId}/createPost`);
  };
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
        {/* Custom dropdown for follow requests 
            CHAT GPT: Prompt help me create a custom dropdown that shows the follow requestsindividually and along with
            options to accept or decline. Date: NOV 2, 2024*/}
        <div className="dropdown">
          <button className="dropdown-toggle" onClick={toggleDropdown}>
            {follows.length} pending follow requests
          </button>

          {dropdownOpen && (
            <div className="dropdown-menu">
              {pendingFollows.map((follow) => (
                <div key={follow.id} className="dropdown-item">
                  <span>{follow.followerName}</span> {/* Display follower's name */}
                  <button
                    className="tick-btn"
                    onClick={(e) => { handleAccept(follow.follower, follow.followerName) }}
                  >
                    ✔️
                  </button>
                  <button
                    className="cross-btn"
                    onClick={(e) => { handleDecline(follow.follower, follow.followerName) }}
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
          {sortedAllPosts.map((post) => (
            <PostCards
              post={post}
              key={post.id}
              editable={false}
              onClick={() =>
                isVisible
                  ? navigate(`/posts/${post.id}`)
                  : navigate(`/stream/${authorId}/${post.id}/edit`)
              }
              canShare={post.can_share}
              isRepost={post.isRepost}
              repostedBy={post.repostedBy}
              isFriend={isFriend(post)}
            />
          ))}
        </div>
      )}
      {!isVisible && (
        <div className="post-grid">
          {sortedEditablePosts.map((post) => (
            <PostCards
              post={post}
              key={post.id}
              editable={true}
              onClick={() =>
                isVisible
                  ? navigate(`/posts/${post.id}`)
                  : navigate(`/stream/${authorId}/${post.id}/edit`)
              }
              canShare={post.can_share}
              isRepost={post.isRepost}
              repostedBy={post.repostedBy}
              isFriend={isFriend(post)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
