import "./App.css";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Login from "./components/Login";
import Footer from "./components/Footer";
import EditPost from "./components/EditPost";
import SignUp from "./components/SignUp";
import Stream from "./components/Stream";

function App() {
  return (
    <div className="App">
      <div className="login">
        <Router basename="/">
          <Routes>
            <Route path="/login" element={<Login />}></Route>
            <Route path="/signup" element={<SignUp />}></Route>
            <Route path="/stream/:authorId" element={<Stream />}></Route>
            <Route
              path="/stream/:authorId/:postId/edit"
              element={<EditPost />}
            />
          </Routes>
        </Router>
      </div>
      <Footer></Footer>
    </div>
  );
}

export default App;
