// 1
// import React, { useState } from "react";
// import { useNavigate, useParams } from "react-router-dom";
// import "../loginStyles.css";
// /**
//  * This is a component for displaying create post page, will be redirected
//  * to stream page after submiting
//  *
//  ********* USABLE, BUT MISSING FUNCTIONALITY ABOUT SNEDING DROPDOWN VALUE AND IMAGE FILE *********
//  *
//  */
// export default function CreatePost() {
//   const [postContent, setPostContent] = useState("");
//   const [postContentType, setPostContentType] = useState("");
//   const [postTitle, setPostTitle] = useState("");
//   const [visibility, setVisibility] = useState("");
//   const { authorId } = useParams();
//   const authorIdInt = parseInt(authorId);
//   const navigate = useNavigate();
//   // handle submit the new post
//   const createPost = async (event) => {
//     event.preventDefault();
//     const response = await fetch(`http://localhost:8000/service/post/`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({
//         title: postTitle,
//         content: postContent,
//         content_type: "text/markdown",
//         created_at: new Date().toISOString(),
//         updated_at: new Date().toISOString(),
//         visibility: "public",
//         author: authorIdInt,
//       }),
//     })
//       .then((responsess) => responsess.json())
//       .then((data) => console.log(data));

//     navigate(`/stream/${authorId}`);
//   };
//   return (
//     <div className="create-post-page">
//       <h2 className="page-subtitle">Welcome to the create post page!</h2>
//       <form onSubmit={createPost}>
//         <div>
//           <input
//             className="new-post-title"
//             type="text"
//             placeholder="Title"
//             value={postTitle}
//             onChange={(e) => setPostTitle(e.target.value)}
//             required
//           />
//         </div>
//         <textarea
//           className="new-post-content"
//           placeholder="Write your post content here..."
//           value={postContent}
//           onChange={(e) => setPostContent(e.target.value)}
//           required
//         />
//         {/* <div className="new-post-content-type">
//           <label for="con_type">Content Type:</label>
//           <select
//             className="content-type-dropdown"
//             id="con_type"
//             value={postContentType}
//             onChange={(e) => setPostContentType(e.target.value)}
//           >
//             <option value="text/markdown">Markdown</option>
//             <option value="image">JPEG</option>
//           </select>
//         </div> */}
//         {/* <div className="new-post-visibility">
//           <label for="visi">Visibility:</label>
//           <select
//             className="visibility-dropdown"
//             id="visi"
//             value={visibility}
//             onChange={(e) => setVisibility(e.target.value)}
//           >
//             <option value="public">Public</option>
//             <option value="friend-only">Friend Only</option>
//             <option value="unlisted">Unlisted</option>
//           </select>
//         </div> */}
//         <button type="submit">Send</button>
//       </form>
//     </div>
//   );
// }

//2
// import React, { useState } from "react";
// import { useNavigate, useParams } from "react-router-dom";
// import "../loginStyles.css";

// export default function CreatePost() {
//   const [postContent, setPostContent] = useState("");
//   const [postContentType, setPostContentType] = useState("text/markdown");
//   const [postTitle, setPostTitle] = useState("");
//   const [visibility, setVisibility] = useState("public");
//   const [selectedImage, setSelectedImage] = useState(null);

//   const { authorId } = useParams();
//   const navigate = useNavigate();

//   const createPost = async (event) => {
//     event.preventDefault();

//     // Create FormData to include file (if any)
//     const formData = new FormData();
//     formData.append("title", postTitle);
//     formData.append("content", postContent);
//     formData.append("content_type", postContentType);
//     formData.append("visibility", visibility);
//     formData.append("author", parseInt(authorId));
//     formData.append("created_at", new Date().toISOString());
//     formData.append("updated_at", new Date().toISOString());

//     // Append the image file if the content type is set to "image/jpeg"
//     if (postContentType === "image/jpeg" && selectedImage) {
//       formData.append("image_content", selectedImage);
//     }

//     try {
//       const response = await fetch("http://localhost:8000/service/post/", {
//         method: "POST",
//         body: formData,
//       });

//       if (response.ok) {
//         navigate(`/stream/${authorId}`);
//       } else {
//         alert("Failed to create a post");
//       }
//     } catch (error) {
//       console.error("Error creating post:", error);
//       alert("Error creating post");
//     }
//   };

