import "./App.css";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Login from "./components/Login";
import Footer from "./components/Footer";
import EditPost from "./components/EditPost";
import SignUp from "./components/SignUp";
import Stream from "./components/Stream";
import Profile from "./components/Profile";
import EditProfile from "./components/EditProfile";
import CreatePost from "./components/CreatePost";
import Likes from "./components/Likes";
import Welcome from "./components/Welcome";
import PostDetail from "./components/PostDetail";
import AuthorsPage from "./components/AuthorsPage";
import ChatAssistant from './components/ChatAssistant';
/**
 * You can put path for components
 *
 *
 */

function App() {
  return (
    <div className="App">
      <div className="login">
        <Router basename="/home">
          <Routes>
            <Route path="/" element={<Welcome />}></Route>
            <Route path="/login" element={<Login />}></Route>
            <Route path="/signup" element={<SignUp />}></Route>
            <Route path="/stream/:authorId" element={<Stream />}></Route>
            <Route
              path="/stream/:authorId/createPost"
              element={<CreatePost />}
            />
            <Route
              path="/stream/:authorId/editProfile"
              element={<EditProfile />}
            ></Route>

            <Route
              path="/stream/:authorId/profile"
              element={<Profile />}
            ></Route>
            <Route
              path="/stream/:authorId/authors"
              element={<AuthorsPage />}
            ></Route>
            <Route
              path="/posts/:postFqid/edit"
              element={<EditPost />}
            />
            <Route path="/posts/:postFqid" element={<PostDetail />} />

          </Routes>
        </Router>
      </div>
      <ChatAssistant />
      <Footer></Footer>
    </div>
  );
}

export default App;

// <Route path="/posts/:postId/edit" element={<EditPost />} />
// <Route path="/posts" element={<PostCards />} />
// <Route path="/posts/:postId" element={<PostDetail />} />
