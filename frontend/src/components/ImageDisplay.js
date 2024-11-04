import React, { useState, useEffect } from 'react';
const apiUrl = process.env.REACT_APP_API_URL
const ImageDisplay = () => {
    const [imageData, setImageData] = useState(null);

    useEffect(() => {
        fetch(`${apiUrl}image_post/1/`) 
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                console.log(data)
                setImageData(data.image_content);
            })
            .catch(error => {
                console.error('Error fetching image:', error);
            });
    }, []); 

    return (
        <div>
            <h1>Image Preview</h1>
            {imageData ? (
                <img src={imageData} alt="Fetched from server" style={{ maxWidth: '100%' }} />
            ) : (
                <p>Loading image...</p>
            )}
        </div>
    );
};

export default ImageDisplay;