//   return (
//     <div className="create-post-page">
//       <h2 className="page-subtitle">Welcome to the create post page!</h2>
//       <form onSubmit={createPost}>
//         <div>
//           <input
//             className="new-post-title"
//             type="text"
//             placeholder="Title"
//             value={postTitle}
//             onChange={(e) => setPostTitle(e.target.value)}
//             required
//           />
//         </div>
//         {postContentType === "text/markdown" ? (
//           <textarea
//             className="new-post-content"
//             placeholder="Write your post content here..."
//             value={postContent}
//             onChange={(e) => setPostContent(e.target.value)}
//             required
//           />
//         ) : (
//           <div>
//             <input
//               type="file"
//               accept="image/jpeg"
//               onChange={(e) => setSelectedImage(e.target.files[0])}
//               required
//             />
//           </div>
//         )}
//         <div className="new-post-content-type">
//           <label htmlFor="con_type">Content Type:</label>
//           <select
//             className="content-type-dropdown"
//             id="con_type"
//             value={postContentType}
//             onChange={(e) => setPostContentType(e.target.value)}
//           >
//             <option value="text/markdown">Markdown</option>
//             <option value="image/jpeg">JPEG</option>
//           </select>
//         </div>
//         <div className="new-post-visibility">
//           <label htmlFor="visi">Visibility:</label>
//           <select
//             className="visibility-dropdown"
//             id="visi"
//             value={visibility}
//             onChange={(e) => setVisibility(e.target.value)}
//           >
//             <option value="public">Public</option>
//             <option value="friend-only">Friend Only</option>
//             <option value="unlisted">Unlisted</option>
//           </select>
//         </div>
//         <button type="submit">Send</button>
//       </form>
//     </div>
//   );
// }

//3
// import React, { useState } from "react";
// import { useNavigate, useParams } from "react-router-dom";
// import { marked } from "marked"; // Import the Markdown library
// import "../loginStyles.css";

// export default function CreatePost() {
//   const [postContent, setPostContent] = useState("");
//   const [postContentType, setPostContentType] = useState("text/markdown");
//   const [postTitle, setPostTitle] = useState("");
//   const [visibility, setVisibility] = useState("public");
//   const [selectedImage, setSelectedImage] = useState(null);

//   const { authorId } = useParams();
//   const navigate = useNavigate();

//   const createPost = async (event) => {
//     event.preventDefault();

//     // Create FormData to include file (if any)
//     const formData = new FormData();
//     formData.append("title", postTitle);
//     formData.append("content", postContent);
//     formData.append("content_type", postContentType);
//     formData.append("visibility", visibility);
//     formData.append("author", parseInt(authorId));
//     formData.append("created_at", new Date().toISOString());
//     formData.append("updated_at", new Date().toISOString());

//     // Append the image file if the content type is set to "image/jpeg"
//     if (postContentType === "image/jpeg" && selectedImage) {
//       formData.append("image_content", selectedImage);
//     }

//     try {
//       const response = await fetch("http://localhost:8000/service/post/", {
//         method: "POST",
//         body: formData,
//       });

//       if (response.ok) {
//         navigate(`/stream/${authorId}`);
//       } else {
//         alert("Failed to create a post");
//       }
//     } catch (error) {
//       console.error("Error creating post:", error);
//       alert("Error creating post");
//     }
//   };

//   // Convert the Markdown content to HTML using "marked"
//   const getMarkdownPreview = () => {
//     return { __html: marked(postContent) };
//   };

