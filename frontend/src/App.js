import "./App.css";
import Login from "./components/Login";
import Footer from "./components/Footer";
import AuthorList from "./components/AuthorTest";

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
