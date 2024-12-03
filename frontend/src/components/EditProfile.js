import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
const apiUrl = process.env.REACT_APP_API_URL

/*
  This component is used to edit the profile of the author. The author will be able to
  update their username, display name, password, bio, GitHub URL, and profile image.
*/
function EditProfile() {
  /*
    The formData state variable is used to store the data that the author will input. 
  */
  const [formData, setFormData] = useState({
    displayName: '',
    github: '',
    profileImage: null
  });

  const token = localStorage.getItem('token');  
  const currentAuthorId = localStorage.getItem("currentAuthorId")
  const encodedCurrentAuthorFqid = encodeURIComponent(currentAuthorId);

  // Gets the authorId from the URL
  const { authorId } = useParams();

  // leverge the useNavigate hook to navigate to a different URL
  const navigate = useNavigate();


  /*
    The useEffect hook is used to fetch the current profile data of the author. This will send a GET request to the API which
    will return the profile data of the author. The profile data will then be set to the formData state variable.
  */
  useEffect(() => {
    // Fetch the current profile data and set it to formData
    fetch(`${currentAuthorId}/`, {
      method: 'GET',
      headers: {
        "token": `${token}`,
        "Content-Type": "application/json"
      }
    })
    .then((response) => response.json())
    .then((data) => setFormData(data));
  }, [authorId]);


  


  /*
    The handleChange function is used to update the formData state variable whenever the author inputs data into the form fields. This 
    will help to keep the state variable updated with the latest data that the author inputs.
  */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };


  /*
    The handleFileChange function is used to update the formData state variable whenever the author uploads a profile image. The reason why its 
    different from the handleChange function is because the profile image is a file and not a string. Therefore, we need to handle it differently.
  */
  const handleFileChange = (e) => {
    setFormData({
      ...formData,
      profileImage: e.target.files[0],
    });
  };

  /*
    The handleSubmit function is used to send a PUT request to the API to update the profile of the author. The function will make sure that the
    author has inputted data into the form fields and then send the data to the API. If the profile is updated successfully, the author will be
    redirected to the profile page.
  */
    const handleSubmit = (e) => {
      e.preventDefault();
      const formDataToSend = new FormData();
      for (const key in formData) {
        if (formData[key] !== "" && formData[key] !== null) {
          formDataToSend.append(key, formData[key]);
        }
      }
    
      
     // print formData to console
      for (var pair of formDataToSend.entries()) {
        console.log(pair[0]+ ', ' + pair[1]); 
      }
      var object = {};
      formDataToSend.forEach(function(value, key){
        object[key] = value;
      });
      alert(JSON.stringify(object))
      
      fetch(`${currentAuthorId}/`, {
        method: 'PUT',
        headers: {
          "token": `${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(object)
      })
        .then(response => {if (response.ok) {
          navigate(`/stream/${encodedCurrentAuthorFqid}/profile`);
        }})
        // .then(data => {
        //   console.log('Profile updated successfully:', data);
        //   navigate(`/stream/${authorId}/profile`);
        // })
        .catch(error => console.error('Error updating profile:', error));
    };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Display Name:</label>
        <input 
          type="text" 
          name="displayName" 
          value={formData.displayName} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>GitHub URL:</label>
        <input 
          type="url" 
          name="github" 
          value={formData.github} 
          onChange={handleChange} 
        />
      </div>
      <div>
        <label>Profile Image:</label>
        <input 
          type="file" 
          name="profileImage" 
          onChange={handleFileChange} 
        />
      </div>
      <button type="submit">Update Profile</button>
    </form>
  );
}

export default EditProfile;