//   return (
//     <div className="create-post-page">
//       <h2 className="page-subtitle">Create a New Post</h2>
//       <form onSubmit={createPost}>
//         <div>
//           <input
//             className="new-post-title"
//             type="text"
//             placeholder="Title"
//             value={postTitle}
//             onChange={(e) => setPostTitle(e.target.value)}
//             required
//           />
//         </div>
//         {postContentType === "text/markdown" ? (
//           <>
//             <textarea
//               className="new-post-content"
//               placeholder="Write your post content in Markdown..."
//               value={postContent}
//               onChange={(e) => setPostContent(e.target.value)}
//               required
//             />
//             {/* Markdown Preview */}
//             <div className="markdown-preview">
//               <h3>Preview</h3>
//               <div
//                 dangerouslySetInnerHTML={getMarkdownPreview()} // Render the Markdown content as HTML
//               ></div>
//             </div>
//           </>
//         ) : (
//           <div>
//             <input
//               type="file"
//               accept="image/jpeg"
//               onChange={(e) => setSelectedImage(e.target.files[0])}
//               required
//             />
//           </div>
//         )}
//         <div className="new-post-content-type">
//           <label htmlFor="con_type">Content Type:</label>
//           <select
//             className="content-type-dropdown"
//             id="con_type"
//             value={postContentType}
//             onChange={(e) => setPostContentType(e.target.value)}
//           >
//             <option value="text/markdown">Markdown</option>
//             <option value="image/jpeg">JPEG</option>
//           </select>
//         </div>
//         <div className="new-post-visibility">
//           <label htmlFor="visi">Visibility:</label>
//           <select
//             className="visibility-dropdown"
//             id="visi"
//             value={visibility}
//             onChange={(e) => setVisibility(e.target.value)}
//           >
//             <option value="public">Public</option>
//             <option value="friend-only">Friend Only</option>
//             <option value="unlisted">Unlisted</option>
//           </select>
//         </div>
//         <button type="submit">Send</button>
//       </form>
//     </div>
//   );
// }
import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marked } from "marked"; // Import the Markdown library
import "../loginStyles.css";

export default function CreatePost() {
  const [postContent, setPostContent] = useState(""); // For Markdown content
  const [postTitle, setPostTitle] = useState("");
  const [visibility, setVisibility] = useState("public");
  const [selectedImage, setSelectedImage] = useState(null); // To handle image uploads

  const { authorId } = useParams();
  const navigate = useNavigate();

  const createPost = async (event) => {
    event.preventDefault();

    // Create FormData to include file (if any)
    const formData = new FormData();
    formData.append("title", postTitle);
    formData.append("content", postContent); // Markdown content
    formData.append("content_type", "text/markdown"); // Setting default type to Markdown
    formData.append("visibility", visibility);
    formData.append("author", parseInt(authorId));
    formData.append("created_at", new Date().toISOString());
    formData.append("updated_at", new Date().toISOString());

    // Append the image file if an image is selected
    if (selectedImage) {
      formData.append("image_content", selectedImage);
    }

    try {
      const response = await fetch("http://localhost:8000/service/post/", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        navigate(`/stream/${authorId}`);
      } else {
        alert("Failed to create a post");
      }
    } catch (error) {
      console.error("Error creating post:", error);
      alert("Error creating post");
    }
  };

  // Handle cancel action
  const cancelPostCreation = () => {
    navigate(`/stream/${authorId}`);
  };

  // Convert the Markdown content to HTML using "marked"
  const getMarkdownPreview = () => {
    return { __html: marked(postContent) };
  };

  return (
    <div className="create-post-page">
      <h2 className="page-subtitle">Create a New Post</h2>
      <form onSubmit={createPost}>
        <div>
          <input
            className="new-post-title"
            type="text"
            placeholder="Title"
            value={postTitle}
            onChange={(e) => setPostTitle(e.target.value)}
            required
          />
        </div>
        <textarea
          className="new-post-content"
          placeholder="Write your post content in Markdown..."
          value={postContent}
          onChange={(e) => setPostContent(e.target.value)}
          required
        />
        {/* Markdown Preview */}
        <div className="markdown-preview">
          <h3>Preview</h3>
          <div
            dangerouslySetInnerHTML={getMarkdownPreview()} // Render the Markdown content as HTML
          ></div>
        </div>
        <div>
          <label htmlFor="image-upload">Upload an image (optional):</label>
          <input
            id="image-upload"
            type="file"
            accept="image/jpeg"
            onChange={(e) => setSelectedImage(e.target.files[0])}
          />
        </div>
        <div className="new-post-visibility">
          <label htmlFor="visi">Visibility:</label>
          <select
            className="visibility-dropdown"
            id="visi"
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
          >
            <option value="public">Public</option>
            <option value="friend-only">Friend Only</option>
            <option value="unlisted">Unlisted</option>
          </select>
        </div>
        <div className="button-container">
          <button type="submit">Send</button>
          {/* Cancel button */}
          <button type="button" onClick={cancelPostCreation} className="cancel-btn">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
