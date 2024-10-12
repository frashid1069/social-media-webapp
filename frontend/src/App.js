import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Login from "./components/Login";
import Footer from "./components/Footer";
import EditPost from "./components/EditPost";


function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/posts/:postId/edit" element={<EditPost />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
