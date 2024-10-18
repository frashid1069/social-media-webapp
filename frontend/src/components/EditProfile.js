import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";
import PostCards from "./PostCards";



export default function EditProfile(){
    const [author, setAuthor] = useState([]);
    const [posts, setPosts] = useState([]);
    const { authorId } = useParams();

    // get the author info
    useEffect(() => {
        fetch(`http://localhost:8000/service/author/${authorId}`)
          .then((response) => response.json())
          .then((data) => setAuthor(data));
    }, [authorId]);

    // get the posts list
    useEffect(() => {
        fetch("http://localhost:8000/service/post/")
        .then((response) => response.json())
        .then((data) => setPosts(data));
    }, []);

    // get the author id as an int
    const authorIdInt = parseInt(authorId);

    // check if the post is from current user
    const matchesAuthor = (post, id) => {
        return post.author === id;
    };

    // Users can edit their profile and manage their posts
    return(
        
    )



}