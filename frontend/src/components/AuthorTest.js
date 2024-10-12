import React, { useEffect, useState } from 'react';

const AuthorList = () => {
  const [authors, setAuthors] = useState([]);   // State to hold author data
  const [loading, setLoading] = useState(true); // State to handle loading state
  const [error, setError] = useState(null);     // State to handle errors

  useEffect(() => {
    // Fetch data from Django backend API
    fetch('http://localhost:8000/service/author/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json(); // Parse JSON data
      })
      .then((data) => {
        setAuthors(data); // Store the fetched data in the state
        setLoading(false); // Set loading to false
      })
      .catch((err) => {
        setError(err.message); // Handle any errors
        setLoading(false); // Set loading to false
      });
  }, []); // Empty dependency array to run the effect only once

  // Show a loading message while data is being fetched
  if (loading) {
    return <p>Loading authors...</p>;
  }

  // Show an error message if something went wrong
  if (error) {
    return <p>Error: {error}</p>;
  }

  // If no authors are returned, display a message
  if (authors.length === 0) {
    return <p>No authors found.</p>;
  }

  // Render the list of authors once data is successfully fetched
  return (
    <div>
      <h1>Author List</h1>
      <ul>
        {authors.map((author) => (
          <li key={author.id}>
            {author.name} - {author.bio}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AuthorList;