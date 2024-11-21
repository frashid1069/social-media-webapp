import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { cusFetch } from "./Login";
import "../streamStyle.css";
import { getAuthorId } from "./Stream";
const apiUrl = process.env.REACT_APP_API_URL;


export default function AuthorsPage() {
    const [authors, setAuthors] = useState([]);
    const [isFollowing, setIsFollowing] = useState({});
    const { authorId } = useParams();
    const navigate = useNavigate();
    const currentAuthorId = authorId;
    const loggedInID = localStorage.getItem("logged_in_id");

    useEffect(() => {
        const fetchAuthors = async () => {
          const response = await cusFetch(`${apiUrl}authors/`);
          const data = await response.json();
      
          if (data && data.authors && data.authors.length > 0) {
            // const filteredAuthors = data.authors.filter(
            //   (author) => {
            //     console.log("author id:", getAuthorId(author.id));
            //     console.log("current author id:", currentAuthorId);
            //     return getAuthorId(author.id) !== currentAuthorId;
            //     }
            // );
            // setAuthors(filteredAuthors); // Update state
            // console.log(filteredAuthors.length); // Log directly from the filtered list
            setAuthors(data.authors);
          }
        };
      
        fetchAuthors();
      }, [currentAuthorId]);

    const goBackStream = () => {
        navigate(`/stream/${currentAuthorId}`);
      };

    // Handle following
    const handleFollow = async (authorID) => {
        const token = localStorage.getItem("token");
        console.log("author ID: ", authorID)
      
        // Fetch the logged-in author's details
        const actorResponse = await cusFetch(`${apiUrl}authors/${currentAuthorId}/`, {
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
      
        // Fetch the author to follow's details
        // const objectResponse = await cusFetch(`${apiUrl}forward/${apiUrl}authors/${authorID}/`, {
        const objectResponse = await cusFetch(`${apiUrl}authors/${authorID}/`, {

          method: "GET",
          headers: {
            token: `${token}`,
            "Content-Type": "application/json",
          },
        });
      
        if (!objectResponse.ok) {
          alert("Failed to fetch author details for following.");
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
          alert(`You have sent a follow request to this author`);
          setIsFollowing((prev) => ({ ...prev, [authorID]: true })); // Mark this author as followed
        } else {
          alert("Failed to follow the author.");
        }
      };
      
    
    // Unfollow functionality
    const handleUnfollow = async (authorID) => {
        const token = localStorage.getItem("token");
      
        // Encode the unfollowed author's ID as required by the API
        const encodedAuthorId = encodeURIComponent(authorID);
      
        // API endpoint to remove the follower
        const url = `${apiUrl}authors/${authorID}/followers/${encodedAuthorId}`;
      
        // Send DELETE request to unfollow the author
        const response = await cusFetch(url, {
          method: "DELETE",
          headers: {
            token: `${token}`,
            "Content-Type": "application/json",
          },
        });
      
        if (response.ok) {
          alert(`You have unfollowed author ${authorID}`);
          setIsFollowing((prev) => ({ ...prev, [authorID]: false })); // Update state
        } else {
          alert("Failed to unfollow the author. Please try again.");
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
            {isFollowing[getAuthorId(author.id)] ? (
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
            )}
        </div>
        ))}
    </div>
    );
}

