// import React, { useState, useEffect } from "react";
// import { Link, useNavigate, useParams } from "react-router-dom";
// import "../streamStyle.css";

// export default function PostCards({ post }) {
//   const [authors, setAuthors] = useState([]);
//   useEffect(() => {
//     fetch("http://localhost:8000/service/author/")
//       .then((response) => response.json())
//       .then((data) => setAuthors(data));
//   }, []);
//   // find the corresponding author's name for the post
//   const matchAuthor = (authorId) => {
//     for (const author of authors) {
//       if (author.id === authorId) {
//         return author.display_name;
//       }
//     }
//   };
//   return (
//     <div key={post.id} className="post-card">
//       <h3 className="post-card-title">{post.title}</h3>
//       <h4 className="post-card-author">{matchAuthor(post.author)}</h4>
//       <p className="post-card-content">{post.content}</p>
//       <p className="post-card-update-date">{post.updated_at}</p>
//     </div>
//   );
// }

import React, { useState, useEffect } from "react";
import ReactMarkdown from 'react-markdown';  // Import react-markdown for rendering
import "../streamStyle_Sukh.css";

export default function PostCards() {
  const [posts, setPosts] = useState([]); // State to store posts
  const [authors, setAuthors] = useState([]); // State to store authors

  useEffect(() => {
    // // Fetch posts from json-server
    // fetch("http://localhost:8000/posts")
    //   .then((response) => response.json())
    //   .then((data) => setPosts(data));
    fetch("http://localhost:8000/posts")
      .then((response) => response.json())
      .then((data) => {
        // Filter posts to include only public ones
        const publicPosts = data.filter((post) => post.visibility === "public");
        setPosts(publicPosts);
      });

    // Fetch authors from json-server
    fetch("http://localhost:8000/authors")
      .then((response) => response.json())
      .then((data) => setAuthors(data));
  }, []);

  // Function to match post's author with the correct display name
  const matchAuthor = (authorId) => {
    const author = authors.find((author) => author.id === authorId);
    return author ? author.display_name : "Unknown Author";
  };

  return (
    <div>
      <h2>Posts</h2>
      {posts.length === 0 ? (
        <p>No posts available</p>
      ) : (
        posts.map((post) => (
          <div key={post.id} className="post-card">
            <h3 className="post-card-title">{post.title}</h3>
            <h4 className="post-card-author">{matchAuthor(post.author_id)}</h4>
            
            {/* Render the Markdown content using react-markdown */}
            <div className="post-card-content">
              <ReactMarkdown>{post.content}</ReactMarkdown>
            </div>
            
            <p className="post-card-update-date">Last updated: {post.updated_at}</p>
          </div>
        ))
      )}
    </div>
  );
}
