import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";

/**
 * This is a component for displaying the personal stream page by using PostCards component.
 * Click Profile button => go to profile page
 * Click Go to Edit Mode button => show only editable posts
 *      Click a post => go to edit page
 * Click Go to Stream Mode button => show all accessible posts
 * Add comment functionality completed
 *
 */
export default function Stream() {
  const apiUrl = process.env.REACT_APP_API_URL;
  const [posts, setPosts] = useState([]);
  const [follows, setFollows] = useState([]);
  const [isVisible, setIsVisible] = useState(true);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const { authorId } = useParams();
  const [reposts, setReposts] = useState([]);
  const [posts2, setPosts2] = useState([]);
  const [posts3, setPosts3] = useState([]);

  // get the posts list
  useEffect(() => {
    fetch(apiUrl + "post/", {
      method: "GET",
      headers: {
        "token": `${token}`,
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => setPosts3(data));
  }, [apiUrl, token]);
  // get the posts list with following_list parameter
  // useEffect(() => {
  //   fetch(`${apiUrl}post/?following_list=true`, {
  //     method: "GET",
  //     headers: {
  //       "token": `${token}`,
  //       "Content-Type": "application/json",
  //     },
  //   })
  //     .then((response) => response.json())
  //     .then((data) => setPosts3(data));
  // }, [apiUrl, token]);

  // get the follows list
  useEffect(() => {
    fetch(apiUrl+'follow/',
      {
        method: "GET",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
        },
      }
    )
      .then((response) => response.json())
      .then((data) => setFollows(data));
  }, []);

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
      console.log("posid: " + postid);
      console.log(`${apiUrl}post/?ids=${postid.join(',')}`);
      fetch(`${apiUrl}post/?ids=${postid.join(',')}`, {
        method: "GET",
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json",
      }
    })
      .then((response) => response.json())
      .then((data) => {
        const repostedPosts = data
            .filter(post => postid.includes(post.id))
            .map(post => {
              const repost = reposts.find(r => r.post === post.id);
              return {
                ...post,
                isRepost: true,
                repostedBy: repost.reposted_by
              };
            });
          setPosts2(repostedPosts);
      });
  }
  }, [reposts, apiUrl, token]);

  useEffect(() => {
    const combinedPosts = [
      ...posts3.map(post => ({ ...post, isRepost: false })), // Add isRepost property to original posts
      ...posts2
    ];
    setPosts(combinedPosts);
  }, [posts3, posts2]);

  // get the author id
  const authorIdInt = parseInt(authorId);

  // check if the post is deleted
  const matchUndelete = (post) => {
    return post.is_deleted === false;
  };

  // check if the post is public
  const matchesPublic = (post) => {
    return post.visibility.toLowerCase() === "public";
  };

  //############
  // check if the post is unlisted
  const matchesUnlisted = (post) => {
    return post.visibility.toLowerCase() === "unlisted";
  };
  // get the following list of current user (authors' id followed by the current user)
  const followingAuthorsId = [];
  follows.forEach(getFollowAuthor);
  function getFollowAuthor(f) {
    if (f.follower === authorIdInt){
      followingAuthorsId.push(f.followed)
    }
  };
  // get the friends list of current user (friend authors' id of the current user)
  const friendsAuthorsId = [];
  followingAuthorsId.forEach(getFriendAuthor);
  function getFriendAuthor(fId) {
    follows.forEach((f)=>{
      if (f.follower === fId && f.followed === authorIdInt){
        friendsAuthorsId.push(f.follower)
      }
    })
  };
  // check if the author of the post is friend of the current user
  // if so, then all posts of that author can be shown on the stream page
  const matchesFriendAuthor = (post) => {
    return friendsAuthorsId.includes(post.author);
  };
  //##########

  // check if the post is from current user
  const matchesAuthor = (post, id) => {
    return post.author === id;
  };

  const matchId = (follow) => {
    return follow.followed.toString() === localStorage.getItem("logged_in_id");
  };
  const matchPending = (follow) => {
    return follow.pending === "yes";
  };
  const pendingFollows = follows.filter((follow) => matchId(follow) && matchPending(follow));

  // Filter posts to show posts belonging to the current user, public posts,
  // unlisted posts belonging to authors that the current user follows, friend-only posts belonging to friends
  const visiblePosts = posts.filter(
    (post) =>
      matchUndelete(post) &&
      (matchesPublic(post) ||
        matchesAuthor(post, authorIdInt) ||
        matchesFriendAuthor(post) ||
        (matchesUnlisted(post) &&
          follows.some(
            (follow) =>
              follow.follower === authorIdInt && follow.followed === post.author
          )) )
  );

  // sort visible posts so that the most recent updated posts appear at the top
  const sortedAllPosts = visiblePosts
    .sort((a, b) => {
      return (
        new Date(a.scheduled_for).getTime() -
        new Date(b.scheduled_for).getTime()
      );
    })
    .reverse();
  // get the posts that belong to the current user
  const editablePosts = posts.filter(
    (post) => matchesAuthor(post, authorIdInt) && !post.isRepost
  );
  const sortedEditablePosts = editablePosts
    .sort((a, b) => {
      return (
        new Date(a.scheduled_for).getTime() -
        new Date(b.scheduled_for).getTime()
      );
    })
    .reverse();
  // Go to the editable profile page belongs to the current user
  const goEditableProfile = () => {
    navigate(`/stream/${authorId}/profile`);
  };

  // Go to the create post page for the current user
  const goCreatePost = () => {
    navigate(`/stream/${authorId}/createPost`);
  };

  return (
    <div className="stream-page">
      {/* Conditional Title */}
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
        <select
          className="dropdown"
          id="follow-notifications"
        >
          <option>{pendingFollows.length} pending follow requests</option>
          <option>
            {pendingFollows.map((follow) => (
              <option key={follow.id}>{follow.followed}</option>
            ))}
          </option>
        </select>
      </div>

      {isVisible && (
        <div className="post-grid">
          {sortedAllPosts.map((post) => (
            <PostCards
              post={post}
              key={post.id}
              editable={false}
              // onClick={() => navigate(`/posts/${post.id}`)} 
              onClick={() => isVisible ? navigate(`/posts/${post.id}`) : navigate(`/stream/${authorId}/${post.id}/edit`)}

              canShare={post.can_share} // ADDED CAN_SHARE PROP
              isRepost={post.isRepost}
              repostedBy={post.repostedBy}
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
              // onClick={() => navigate(`/posts/${post.id}`)}
              onClick={() => isVisible ? navigate(`/posts/${post.id}`) : navigate(`/stream/${authorId}/${post.id}/edit`)}

              canShare={post.can_share} // ADDED CAN_SHARE PROP
              isRepost={post.isRepost}
              repostedBy={post.repostedBy}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// import React, { useState, useEffect } from "react";
// import { useNavigate, useParams } from "react-router-dom";
// import "../streamStyle.css";
// import PostCards from "./PostCards";

// export default function Stream() {
//   const apiUrl = process.env.REACT_APP_API_URL;
//   const [posts, setPosts] = useState([]);
//   const [follows, setFollows] = useState([]);
//   const [isVisible, setIsVisible] = useState(true);
//   const navigate = useNavigate();
//   const token = localStorage.getItem("token");
//   const { authorId } = useParams();

//   // Fetch the list of posts
//   useEffect(() => {
//     fetch(apiUrl + "post/", {
//       method: "GET",
//       headers: {
//         token: `${token}`,
//         "Content-Type": "application/json",
//       },
//     })
//       .then((response) => response.json())
//       .then((data) => setPosts(data)); // Directly set posts without visibility filtering
//   }, [apiUrl, token]);

//   const matchesAuthor = (post, id) => {
//     return post.author === id;
//   };

//   const authorIdInt = parseInt(authorId);

//   const editablePosts = posts.filter(
//     (post) => matchesAuthor(post, authorIdInt) && !post.isRepost
//   );

//   // Filter posts to exclude deleted ones
//   const visiblePosts = posts.filter((post) => post.is_deleted === false);

//   // Sort posts to display the most recent at the top
//   const sortedAllPosts = visiblePosts.sort(
//     (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
//   );

//   // Navigate to profile
//   const goEditableProfile = () => {
//     navigate(`/stream/${authorId}/profile`);
//   };

//   // Navigate to create a new post
//   const goCreatePost = () => {
//     navigate(`/stream/${authorId}/createPost`);
//   };

//   return (
//     <div className="stream-page">
//       <h2 className="page-subtitle">
//         {isVisible ? "Welcome to the Stream Page!" : "Edit Page"}
//       </h2>

//       <div className="button-container">
//         <button className="edit-profile-btn" onClick={goEditableProfile}>
//           Profile
//         </button>
//         <button className="go-create-post" onClick={goCreatePost}>
//           Make a Post
//         </button>
//         <button
//           className="post-edit-btn"
//           onClick={() => setIsVisible(!isVisible)}
//         >
//           {isVisible ? "Go to Edit Mode" : "Go to Stream Mode"}
//         </button>
//       </div>

//       {isVisible && (
//         <div className="post-grid">
//           {sortedAllPosts.map((post) => (
//             <PostCards
//               post={post}
//               key={post.id}
//               editable={false}
//               canShare={post.can_share}
//               isRepost={post.isRepost}
//               repostedBy={post.repostedBy}
//             />
//           ))}
//         </div>
//       )}
//       {!isVisible && (
//         <div className="post-grid">
//           {editablePosts.map((post) => (
//             <PostCards
//               post={post}
//               key={post.id}
//               editable={true}
//               canShare={post.can_share} // ADDED CAN_SHARE PROP
//               isRepost={post.isRepost}
//               repostedBy={post.repostedBy}
//             />
//           ))}
//         </div>
//       )}
//     </div>
//   );
// }
