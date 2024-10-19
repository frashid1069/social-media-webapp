import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../streamStyle.css";



function EditProfile() {
  const [formData, setFormData] = useState({
    username: '',
    display_name: '',
    password: '',
    bio: '',
    github_url: '',
    profile_image: null,
  });

  const { authorId } = useParams();

  const navigate = useNavigate();

  useEffect(() => {
    // Fetch the current profile data and set it to formData
    fetch(`http://localhost:8000/service/author/${authorId}/`)
      .then(response => response.json())
      .then(data => setFormData(data))
      .catch(error => console.error('Error fetching profile data:', error));
  }, [authorId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleFileChange = (e) => {
    setFormData({
      ...formData,
      profile_image: e.target.files[0],
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const formDataToSend = new FormData();
    for (const key in formData) {
      if (formData[key] !== "" && formData[key] !== null) {
        formDataToSend.append(key, formData[key]);
      }
    }
  
    
    formDataToSend.append('updated_at', new Date().toISOString());
  
    fetch(`http://localhost:8000/service/author/${authorId}/`, {
      method: 'PUT',
      body: formDataToSend,
    })
      .then(response => response.json())
      .then(data => {
        console.log('Profile updated successfully:', data);
        navigate(`/stream/${authorId}/profile`);
      })
      .catch(error => console.error('Error updating profile:', error));
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Username:</label>
        <input 
          type="text" 
          name="username" 
          value={formData.username} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Display Name:</label>
        <input 
          type="text" 
          name="display_name" 
          value={formData.display_name} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Password:</label>
        <input 
          type="password" 
          name="password" 
          value={formData.password} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Bio:</label>
        <textarea 
          name="bio" 
          value={formData.bio} 
          onChange={handleChange}
        ></textarea>
      </div>
      <div>
        <label>GitHub URL:</label>
        <input 
          type="url" 
          name="github_url" 
          value={formData.github_url} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Profile Image:</label>
        <input 
          type="file" 
          name="profile_image" 
          onChange={handleFileChange} 
        />
      </div>
      <button type="submit">Update Profile</button>
    </form>
  );
}

export default EditProfile;