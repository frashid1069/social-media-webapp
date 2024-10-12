import "./App.css";
import Login from "./components/Login";
import Footer from "./components/Footer";
import AuthorList from "./components/AuthorTest";
import EditPost from "./components/EditPost";     // not yet implemented in main app

function App() {
  return (
    <div className="App">
      <div className="login">
        <Login></Login>
      </div>
      {/* data test */}
      {/* <AuthorList />   */}
      <Footer></Footer>
    </div>

  );
}

export default App;
